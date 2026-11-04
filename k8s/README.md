# Despliegue en Kubernetes (HU-07)

Requisitos: Minikube/k3s con `metrics-server` (`minikube addons enable metrics-server`).

```bash
docker build -t legacy-order-hub:latest .
minikube image load legacy-order-hub:latest
# Edite secret.yaml (o cree el Secret con kubectl, ver comentario) y luego:
kubectl apply -k k8s/
kubectl -n orderhub get pods,hpa
minikube service orderhub -n orderhub --url
```

- `Deployment`: 2 réplicas, no root, probes liveness/readiness en `/healthcheck`.
- `HPA`: 2–5 réplicas al superar 70 % de CPU.
- `Service`: NodePort 30080 → puerto 8000.
- PostgreSQL corre como `StatefulSet` con volumen persistente.
