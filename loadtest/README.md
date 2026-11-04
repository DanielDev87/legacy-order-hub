# Canary y pruebas de carga (HU-09)

1. Despliegue estable: `kubectl apply -k k8s/`
2. Active el Ingress: `minikube addons enable ingress`; añada `orderhub.local` al archivo hosts.
3. Despliegue canary (10 %): `kubectl apply -f k8s/canary/`
4. Genere carga: `LOAD_PASSWORD=... locust -f loadtest/locustfile.py --host http://orderhub.local --headless -u 50 -r 10 -t 2m`
5. Evalúe y revierta si el error > 1 %: `./loadtest/canary_check.sh`

Para que Prometheus distinga `version="canary"`, el scrape debe copiar la etiqueta `version` del pod
(relabel de `__meta_kubernetes_pod_label_version`).
