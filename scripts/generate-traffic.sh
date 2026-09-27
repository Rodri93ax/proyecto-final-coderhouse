#!/usr/bin/env bash
set -euo pipefail
APP_URL="${1:?Indicar URL de la API}"

date -Iseconds
for ((i=1; i<=100; i++)); do
  curl -fsS --connect-timeout 5 --max-time 10 \
    "${APP_URL%/}/" >/dev/null
  sleep 0.2
done
echo "Completadas 100 solicitudes a la API sin errores HTTP."
date -Iseconds
