# Chat Distribué - Projet d'Examen DEVNET

Application de chat distribuée avec communication réseau entre conteneurs Docker, développée dans le cadre du projet d'examen de Licence 3 Réseaux et Informatique (L3 RI) - ISI Keur Massar.

## 🎯 Objectif du Projet

Ce projet démontre la capacité à combiner développement web et concepts réseau en créant une application de chat qui fonctionne sur plusieurs conteneurs Docker communiquant via un réseau personnalisé.

## 🏗️ Architecture

### Composants Principaux

- **Application Flask** : Serveur web principal avec API REST
- **Base de données PostgreSQL** : Persistance des messages et utilisateurs
- **Réseau Docker** : Communication entre services (sous-réseau 172.20.0.0/16)
- **Nginx** : Reverse proxy pour load balancing
- **2 Instances de Chat** : Déploiement distribué sur différents ports

### Aspect Réseau

- **Réseau Docker personnalisé** : `chat_network` (bridge, 172.20.0.0/16)
- **Communication inter-conteneurs** : Les instances peuvent échanger des données
- **Load balancing** : Nginx distribue les requêtes entre les instances
- **Monitoring réseau** : API pour vérifier le statut des conteneurs actifs

## 🛠️ Technologies Utilisées

- **Backend** : Flask 2.3.3 (Python)
- **Frontend** : Bootstrap 5, JavaScript vanilla
- **Base de données** : PostgreSQL 13
- **Conteneurisation** : Docker & Docker Compose
- **Reverse Proxy** : Nginx
- **Serveur WSGI** : Gunicorn

## 📋 Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- Git

## 🚀 Installation et Démarrage

### 1. Cloner le dépôt

```bash
git clone https://github.com/[votre-username]/projet_devnet.git
cd projet_devnet
```

### 2. Construire et lancer les conteneurs

```bash
docker-compose up --build
```

### 3. Accéder à l'application

- **Instance 1** : http://localhost:5001
- **Instance 2** : http://localhost:5002
- **Load Balancer** : http://localhost (Nginx)
- **Base de données** : localhost:5432

### 4. Arrêter l'application

```bash
docker-compose down
```

## 🌐 Utilisation

### Démarrage Rapide

1. Lancez les conteneurs avec `docker-compose up`
2. Accédez à http://localhost via Nginx
3. Choisissez un nom d'utilisateur
4. Commencez à chatter !

### Test de la Communication Distribuée

1. Ouvrez deux navigateurs :
   - Navigateur 1 : http://localhost:5001 (Instance 1)
   - Navigateur 2 : http://localhost:5002 (Instance 2)

2. Connectez-vous avec des utilisateurs différents

3. Envoyez des messages depuis chaque instance

4. Observez que les messages apparaissent sur les deux instances

### Vérification Réseau

- **Statut réseau** : Visitez `/api/network/status` sur n'importe quelle instance
- **Liste des conteneurs actifs** : `docker ps`
- **Logs des conteneurs** : `docker-compose logs -f`

## 📊 API Endpoints

### Messages
- `GET /api/messages` - Récupérer tous les messages
- `POST /api/messages` - Envoyer un message

### Utilisateurs
- `GET /api/users` - Lister les utilisateurs actifs
- `POST /api/users` - Enregistrer un utilisateur

### Réseau
- `GET /api/network/status` - Statut du réseau et conteneurs
- `POST /api/sync` - Synchroniser les données entre conteneurs

## 🐳 Docker Hub

L'image Docker est publiée sur Docker Hub :

```bash
docker pull [votre-username]/chat-distribue:latest
```

## 🔧 Configuration

### Variables d'Environnement

- `PORT` : Port de l'application Flask (défaut: 5000)
- `HOSTNAME` : Identifiant du conteneur
- `FLASK_ENV` : Environnement Flask (production)

### Réseau Docker

Le réseau personnalisé `chat_network` utilise :
- **Driver** : bridge
- **Sous-réseau** : 172.20.0.0/16
- **Isolation** : Les conteneurs peuvent communiquer entre eux

## 📈 Monitoring et Débogage

### Logs en temps réel

```bash
# Logs de toutes les instances
docker-compose logs -f

# Logs d'une instance spécifique
docker-compose logs -f chat-app-1
```

### Statistiques des conteneurs

```bash
# Utilisation des ressources
docker stats

# Inspection du réseau
docker network inspect projet_devnet_chat_network
```

## 🧪 Tests

### Test de communication réseau

```bash
# Test de connectivité entre conteneurs
docker exec chat-instance-1 ping chat-instance-2

# Test des API
curl http://localhost:5001/api/network/status
curl http://localhost:5002/api/network/status
```

## 📁 Structure du Projet

```
projet_devnet/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── Dockerfile            # Configuration Docker
├── docker-compose.yml    # Orchestration des services
├── nginx.conf            # Configuration Nginx
├── init.sql              # Script d'initialisation PostgreSQL
├── templates/            # Templates HTML
│   ├── index.html        # Page d'accueil
│   └── chat.html         # Interface de chat
└── README.md             # Documentation
```

## 🎓 Concepts Réseaux Démontrés

1. **Conteneurisation** : Isolation et déploiement d'applications
2. **Réseau Docker** : Communication inter-services
3. **Load Balancing** : Distribution de charge avec Nginx
4. **API REST** : Communication entre services
5. **Persistance** : Base de données partagée
6. **Monitoring** : Surveillance du réseau et des services

## 🔮 Évolutions Possibles

- **WebSockets** : Communication temps réel
- **Kubernetes** : Orchestration avancée
- **Redis** : Cache et messagerie
- **Monitoring avancé** : Prometheus + Grafana
- **CI/CD** : Pipeline GitHub Actions

## 📝 Support de Présentation

Une présentation complète est disponible expliquant :
- Le problème résolu
- L'architecture du système  
- L'aspect réseau du projet
- Les technologies utilisées
- Le fonctionnement de l'application

## 🤝 Auteur

Développé par [Votre Nom] dans le cadre du projet d'examen DEVNET - L3 Réseaux et Informatique, ISI Keur Massar.

## 📄 Licence

Ce projet est sous licence MIT.
