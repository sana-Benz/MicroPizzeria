# La Micro Pizzeria - Projet de programmation distribuée

La Micro Pizzeria est une application web de commande de pizzas basée sur une architecture microservices, déployée sur Kubernetes. Les utilisateurs peuvent parcourir le menu, composer un panier, passer des commandes et consulter leur historique — le tout servi par un seul contrôleur Nginx Ingress qui route le trafic vers des services backend indépendants.

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Commandes utiles](#commandes-utiles)
3. [Architecture microservices](#architecture-microservices)
4. [Configuration Kubernetes](#configuration-kubernetes)
5. [Ingress & Routage](#ingress--routage)
6. [Décisions d'architecture](#décisions-darchitecture)
7. [Flux complet d'une requête](#flux-complet-dune-requête)

---

## Prérequis

Les outils suivants doivent être installés et configurés avant de lancer le projet :

| Outil | Rôle |
|-------|------|
| [Docker](https://docs.docker.com/get-docker/) | Construire et pousser les images de conteneurs |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | Interagir avec le cluster Kubernetes |
| [Minikube](https://minikube.sigs.k8s.io/docs/start/) | Cluster Kubernetes local (ou tout autre fournisseur K8s) |

Une fois Minikube démarré, l'addon Nginx Ingress Controller doit être activé :

```bash
minikube start
minikube addons enable ingress
```

> **Remarque :** Après avoir activé l'addon ingress, récupérez l'IP du cluster avec `minikube ip`. Toutes les requêtes passent par cette adresse (ex. `http://192.168.49.2`).

---

## Commandes utiles

### Premier déploiement

```bash
# 1. Construire et pousser toutes les images
docker build -t sanabns/user-service:latest ./user-service
docker build -t sanabns/order-service:latest ./order-service
docker build -t sanabns/frontend:latest ./frontend

docker push sanabns/user-service:latest
docker push sanabns/order-service:latest
docker push sanabns/frontend:latest

# 2. Déployer tout sur Kubernetes
chmod +x deploy.sh
./deploy.sh
```

### Redéployer un seul service après modification

```bash
# Exemple : reconstruire et redéployer le frontend
docker build -t sanabns/frontend:latest ./frontend
docker push sanabns/frontend:latest
kubectl rollout restart deployment/frontend
kubectl rollout status deployment/frontend
```

### Inspecter le cluster

```bash
kubectl get pods                          # Tous les pods en cours d'exécution
kubectl get services                      # Tous les services et leurs IPs internes
kubectl get ingress                       # Règles Ingress et IP externe
kubectl logs deployment/user-service      # Logs du user-service
kubectl logs deployment/order-service     # Logs du order-service
kubectl logs deployment/frontend          # Logs Nginx
```

### Accès aux bases de données

```bash
# Base de données utilisateurs
kubectl exec <mysql-user-pod> -- mysql -u root -p<root-password> users_db \
  -e "SELECT id, name, email FROM user;"

# Base de données commandes
kubectl exec <mysql-order-pod> -- mysql -u root -p<root-password> orders_db \
  -e "SELECT id, user_id, total, status FROM \`order\`;"
```

### Réinitialiser le cluster

```bash
kubectl delete -f ingress.yaml
kubectl delete -f frontend/k8s/
kubectl delete -f user-service/k8s/
kubectl delete -f order-service/k8s/
```

---

### ⚠️ Les fichiers secrets ne sont pas commités dans ce dépôt

Les fichiers suivants contiennent des identifiants sensibles et **doivent être créés manuellement** avant d'exécuter `deploy.sh` :

- `user-service/k8s/secret.yaml`
- `order-service/k8s/secret.yaml`

**`user-service/k8s/secret.yaml`**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: user-service-secret
  namespace: default
type: Opaque
stringData:
  secret-key: "<votre-clé-jwt>"
  mysql-password: "<mot-de-passe-users-db>"
  mysql-root-password: "<mot-de-passe-root-mysql>"
```

**`order-service/k8s/secret.yaml`**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: order-service-secret
  namespace: default
type: Opaque
stringData:
  mysql-password: "<mot-de-passe-orders-db>"
  mysql-root-password: "<mot-de-passe-root-mysql>"
```

Les valeurs renseignées ici doivent correspondre aux identifiants MySQL référencés dans les YAMLs de déploiement de chaque service.

---

## Architecture microservices

L'application est découpée en trois services indépendants, chacun avec sa propre base de code, son image de conteneur et sa base de données.

```
┌─────────────┐     REST      ┌──────────────────┐     REST      ┌──────────────────┐
│   Frontend  │ ────────────► │   user-service   │               │  order-service   │
│  (Nginx)    │               │   (Flask :5001)  │ ◄──────────── │  (Flask :5002)   │
│  port 80    │               │   MySQL :3306    │  vérif. token │   MySQL :3306    │
└─────────────┘               └──────────────────┘               └──────────────────┘
       ▲                                ▲                                  ▲
       └────────────────────────────────┴──────────────────────────────────┘
                           Nginx Ingress Controller
                             (point d'entrée unique)
```

### Frontend

| Propriété | Valeur |
|-----------|--------|
| Langage | HTML / CSS / JavaScript |
| Serveur | Nginx (Alpine) |
| Port | 80 |
| Image | `sanabns/frontend:latest` |

Site entièrement statique servi par Nginx. Il n'y a pas de rendu côté serveur — toutes les données sont récupérées côté client via des appels `fetch()` vers les endpoints `/api/*`. Le contrôleur Ingress se charge de router ces appels vers le bon service backend.

**Pages :**

| Fichier | Rôle |
|---------|------|
| `index.html` | Page d'accueil publique |
| `auth.html` | Connexion et inscription |
| `commande.html` | Navigation dans le menu et gestion du panier |
| `recapitulatif.html` | Récapitulatif de commande avant confirmation |
| `commande-terminee.html` | Écran de confirmation post-commande |
| `historique.html` | Historique complet des commandes de l'utilisateur connecté |

---

### user-service

| Propriété | Valeur |
|-----------|--------|
| Langage | Python 3.10 |
| Framework | Flask + Flask-SQLAlchemy |
| Port | 5001 |
| Base de données | MySQL 8.0 (`users_db`) |
| Image | `sanabns/user-service:latest` |

Responsable de toute la gestion des identités : inscription, connexion, émission de JWT et gestion du profil. Les mots de passe sont hachés avec **bcrypt**. Les tokens sont des JWT signés (HS256) avec une expiration d'1 heure, en utilisant une clé secrète injectée depuis un Secret Kubernetes.

**Endpoints :**

| Méthode | Chemin | Description |
|---------|--------|-------------|
| `POST` | `/auth/register` | Créer un nouveau compte |
| `POST` | `/auth/login` | S'authentifier et recevoir un JWT |
| `GET` | `/auth/validate` | Vérifier un JWT — appelé en interne par l'order-service |
| `GET` | `/users/me` | Récupérer le profil de l'utilisateur authentifié |
| `PUT` | `/users/me` | Mettre à jour le nom, téléphone ou adresse |
| `GET` | `/health` | Sonde liveness/readiness Kubernetes |

**Modèle de données — `User` :**

```
id | name | email (unique) | password (hash bcrypt) | phone | address
```

---

### order-service

| Propriété | Valeur |
|-----------|--------|
| Langage | Python 3.10 |
| Framework | Flask + Flask-SQLAlchemy |
| Port | 5002 |
| Base de données | MySQL 8.0 (`orders_db`) |
| Image | `sanabns/order-service:latest` |

Gère le catalogue du menu et toute la logique du cycle de vie des commandes. Au démarrage, il initialise automatiquement la base avec 17 articles (7 pizzas, 5 boissons, 5 desserts) si aucun n'existe. Pour authentifier les requêtes, il appelle l'endpoint `/auth/validate` du user-service via le réseau interne du cluster — il ne gère jamais les JWT directement.

**Endpoints :**

| Méthode | Chemin | Description |
|---------|--------|-------------|
| `GET` | `/menu` | Lister tous les articles du menu |
| `GET` | `/menu/<id>` | Récupérer un article spécifique |
| `POST` | `/orders` | Passer une nouvelle commande (auth requise) |
| `GET` | `/orders` | Récupérer l'historique de commandes de l'utilisateur (auth requise) |
| `GET` | `/orders/<id>` | Récupérer une commande spécifique (auth requise) |
| `PUT` | `/orders/<id>/status` | Mettre à jour le statut d'une commande |
| `PUT` | `/orders/<id>/cancel` | Annuler une commande en attente |
| `GET` | `/health` | Sonde liveness/readiness Kubernetes |

**Modèles de données :**

```
MenuItem:  id | name | category (pizza/drink/dessert) | price | description
Order:     id | user_id | delivery_address | total | status | created_at
OrderItem: id | order_id (FK) | menu_item_id (FK) | quantity | unit_price
```

**Statuts de commande :** 4 valeurs possibles : `pending` → `preparing` → `delivered` (ou `cancelled`)

---

## Configuration Kubernetes

Toutes les ressources se trouvent dans le namespace `default`. Le projet utilise les primitives K8s suivantes :

### Deployments

Chaque service (user-service, order-service, frontend, mysql-user, mysql-order) tourne en tant que **Deployment** avec 1 réplica. Les Deployments ont été choisis plutôt que des Pods nus car ils offrent un redémarrage automatique en cas de crash, des mises à jour progressives sans interruption, et un sélecteur stable pour que les Services puissent les cibler.

Tous les déploiements applicatifs utilisent `imagePullPolicy: Always` pour s'assurer que la dernière image poussée est récupérée à chaque redémarrage — important lors de l'utilisation d'un tag `latest` en développement actif.

### Init Containers

Les deux services Flask déclarent un init container (`busybox`) qui boucle jusqu'à ce que le pod MySQL accepte des connexions sur le port 3306. Cela évite que l'application Flask crashe au démarrage à cause d'une base de données pas encore prête — une condition de course courante dans les déploiements multi-pods.

```yaml
initContainers:
  - name: wait-for-mysql
    image: busybox
    command: ['sh', '-c', 'until nc -z mysql-user 3306; do sleep 2; done']
```

### Services

Chaque Deployment est exposé par un **Service ClusterIP**. ClusterIP a été choisi car aucun service backend n'a besoin d'être directement accessible depuis l'extérieur du cluster — seul le contrôleur Ingress communique avec eux via le réseau interne. Cela minimise la surface d'attaque.

| Service | Port | Cible |
|---------|------|-------|
| `user-service` | 5001 | pods user-service |
| `order-service` | 5002 | pods order-service |
| `frontend` | 80 | pods Nginx |
| `mysql-user` | 3306 | pod MySQL (DB utilisateurs) |
| `mysql-order` | 3306 | pod MySQL (DB commandes) |

### PersistentVolumeClaims

Chaque instance MySQL dispose d'un **PVC** dédié (`mysql-user-pvc`, `mysql-order-pvc`) demandant 1Gi avec un mode d'accès `ReadWriteOnce`. Cela garantit que les fichiers de base de données survivent aux redémarrages et aux replanifications des pods. Sans PVC, toutes les données seraient perdues à chaque fois que le pod MySQL est arrêté.

### Secrets

Les mots de passe des bases de données et la clé de signature JWT sont stockés dans des **Secrets** Kubernetes, non codés en dur dans les YAMLs de déploiement ni commités dans le dépôt. Ils sont injectés comme variables d'environnement dans la spec du pod :

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: user-service-secret
        key: mysql-password
```

La rotation d'un identifiant nécessite uniquement de mettre à jour le Secret et de redémarrer le pod concerné — aucune reconstruction d'image n'est nécessaire.

### Sondes de santé

Les deux services Flask exposent un endpoint `/health` retournant `{"status": "ok"}`. Kubernetes l'utilise pour :
- **Readiness probe** — ne pas router le trafic vers le pod tant qu'il ne répond pas correctement
- **Liveness probe** — redémarrer le pod s'il cesse de répondre

### Limites de ressources

Tous les pods déclarent des `requests` et `limits` de CPU et mémoire pour éviter qu'un seul service n'affame les autres sur un nœud partagé.

| Service | CPU request | CPU limit | Mémoire request | Mémoire limit |
|---------|-------------|-----------|-----------------|---------------|
| user-service | 100m | 250m | 128Mi | 256Mi |
| order-service | 100m | 250m | 128Mi | 256Mi |
| frontend | 50m | 100m | 64Mi | 128Mi |

---

## Ingress & Routage

Un seul **Nginx Ingress Controller** constitue l'unique point d'entrée dans le cluster. Tout le trafic HTTP arrive à l'IP Minikube sur le port 80 et est routé vers le service backend approprié en fonction du préfixe du chemin URL.

### Pourquoi Nginx Ingress ?

- C'est l'addon intégré à Minikube et ne nécessite aucune configuration supplémentaire.
- Il supporte la correspondance de chemin par regex et les règles de réécriture, nécessaires ici pour supprimer le préfixe `/api/` avant de transmettre les requêtes aux services backend.
- C'est le contrôleur Ingress standard de facto et il reproduit fidèlement les configurations de passerelles API en production.

### Table de routage

| Chemin entrant | Réécrit en | Transmis à |
|----------------|-----------|-----------|
| `/api/users/*` | `/users/*` | `user-service:5001` |
| `/api/auth/*` | `/auth/*` | `user-service:5001` |
| `/api/orders/*` | `/orders/*` | `order-service:5002` |
| `/api/menu/*` | `/menu/*` | `order-service:5002` |
| `/*` (catch-all) | `/*` | `frontend:80` |

La réécriture de chemin est réalisée grâce à deux annotations sur la ressource Ingress :

```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /$2
  nginx.ingress.kubernetes.io/use-regex: "true"
```

Les services backend n'ont aucune connaissance de la structure d'URL publique — ils ne voient que des chemins comme `/orders` ou `/auth/login`.

### Routage par chemin vs par hôte

Le **routage par chemin** a été choisi car l'application tourne sous une seule adresse IP sans nom de domaine enregistré. Le routage par hôte (ex. `api.micropizzeria.com`) nécessiterait une configuration DNS et est plus adapté aux déploiements en production avec de vrais domaines et une terminaison TLS.

### TLS

TLS n'est pas configuré dans la configuration actuelle (HTTP uniquement). Dans un environnement de production, un `ClusterIssuer` cert-manager adossé à Let's Encrypt serait ajouté et l'Ingress serait annoté pour gérer la terminaison HTTPS au niveau du contrôleur.

---

## Décisions d'architecture

### Microservices

L'application sépare délibérément les préoccupations d'authentification (user-service) des préoccupations de commande (order-service) en unités déployables indépendantes. Cela signifie que :

- Chaque service peut être mis à jour, redémarré ou mis à l'échelle sans affecter l'autre.
- Chaque service possède son propre schéma de base de données — il n'y a pas de tables partagées ni de jointures SQL inter-services.
- Les pannes sont isolées : si l'order-service crashe, les utilisateurs peuvent toujours s'authentifier.

Le compromis est une complexité opérationnelle accrue (plus de déploiements à gérer, des appels HTTP inter-services susceptibles d'échouer). À cette échelle, un monolithe serait plus simple, mais la structure microservices a été choisie pour pratiquer la conception d'applications Kubernetes-native et la décomposition en services.

### Kubernetes 

Kubernetes a été choisi pour pratiquer :

- L'infrastructure déclarative sous forme de manifestes YAML versionnés dans le dépôt
- La découverte de services via DNS (les services se référencent par nom, ex. `http://user-service:5001`)
- Les vérifications de santé natives, les redémarrages automatiques et les déploiements progressifs
- Le routage basé sur l'Ingress qui reproduit le fonctionnement des passerelles API en production

### Bases de données séparées par service

Chaque service possède sa propre instance MySQL (pods et PVCs séparés), conformément au pattern **Database per Service**. Ce pattern stipule que les données persistantes d'un service lui sont privées et ne sont accessibles que via son API — aucun autre service ne peut requêter directement sa base de données.

Une base de données partagée serait plus simple opérationnellement, mais couplerait les deux services au niveau de la couche données : un changement de schéma dans une table pourrait casser l'autre service, et les déploiements indépendants deviendraient risqués.

**Avantages dans ce projet :**
- Le user-service et l'order-service peuvent évoluer indépendamment sans coordination de schéma.
- Chaque service utilise uniquement le type de base dont il a besoin (ici MySQL pour les deux, mais rien n'empêcherait l'un d'utiliser MongoDB ou Redis si le besoin évoluait).
- Les pannes de base de données sont isolées par service.

### Validation des tokens via HTTP

L'order-service ne contient aucune logique de décodage JWT. Lorsqu'il reçoit une requête authentifiée, il transmet le bearer token à `user-service/auth/validate` et fait confiance à la réponse. Cela signifie que :

- La clé secrète JWT réside exclusivement dans le user-service.
- Changer l'algorithme de signature ou faire une rotation de la clé ne nécessite que de mettre à jour le user-service.
- L'order-service reste sans état en ce qui concerne l'authentification.

### Stratégie de mise à l'échelle

Les deux services Flask étant sans état (tout l'état persistant est dans MySQL), les mettre à l'échelle horizontalement ne nécessite que d'augmenter le champ `replicas` dans le Deployment. Les instances MySQL sont intentionnellement maintenues à 1 réplica — la mise à l'échelle horizontale de MySQL nécessite des outils dédiés (ex. réplicas en lecture, MySQL Operator) qui sortent du cadre de ce projet.

---

## Flux complet d'une requête

La trace suivante suit un utilisateur passant une commande, du navigateur jusqu'à la base de données et en retour.

```
Navigateur
  │
  │  POST /api/orders
  │  Authorization: Bearer <jwt>
  │  Body: { delivery_address, items: [{menu_item_id, quantity}, ...] }
  │
  ▼
Nginx Ingress Controller  (minikube-ip:80)
  │  Le chemin correspond à /api(/)(orders.*)
  │  Réécriture du chemin → /orders
  │  Transmission à order-service:5002
  │
  ▼
Pod order-service
  │
  │  1. Extrait le JWT depuis l'en-tête Authorization
  │  2. Appelle GET http://user-service:5001/auth/validate
  │     (le DNS Kubernetes résout "user-service" vers son ClusterIP)
  │
  ▼
Pod user-service
  │  Décode et vérifie le JWT avec SECRET_KEY
  │  Retourne { "valid": true, "user_id": 4, "name": "Jean Dupont" }
  │
  ▼
Pod order-service  (reprend l'exécution)
  │  3. Crée une nouvelle ligne dans la table `order`
  │  4. Pour chaque article dans le corps de la requête :
  │     - Récupère le prix dans la table `menu_item`
  │     - Insère une ligne dans la table `order_item`
  │     - Cumule le total courant
  │  5. Écrit le total final dans la ligne `order`
  │  6. Retourne { "order_id": 3, "status": "pending", "total": 41.50 }
  │
  ▼
Nginx Ingress  (réponse, sans réécriture au retour)
  │
  ▼
Navigateur
  Stocke order_id dans localStorage
  Redirige vers commande-terminee.html
```

**Résolution DNS à l'intérieur du cluster :**
Kubernetes crée automatiquement un enregistrement DNS pour chaque Service. Lorsque l'`order-service` appelle `http://user-service:5001`, le DNS du cluster résout le nom d'hôte `user-service` vers le ClusterIP du Service correspondant, qui répartit la charge entre tous les pods sains derrière lui. Aucune adresse IP codée en dur n'apparaît dans le code de l'application.