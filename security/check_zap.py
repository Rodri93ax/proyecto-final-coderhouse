import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text())
sites = report.get("site")
if not isinstance(sites, list) or not sites:
    raise SystemExit("ERROR: informe ZAP sin sitios analizados.")

blocked = []
for site in sites:
    for alert in site.get("alerts", []):
        accepted = (
            str(alert.get("alertRef")) == "10049-1"
            and str(alert.get("riskcode")) == "0"
        )
        name = alert.get("name") or alert.get("alert")
        if accepted:
            print(f"ACEPTADA: {name}; no-store intencional.")
        else:
            blocked.append(alert)
            print(f"BLOQUEANTE: {name} [{alert.get('alertRef')}]")

if blocked:
    raise SystemExit(1)

print("DAST aprobado: sin alertas fuera de la excepción documentada.")
