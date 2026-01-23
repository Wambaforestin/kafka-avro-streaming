# Kafka Avro Project

## Objectif
Système de streaming de données avec Kafka et Avro pour produire et consommer des événements utilisateur avec gestion de schémas.

## Technologies
- **Apache Kafka** : Plateforme de streaming
- **Avro** : Sérialisation de données
- **Schema Registry** : Gestion et évolution des schémas
- **Python 3.12+** : Langage de développement
- **UV** : Gestionnaire de dépendances Python

## Installation

### 1. Installer UV
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Cloner et configurer le projet
```bash
cd kafka-avro-project
uv sync
```

### 3. Démarrer l'infrastructure Kafka
```bash
docker-compose up -d
```

Vérifier que les services sont actifs :
- Kafka : `localhost:9092`
- Schema Registry : `localhost:8081`
- Zookeeper : `localhost:2181`

## Utilisation

### Produire des événements
```bash
uv run producer.py
```

### Consommer des événements
```bash
uv run consumer.py
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
