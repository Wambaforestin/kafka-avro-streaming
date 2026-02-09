from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from pymongo import MongoClient
from datetime import datetime, UTC

# Configuration Kafka
TOPIC = "user_events"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
GROUP_ID = "user_event_consumer_group"

# Configuration MongoDB
# Utiliser 'localhost' depuis l'hôte Windows, 'mongodb' depuis un conteneur Docker
# Pas d'authentification en mode développement
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "streaming_db"
COLLECTION_NAME = "events"

def load_schema(filename):
    with open(filename, 'r') as f:
        return f.read()

def main():
    # ====================================
    # 1. Configuration Schema Registry
    # ====================================
    schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # Nous configurons le désérialiseur pour utiliser le schéma V2 comme référence.
    # Grâce aux règles de compatibilité Avro (champs par défaut/null) :
    # - Si on reçoit un message V1 (sans browser), Avro mettra "browser=None".
    # - Si on reçoit un message V2 (avec browser), Avro le lira correctement.
    schema_v2_str = load_schema("user_event_v2.avsc")
    avro_deserializer = AvroDeserializer(schema_registry_client, schema_v2_str)

    # ====================================
    # 2. Configuration Kafka Consumer
    # ====================================
    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe([TOPIC])

    # ====================================
    # 3. Connexion MongoDB
    # ====================================
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test de connexion
        mongo_client.admin.command('ping')
        db = mongo_client[DB_NAME]
        collection = db[COLLECTION_NAME]
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        print("💡 Vérifiez que MongoDB est démarré: docker-compose ps")
        return
    
    print(f"✓ Connecté à MongoDB: {DB_NAME}.{COLLECTION_NAME}")
    print(f"✓ En attente de messages sur le topic {TOPIC}...")
    print("=" * 60)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"❌ Erreur consommateur: {msg.error()}")
                continue

            # ====================================
            # 4. Désérialisation du message
            # ====================================
            user_event = avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
            
            # ====================================
            # 5. Préparation du document MongoDB
            # ====================================
            # On stocke l'événement tel quel (V1 ou V2)
            document = {
                **user_event,  # Copie tous les champs de l'événement (user_id, action, timestamp, browser si présent)
                'received_at': datetime.now(UTC),  # Ajout du timestamp de réception (timezone-aware)
                'schema_version': 'v2' if user_event.get('browser') else 'v1'  # Détection de version
            }
            
            # ====================================
            # 6. Insertion dans MongoDB
            # ====================================
            result = collection.insert_one(document)
            
            # ====================================
            # 7. Affichage de confirmation
            # ====================================
            print("-" * 60)
            print(f"📨 Message reçu - Clé: {msg.key().decode('utf-8')}")
            print(f"   Event Type: {user_event['event_type']}")
            print(f"   Schema: {document['schema_version'].upper()}")
            
            if user_event.get('browser'):
                print(f"   Browser: {user_event['browser']}")
            
            print(f"   MongoDB ID: {result.inserted_id}")
            print(f"   Données: {user_event}")

    except KeyboardInterrupt:
        print("\n🛑 Arrêt du consommateur...")
    finally:
        consumer.close()
        mongo_client.close()
        print("✓ Connexions fermées")

if __name__ == '__main__':
    main()