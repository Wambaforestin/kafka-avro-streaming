from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

# Configuration
TOPIC = "user_events"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
GROUP_ID = "user_event_consumer_group"

def load_schema(filename):
    with open(filename, 'r') as f:
        return f.read()

def main():
    schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # Nous configurons le désérialiseur pour utiliser le schéma V2 comme référence.
    # Grâce aux règles de compatibilité Avro (champs par défaut/null) :
    # - Si on reçoit un message V1 (sans browser), Avro mettra "browser=None".
    # - Si on reçoit un message V2 (avec browser), Avro le lira correctement.
    schema_v2_str = load_schema("user_event_v2.avsc")
    avro_deserializer = AvroDeserializer(schema_registry_client, schema_v2_str)

    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe([TOPIC])

    print(f"En attente de messages sur le topic {TOPIC}...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Erreur consommateur: {msg.error()}")
                continue

            # Désérialisation
            user_event = avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
            
            # Affichage
            print("-" * 50)
            print(f"Clé: {msg.key().decode('utf-8')}")
            print(f"Event Type: {user_event['event_type']}")
            
            # Vérification de la version du schéma via la présence du champ browser
            if user_event.get('browser'):
                print(f"Version Détectée: V2 | Browser: {user_event['browser']}")
            else:
                print("Version Détectée: V1 | Browser: Non spécifié (Valeur par défaut appliquée)")
            
            print(f"Données complètes: {user_event}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()