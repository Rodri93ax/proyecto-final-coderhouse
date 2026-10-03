# Preparación de AWS y GitHub para reproducir el laboratorio

Esta guía acompaña el README. Los módulos del repositorio crean red, instancia, clave pública, Security Group y rol/perfil IAM de EC2. **El bucket del backend y el rol federado de GitHub se preparan antes**, con una identidad administradora del laboratorio. Los ejemplos IAM adjuntos son plantillas documentales reconstruidas a partir de la configuración utilizada; no son un export completo de la cuenta ni fueron aplicados por la generación del informe.

## 1. Valores que deben adaptarse

| Valor original | Dónde cambiarlo en una réplica |
|---|---|
| Cuenta `277385996330` | ARN OIDC de workflows y políticas IAM |
| Región `us-east-1` | Provider, backend, workflows, políticas y AMI |
| Proyecto `coderhouse` | Variables, nombres IAM y permisos asociados |
| Bucket `coderhouse-tfstate-277385996330-us-east-1` | `infra/backend.tf`, `aws-identity.yml` y política S3 |
| Repo `Rodri93ax/proyecto-final-coderhouse` | Trust OIDC, GHCR, imagen K8s y regex del deploy |
| Instancia `i-0125cbf96588912aa` | `ci.yml: INSTANCE_ID` y Resource del permiso SSM |
| IPv4 del operador `/32` | `ADMIN_CIDR` en GitHub y tfvars local |
| Clave pública | `infra/keys/coderhouse-aws.pub` para CI; tfvars para ejecución local |

La IP `100.54.24.213` fue observada el 03/10/2026. No se considera un endpoint fijo.

## 2. Backend S3 (una vez por entorno)

Con AWS CLI configurada en una cuenta autorizada, escoger un nombre globalmente único. Los comandos siguientes son para **us-east-1**:

```bash
export AWS_DEFAULT_REGION=us-east-1
aws sts get-caller-identity
export TF_STATE_BUCKET="mi-bucket-unico-de-estado"
aws s3api create-bucket --bucket "$TF_STATE_BUCKET" --region us-east-1
aws s3api put-public-access-block --bucket "$TF_STATE_BUCKET" \
  --public-access-block-configuration \
  'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'
aws s3api put-bucket-versioning --bucket "$TF_STATE_BUCKET" \
  --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket "$TF_STATE_BUCKET" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

Si el bucket ya existe y es el correcto, no ejecutar create-bucket. Actualizar `infra/backend.tf` con su nombre, manteniendo `encrypt = true` y `use_lockfile = true`. La clave es `coderhouse/terraform.tfstate`, con lock `coderhouse/terraform.tfstate.tflock`. No se usa tabla DynamoDB.

Para un entorno nuevo ejecutar `terraform -chdir=infra init -lockfile=readonly`. Para migrar un **estado local existente** usar `terraform -chdir=infra init -migrate-state` después de respaldarlo y revisar el destino; no iniciar un estado vacío para recursos que ya existen.

## 3. Federación OIDC de GitHub

En IAM > Identity providers, crear (o reutilizar) el proveedor OpenID Connect:

- URL: `https://token.actions.githubusercontent.com`.
- Audience: `sts.amazonaws.com`.

Crear el rol `github-coderhouse-deploy` con la trust policy de `docs/iam/github-trust.json`, adaptando cuenta y subject. Para el repositorio original se utilizó:

```text
repo:Rodri93ax@69176514/proyecto-final-coderhouse@1389816159:ref:refs/heads/main
```

No copiar ese subject para un fork. El formato depende de la configuración OIDC del repositorio y puede incluir IDs inmutables. Obtener los IDs del repositorio propio con la API de GitHub o `gh api repos/OWNER/REPO --jq '{owner_id: .owner.id, repo_id: .id}'` y verificar el formato OIDC que usa. La confianza debe restringirse a ese repositorio y `main`, con audiencia exacta, sin comodín global.

Las políticas adjuntas a esta documentación separan:

1. `terraform-state.json`: ListBucket, lectura/escritura del estado y lectura/escritura/borrado del lock.
2. `terraform-provision.json`: acciones EC2 en us-east-1 y operaciones IAM limitadas al rol/perfil de EC2; asociación únicamente de AmazonSSMManagedInstanceCore y PassRole para EC2.
3. `ssm-deploy.json`: comprobación de la instancia, envío de AWS-RunShellScript a la instancia elegida y lectura del resultado.

En IAM > rol > Add permissions > Create inline policy, usar cada JSON adaptado. Revisar la política antes de guardarla. No hace falta cargar estas plantillas en el entorno original si ya tiene los permisos funcionando. Su uso en otra cuenta puede estar condicionado por SCP, permission boundaries u otras restricciones.

En GitHub > Settings > Secrets and variables > Actions > Variables, crear `ADMIN_CIDR`. Habilitar Actions y permisos de publicación de packages según la configuración de la organización. El job publish solicita `packages: write` y usa el `GITHUB_TOKEN` generado por GitHub. Los jobs de AWS solicitan `id-token: write`.

