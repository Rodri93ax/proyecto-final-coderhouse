import json
from pathlib import Path

datasource = {"type": "prometheus", "uid": "${datasource}"}

def panel(number, title, expression, unit, x, y, kind="timeseries",
          legend="{{pod}}", description=""):
    result = {
        "id": number,
        "title": title,
        "description": description,
        "type": kind,
        "datasource": datasource,
        "gridPos": {
            "x": x, "y": y, "w": 12,
            "h": 5 if kind == "stat" else 8
        },
        "targets": [{
            "refId": "A",
            "expr": expression,
            "legendFormat": legend,
            "datasource": datasource,
            "instant": kind == "stat",
            "range": kind != "stat"
        }],
        "fieldConfig": {
            "defaults": {"unit": unit, "min": 0},
            "overrides": []
        }
    }
    if kind == "stat":
        result["options"] = {
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": False
            },
            "colorMode": "value",
            "graphMode": "none"
        }
    else:
        result["options"] = {
            "legend": {"displayMode": "list", "placement": "bottom"},
            "tooltip": {"mode": "multi"}
        }
    return result

dashboard = {
    "uid": "coderhouse-api",
    "title": "Coderhouse - API en AWS",
    "description": "API Flask en K3s. Trafico HTTP separado de las sondas de salud.",
    "tags": ["coderhouse", "aws", "k3s"],
    "schemaVersion": 39,
    "version": 1,
    "editable": False,
    "timezone": "browser",
    "refresh": "10s",
    "time": {"from": "now-15m", "to": "now"},
    "templating": {
        "list": [{
            "name": "datasource",
            "label": "Fuente de datos",
            "type": "datasource",
            "query": "prometheus",
            "refresh": 1,
            "options": []
        }]
    },
    "panels": [
        panel(
            1, "Replicas con recoleccion de metricas OK",
            'sum(up{namespace="coderhouse",job="monitoring/coderhouse-api"})',
            "none", 0, 0, "stat",
            description="Cantidad de replicas cuyo /metrics responde a Prometheus."
        ),
        panel(
            2, "Solicitudes en el periodo (sin health)",
            'sum(increase(app_requests_total{namespace="coderhouse",'
            'exported_endpoint!="health"}[$__range]))',
            "short", 12, 0, "stat",
            description="Estimacion de increase(); excluye las sondas /health."
        ),
        panel(
            3, "Solicitudes por segundo y ruta (sin health)",
            'sum by (exported_endpoint) (rate(app_requests_total{'
            'namespace="coderhouse",exported_endpoint!="health"}'
            '[$__rate_interval]))',
            "reqps", 0, 5, legend="{{exported_endpoint}}"
        ),
        panel(
            4, "Respuestas por segundo y codigo HTTP (sin health)",
            'sum by (status) (rate(app_requests_total{'
            'namespace="coderhouse",exported_endpoint!="health"}'
            '[$__rate_interval]))',
            "reqps", 12, 5, legend="HTTP {{status}}"
        ),
        panel(
            5, "CPU del proceso Python (% de un nucleo)",
            '100 * rate(process_cpu_seconds_total{namespace="coderhouse"}'
            '[$__rate_interval])',
            "percent", 0, 13
        ),
        panel(
            6, "Memoria residente del proceso Python",
            'process_resident_memory_bytes{namespace="coderhouse"}',
            "bytes", 12, 13
        )
    ]
}

content = json.dumps(dashboard, indent=2, ensure_ascii=False)
Path("monitoring/dashboard.json").write_text(content + "\n")

configmap = {
    "apiVersion": "v1",
    "kind": "ConfigMap",
    "metadata": {
        "name": "coderhouse-dashboard",
        "namespace": "monitoring",
        "labels": {"grafana_dashboard": "1"}
    },
    "data": {"coderhouse-api.json": content}
}

Path("monitoring/dashboard-configmap.json").write_text(
    json.dumps(configmap, indent=2, ensure_ascii=False) + "\n"
)
print("Dashboard y ConfigMap generados.")
