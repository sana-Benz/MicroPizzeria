# 🍕 KubePizza – Microservices Pizza Ordering App

## 📌 Description
KubePizza est une application de commande de pizzas basée sur une architecture **microservices**.

L’utilisateur peut :
- consulter le menu des pizzas
- passer une commande
- suivre le statut de sa commande

Ce projet a pour objectif de mettre en œuvre :
- des microservices REST
- Docker
- Kubernetes
- une base de données MySQL

---

## 🧱 Architecture

Le système est composé de :

- **menu-service** → gestion du catalogue de pizzas
- **order-service** → gestion des commandes
- **mysql** → base de données
- **frontend** → interface utilisateur

Les services communiquent via des API REST (JSON).

---

## ⚙️ Technologies utilisées

- Backend : Flask (Python)
- Frontend : React / HTML / JavaScript
- Base de données : MySQL
- Conteneurisation : Docker
- Orchestration : Kubernetes (Minikube)

---

## 📁 Structure du projet

```

kube-pizza/
│
├── menu-service/
├── order-service/
├── frontend/
├── database/
├── k8s/
├── docker-compose.yml
└── README.md

````

---

## 🚀 Lancer le projet en local

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-repo/kube-pizza.git
cd kube-pizza
````

### 2. Lancer avec Docker Compose

```bash
docker-compose up --build
```

### 3. Accéder à l'application

* Frontend : [http://localhost:3000](http://localhost:3000)
* Menu API : [http://localhost:5001/pizzas](http://localhost:5001/pizzas)
* Order API : [http://localhost:5002/orders](http://localhost:5002/orders)

---

## ☸️ Déploiement avec Kubernetes

### 1. Démarrer Minikube

```bash
minikube start
```

### 2. Appliquer les configurations

```bash
kubectl apply -f k8s/
```

### 3. Vérifier le déploiement

```bash
kubectl get pods
kubectl get services
```

---

## 🧪 Tests

### Tester le menu

```bash
curl http://localhost:5001/pizzas
```

### Créer une commande

```bash
curl -X POST http://localhost:5002/orders \
-H "Content-Type: application/json" \
-d '{"items":[{"pizza_id":1,"quantity":2}]}'
```

---

## 🗄️ Base de données

MySQL est utilisé pour stocker les commandes.

Tables principales :

* `orders`
* `order_items`

---

## 🔒 Sécurité (option)

* RBAC Kubernetes
* gestion des secrets (variables d’environnement)
* sécurisation des communications

---

## 👨‍💻 Auteurs

* 
* 

---

## 📌 Objectifs pédagogiques

* Comprendre les microservices
* Conteneuriser une application avec Docker
* Déployer avec Kubernetes
* Gérer la communication entre services
* Manipuler une base de données distribuée

---

## 🚧 Améliorations possibles

* ajout d’un service de notification
* ajout d’un système de paiement (simulé)
* ajout d’un service de livraison
* utilisation de gRPC (bonus)

