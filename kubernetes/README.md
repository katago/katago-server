# Installation

On https://katagotraining.org we run the server on kubernetes.
The cloud provider is GCP.

We run it on:

- a modern GKE cluster, with Istio plugin activated
- cloudSQl postgres DB
- memstore redis 

## Expected machine for the run

TODO: describe what kind of instance we used for GKE, cloudSQL, and memestore

## Istio specific config


We want istio to be run behind Ingress, to use NativeIngress and cloud armor

We thus need top patch it:

```bash
cat <<EOF > istio-ingress-patch.json
[
  {
    "op": "add",
    "path": "/metadata/annotations/cloud.google.com~1neg",
    "value": "{"exposed_ports": {"80":{}}, \"ingress\": true}" 
  },
  {
    "op": "replace",
    "path": "/spec/type",
    "value": "NodePort"
  },
  {
    "op": "remove",
    "path": "/status"
  },
  {    
    "op": "add",
    "path": "/metadata/annotations/cloud.google.com~1backend-config",
    "value": "{"ports": {"80":"katago-server-backend-config"}}"
  }
]
EOF

kubectl -n gke-system patch svc istio-ingress \
    --type=json -p="$(cat istio-ingress-patch.json)" \
    --dry-run=true -o yaml | kubectl apply -f -

```