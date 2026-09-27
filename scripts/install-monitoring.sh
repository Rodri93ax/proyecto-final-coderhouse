#!/usr/bin/env bash
set -euo pipefail

VALUES_FILE="${1:?Indicar archivo values.yaml}"
MONITOR_FILE="${2:?Indicar archivo PodMonitor}"

sudo k3s kubectl create namespace monitoring \
  --dry-run=client -o yaml | sudo k3s kubectl apply -f -

if ! sudo k3s kubectl get secret grafana-admin \
  -n monitoring >/dev/null 2>&1; then
  python3 - <<'PY' | sudo k3s kubectl create -f -
import json
import secrets

print(json.dumps({
    "apiVersion": "v1",
    "kind": "Secret",
    "metadata": {
        "name": "grafana-admin",
        "namespace": "monitoring"
    },
    "type": "Opaque",
    "stringData": {
        "admin-user": "admin",
        "admin-password": secrets.token_urlsafe(24)
    }
}))
PY
fi

sudo helm upgrade --install monitoring kube-prometheus-stack \
  --repo https://prometheus-community.github.io/helm-charts \
  --version 91.4.0 \
  --namespace monitoring \
  --kubeconfig /etc/rancher/k3s/k3s.yaml \
  --values "$VALUES_FILE" \
  --wait --timeout 10m

sudo k3s kubectl apply -f "$MONITOR_FILE"

sudo k3s kubectl get pods,pvc,svc -n monitoring
