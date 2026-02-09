# Visualisation des données en streaming

## Contexte
Dans le cadre de mon apprentissage du domaine de la Data Engineering, j'ai réalisé ce projet pour illustrer trois concepts fondamentaux :
- La **gestion des changements de schéma** (schema evolution)
- Les **mécanismes de stockage de données** en streaming
- La **visualisation en temps réel** avec des outils de visualisation interactifs

## Objectif
J'ai décidé de mettre en place une architecture simple de production, consommation et visualisation de données en streaming. Le but n'est pas de créer un système de production complexe, mais plutôt de comprendre comment ces concepts fonctionnent et interagissent ensemble.

J'ai choisi de conteneuriser les trois composants centraux (Kafka, MongoDB et le Dashboard) pour faciliter le déploiement. Le producteur et le consommateur ne sont pas conteneurisés pour l'instant, mais une conteneurisation future serait nécessaire afin de garantir la portabilité de l'environnement.

## Technologies
- **Kafka 7.5.0** : Broker de messages pour le streaming
- **Schema Registry 7.5.0** : Gestion des schémas Avro et évolution
- **MongoDB** : Base de données NoSQL pour le stockage des événements
- **Mongo Express** : Interface web pour MongoDB
- **Streamlit** : Dashboard de visualisation temps réel
- **Plotly** : Bibliothèque de visualisations interactives
- **Python 3.12** : Langage de développement
- **UV** : Gestionnaire de packages Python moderne

## Architecture

J'ai mis en place un pipeline simple de données en streaming :

```
Producer → Kafka → Consumer → MongoDB → Dashboard
```

**Ce que fait chaque composant :**

1. **Producer** (Python) : Génère des événements utilisateur simulés toutes les 2 secondes. J'ai implémenté deux versions de schéma (V1 et V2) pour démontrer l'évolution de schéma - 70% utilisent V2 et 30% utilisent V1.

2. **Kafka** (Conteneurisé) : Achemine les messages entre le producteur et le consommateur. J'utilise Avro pour la sérialisation des données et Schema Registry pour gérer les versions de schémas.

3. **Consumer** (Python) : Consomme les messages depuis Kafka et les stocke dans MongoDB. Il détecte automatiquement la version du schéma et enrichit les données avec un timestamp de réception.

4. **MongoDB** (Conteneurisé) : Stocke les événements dans une base NoSQL. J'ai choisi MongoDB pour sa flexibilité avec des schémas évolutifs.

5. **Dashboard** (Conteneurisé) : Visualise les données en temps réel avec Streamlit et Plotly. Il se rafraîchit automatiquement toutes les 5 secondes pour afficher les nouvelles données.

## Installation

### 1. Installer UV (si pas déjà installé)
```bash
pip install uv
```

### 2. Synchroniser les dépendances
```bash
uv sync
```

### 3. Démarrer l'infrastructure Docker
```bash
docker-compose up -d
```

Cette commande démarre :
- Zookeeper (port 2181)
- Kafka Broker (port 9092)
- Schema Registry (port 8081)
- MongoDB (port 27017)
- Mongo Express (port 8082)
- Dashboard Streamlit (port 8501)

## Usage

### 1. Lancer le producteur
Génère des événements utilisateur en continu (toutes les 2 secondes) :
```bash
uv run producer.py
```

### 2. Lancer le consommateur
Consomme les événements et les stocke dans MongoDB :
```bash
uv run consumer.py
```

### 3. Accéder au dashboard
Ouvrez votre navigateur à l'adresse :
```
http://localhost:8501
```

Le dashboard affiche :
- **4 KPIs** : Total événements, utilisateurs uniques, adoption V2, action principale
- **4 visualisations** : Volume temporel, répartition par type, navigateurs, appareils
- **Auto-refresh** : Option pour actualiser automatiquement toutes les 5 secondes

### 4. Accéder à Mongo Express
Interface web pour explorer MongoDB :
```
http://localhost:8082
```

## Évolution des schémas

Le projet illustre l'évolution de schémas Avro :

- **V1** : `user_id`, `event_type`, `event_timestamp`, `metadata` (device, location)
- **V2** : V1 + champ `browser` (optionnel pour rétrocompatibilité)

Le producteur génère 70% d'événements V2 et 30% d'événements V1.
Le consommateur détecte automatiquement la version et l'ajoute aux documents MongoDB.

## Structure des données MongoDB

Base de données : `streaming_db`
Collection : `events`

Structure d'un document :
```json
{
  "user_id": "user_3",
  "event_type": "CLICK",
  "event_timestamp": 1738800123456,
  "metadata": {
    "device": "mobile",
    "location": "Paris"
  },
  "browser": "Chrome",
  "received_at": "2026-02-09T14:30:23.456Z",
  "schema_version": "v2"
}
```

## Commandes utiles

### Voir les logs d'un service
```bash
docker-compose logs -f [service-name]
# Exemples : kafka, mongodb, dashboard
```

### Vérifier le statut des services
```bash
docker-compose ps
```

### Compter les événements dans MongoDB
```bash
docker exec mongodb mongosh streaming_db --eval "db.events.countDocuments({})"
```

### Arrêter tous les services
```bash
docker-compose down
```

### Supprimer les volumes (données persistantes)
```bash
docker-compose down -v
```

### Reconstruire le dashboard après modification
```bash
docker-compose build dashboard
docker-compose up -d dashboard
```

## Schémas Avro
- `user_event_v1.avsc` : Version initiale du schéma
- `user_event_v2.avsc` : Schéma évolué (compatibilité backward)

## Commandes utiles

### Gestion des dépendances
```bash
# Installer une nouvelle dépendance
uv add <package>

# Supprimer une dépendance
uv remove <package>

# Mettre à jour les dépendances
uv sync --upgrade
```

### Docker
```bash
# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f

# Nettoyer les volumes
docker-compose down -v
```
