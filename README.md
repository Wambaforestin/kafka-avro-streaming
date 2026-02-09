# Visualisation des données en streaming

## Objectif
Ce projet illustre une architecture complète de traitement de données en streaming avec Kafka, Avro, MongoDB et visualisation en temps réel. Il démontre la gestion de l'évolution des schémas Avro et le traitement de flux d'événements utilisateur.

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

Le projet suit un pipeline de données en streaming :

```
Producer → Kafka → Consumer → MongoDB → Dashboard
```

1. **Producer** : Génère des événements utilisateur aléatoires (70% schéma V2, 30% schéma V1)
2. **Kafka** : Achemine les messages avec sérialisation Avro
3. **Consumer** : Consomme les messages et les stocke dans MongoDB
4. **MongoDB** : Stocke les événements avec enrichissement (timestamp, version)
5. **Dashboard** : Visualise les données en temps réel avec Streamlit et Plotly

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
