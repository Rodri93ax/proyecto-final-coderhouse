# Revisión del análisis DAST

Imagen desplegada: ghcr.io/rodri93ax/proyecto-final-coderhouse:633d1a6add6430b6a72fa0388f6a3c3e4d856e61

Herramienta: OWASP ZAP Baseline.
Alcance observado: /, /robots.txt y /sitemap.xml.
Análisis pasivo; no constituye una auditoría completa de seguridad.

Resultado inicial: 62 PASS, 5 WARN, 0 FAIL.
Resultado posterior: 66 PASS, 1 WARN, 0 FAIL.
Código de salida posterior: 2.

Se corrigieron las cabeceras X-Content-Type-Options,
Content-Security-Policy, Permissions-Policy y
Cross-Origin-Resource-Policy.

La alerta de caché cambió de Storable and Cacheable Content a
Non-Storable Content (10049-1), de riesgo informativo.
Se mantiene Cache-Control: no-store por decisión de diseño.
La alerta queda registrada, sin ocultarla ni desactivar la regla.

Referencia: https://www.zaproxy.org/docs/alerts/10049-1/

Pendiente: ampliar la cobertura DAST a /health y /metrics e integrar
su ejecución y evaluación en el pipeline.
