#!/bin/bash
# Script conataining kubectl commands to deploy the application
set -e

echo ">>> Applying RBAC..."
kubectl apply -f rbac.yaml

echo ">>> Applying secrets..."
kubectl apply -f user-service/k8s/secret.yaml
kubectl apply -f order-service/k8s/secret.yaml

echo ">>> Applying MySQL (PVC + Deployment + Service)..."
kubectl apply -f user-service/k8s/mysql.yaml
kubectl apply -f order-service/k8s/mysql.yaml

echo ">>> Waiting for MySQL pods to be ready..."
kubectl wait --for=condition=ready pod -l app=mysql-user --timeout=120s
kubectl wait --for=condition=ready pod -l app=mysql-order --timeout=120s

echo ">>> Applying Flask deployments..."
kubectl apply -f user-service/k8s/deployment.yaml
kubectl apply -f order-service/k8s/deployment.yaml

echo ">>> Applying Flask services..."
kubectl apply -f user-service/k8s/service.yaml
kubectl apply -f order-service/k8s/service.yaml

echo ">>> Applying frontend..."
kubectl apply -f frontend/k8s/deployment.yaml
kubectl apply -f frontend/k8s/service.yaml

echo ">>> Applying ingress..."
kubectl apply -f ingress.yaml

echo ""
echo ">>> All done! Current pod status:"
kubectl get pods

echo ""
echo ">>> Services:"
kubectl get services

echo ""
echo ">>> Ingress:"
kubectl get ingress