Cambiar `role-to-assume` en los cuatro workflows por el ARN del rol propio. Cambiar bucket/key en el workflow de identidad. Este último usa `head-object`: requiere que ya exista un estado; en un entorno totalmente nuevo ejecutarlo después del primer apply.

## 4. Primera provisión y conexión

1. Adaptar Terraform, backend y clave pública según el README.
2. Para un entorno nuevo sin recursos IAM preexistentes, renombrar `infra/imports.tf` a `infra/imports.tf.example`.
3. Ejecutar Terraform plan y apply con la identidad local autorizada o con el workflow de apply tras preparar OIDC. Los permisos SSM de la plantilla todavía pueden apuntar al ID antiguo; no son necesarios para crear la EC2.
4. Obtener el nuevo `instance_id`; actualizar `INSTANCE_ID` y el ARN de la política SSM.
5. Esperar cloud-init y K3s. Con SSH, usuario Ubuntu y clave privada propia:

```bash
ssh -i ~/.ssh/coderhouse-aws ubuntu@IP_PUBLICA_ACTUAL
sudo cloud-init status --wait
sudo systemctl is-active k3s
sudo k3s kubectl get nodes
```

No ejecutar cambios en bootstrap sobre la instancia existente sin revisar Terraform: `user_data_replace_on_change` está activado.

## 5. SSM y administración desde navegador

Terraform crea el rol y perfil `coderhouse-ec2-ssm`, con confianza de `ec2.amazonaws.com` y política `AmazonSSMManagedInstanceCore`, y los asocia a la instancia. El agente SSM debe estar instalado, activo y tener salida HTTPS. El bootstrap de este repositorio **no instala explícitamente SSM Agent**; verificarlo en la AMI seleccionada.

En Ubuntu, si el agente utiliza Snap:

```bash
sudo snap list amazon-ssm-agent
sudo systemctl status snap.amazon-ssm-agent.amazon-ssm-agent.service
```

Solo si no está instalado, y tras comprobar que no existe otra instalación por paquete deb:

```bash
sudo snap install amazon-ssm-agent --classic
sudo snap start amazon-ssm-agent
```

Si existe y necesita reinicio:

```bash
sudo snap restart amazon-ssm-agent
```

Desde la computadora administradora:

```bash
aws ssm describe-instance-information \
  --filters Key=InstanceIds,Values=ID_DE_LA_INSTANCIA \
  --query 'InstanceInformationList[0].PingStatus' --output text
```

Debe mostrar `Online`. Para abrir una shell, AWS Console > EC2 > Conectar > Session Manager. La identidad humana requiere permisos de Session Manager propios; la política de deploy de GitHub solo cubre Run Command, no autoriza sesiones interactivas.

Para acceder a Grafana mediante SSM en vez de SSH: instalar AWS CLI y Session Manager Plugin en la computadora, iniciar previamente el port-forward de Kubernetes a `127.0.0.1:3000` en EC2 y ejecutar localmente:

```bash
aws ssm start-session --target ID_DE_LA_INSTANCIA \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["3000"],"localPortNumber":["3000"]}'
```

Abrir `http://localhost:3000`. Esta operación necesita permisos `ssm:StartSession` sobre la instancia y el documento, además de los permisos de gestión de sesión de la identidad humana. No ampliar el rol del pipeline para conceder acceso interactivo innecesario.

## 6. Primera publicación y despliegue

El workflow `ci.yml` se dispara con push a main, pull request o manualmente. En main, todos los controles deben terminar correctamente antes de publicar; el deploy espera a publish. La imagen GHCR debe permitir lectura desde el nodo sin credenciales, o requiere una configuración adicional de registry privado.

En una réplica, cambiar **todas** las referencias a la ruta original de la imagen: env IMAGE de publish/deploy, `k8s/app.yaml` y el patrón `re.subn` del deploy. Si ese patrón no coincide exactamente una vez, el job falla de forma explícita. Al terminar, verificar rollout, pods, HPA y /health con los comandos del README.

Para una prueba nueva completa: preparar los prerrequisitos, provisionar, instalar monitoreo, publicar/desplegar y revisar métricas. Esta secuencia está documentada a partir de los componentes y ejecuciones del laboratorio; no se realizó una segunda reconstrucción íntegra desde cero durante la preparación del informe.

## 7. Referencias oficiales

- [Backend S3 de Terraform](https://developer.hashicorp.com/terraform/language/backend/s3).
- [Importación de recursos de Terraform](https://developer.hashicorp.com/terraform/language/import).
- [OIDC de GitHub con AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).
- [SSM Agent en Ubuntu con Snap](https://docs.aws.amazon.com/systems-manager/latest/userguide/agent-install-ubuntu-64-snap.html).
- [Session Manager y port forwarding](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html).
- [Instalación de Helm](https://helm.sh/docs/intro/install/).

Las versiones concretas citadas en el proyecto corresponden al código y a las evidencias del ZIP entregado; no representan una recomendación de actualizar componentes antes de la entrega.
