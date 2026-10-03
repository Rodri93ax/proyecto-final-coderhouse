# Índice de evidencias del proyecto final

Las rutas son relativas a `docs/evidencias/`. Los logs originales se conservan en el repositorio. Las capturas incorporadas proceden de las imágenes aportadas por el autor; no son recreaciones. Los resultados corresponden a sus respectivas ejecuciones históricas, no a una comprobación continua del servicio.

| Requisito | Evidencia | Qué demuestra |
|---|---|---|
| Tests de aplicación y cabeceras | [tests-security.txt](tests-security.txt) | Cinco tests OK |
| Imagen publicada ejecutada localmente | [ghcr-local.txt](ghcr-local.txt) | Contenedor running/healthy, /health OK |
| Aprovisionamiento | [terraform-apply.txt](terraform-apply.txt) | Creación inicial de ocho recursos |
| Corrección de red | [terraform-fix-network.txt](terraform-fix-network.txt) | Reemplazo histórico de la EC2 inicial |
| Backend remoto | [terraform-s3-plan.txt](terraform-s3-plan.txt) | Plan sobre infraestructura existente tras migración |
| OIDC | [aws-oidc-success.txt](aws-oidc-success.txt) | Workflow de identidad aprobado |
| IAM incorporado a Terraform | [terraform-github-import.txt](terraform-github-import.txt) | 3 importados, 2 cambios, 0 destruidos |
| Estado final Terraform | [terraform-plan-final.txt](terraform-plan-final.txt) | Sin diferencias; transcripción aportada el 03/10 |
| Kubernetes | [k8s-deploy.txt](k8s-deploy.txt) y [k8s-metricas.txt](k8s-metricas.txt) | Deployment, servicio, ingreso, HPA y métricas |
| Despliegue automatizado | [deploy-github-ssm.txt](deploy-github-ssm.txt) | SSM Success, rollout correcto y salud OK |
| CI/CD completo | [ci-cd-success.png](capturas/ci-cd-success.png) | Seis jobs aprobados, SHA 5b4bec7, duración 3m36s |
| DAST inicial | [reporte.html](zap-inicial/reporte.html) / [JSON](zap-inicial/reporte.json) | Hallazgos antes de remediar |
| DAST posterior | [análisis](zap-final/analisis.md), [HTML](zap-final/reporte.html), [JSON](zap-final/reporte.json) | Solo excepción informativa de caché |
| Controles CI antes de publicar | [ci-dast-success.txt](ci-dast-success.txt) | Tests, build, SAST, DAST y publicación aprobados |
| Cabeceras desplegadas | [deploy-security.txt](deploy-security.txt) | HTTP 200 y cabeceras de la versión corregida |
| Monitoreo | [monitoring-install.txt](monitoring-install.txt) | Stack desplegado y PVC Bound |
| Dashboard | [grafana-api.png](capturas/grafana-api.png) | Dos targets, tráfico, CPU y memoria |
| Carga | [hpa-carga.txt](hpa-carga.txt) | 81.443 respuestas OK, cero errores |
| Autoescalado | [hpa-prueba.txt](hpa-prueba.txt) / [hpa-final.txt](hpa-final.txt) | Ascenso a 4 y retorno a 2 réplicas |
| Dashboard durante carga | [grafana-hpa-carga.png](capturas/grafana-hpa-carga.png) | Cuatro targets y aumento de actividad |
| Revisión de entrega | [revision-documental.txt](revision-documental.txt) | Checks locales complementarios y límites de validación |

## Enlaces de ejecuciones conservados en los logs

- [CI con SAST/DAST aprobado: 36353724830](https://github.com/Rodri93ax/proyecto-final-coderhouse/actions/runs/36353724830).
- [Verificación OIDC: 36355746346](https://github.com/Rodri93ax/proyecto-final-coderhouse/actions/runs/36355746346).
- El despliegue SSM identifica el comando `f2afe7fe-ad1f-4dea-a1d5-43ef08cc1950` y la imagen `5b4bec77111ad68919fe0f8e7f20a01e1b6b9dab`. No se inventa un run ID que no figure en esa evidencia.

El archivo `terraform-github-plan.txt` original documenta una IP anterior, no el último plan sin diferencias. Las capturas de Grafana pertenecen al 27/09/2026 y la del CI/CD al 02/10/2026, según los archivos aportados. La lectura 96.1 del dashboard es una estimación Prometheus del intervalo, no el total exacto del generador.
