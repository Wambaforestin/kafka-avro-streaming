import time
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

# Configuration
TOPIC = "user_events"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

def load_schema(filename):
    with open(filename, 'r') as f:
        return f.read()

def delivery_report(err, msg):
    if err is not None:
        print(f"Échec de l'envoi du message: {err}")
    else:
        print(f"Message envoyé à {msg.topic()} [{msg.partition()}] offset {msg.offset()}")

def main():
    # 1. Configuration du Client Schema Registry
    schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # 2. Configuration du Producteur Kafka
    producer_conf = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}
    producer = Producer(producer_conf)

    # --- PHASE 1 : Envoi avec Schéma V1 ---
    print("\n--- Démarrage Phase 1 : Schéma V1 ---")
    schema_v1_str = load_schema("user_event_v1.avsc")
    
    # Le sérialiseur Avro enregistre automatiquement le schéma s'il n'existe pas
    avro_serializer_v1 = AvroSerializer(schema_registry_client, schema_v1_str)

    event_v1 = {
        "user_id": "user_123",
        "event_type": "LOGIN",
        "event_timestamp": int(time.time() * 1000),
        "metadata": {
            "device": "mobile",
            "location": "Paris"
        }
    }

    producer.produce(
        topic=TOPIC,
        key=StringSerializer()("user_123"),
        value=avro_serializer_v1(event_v1, SerializationContext(TOPIC, MessageField.VALUE)),
        on_delivery=delivery_report
    )
    producer.flush()
    time.sleep(1)

    # --- PHASE 2 : Évolution vers Schéma V2 ---
    print("\n--- Démarrage Phase 2 : Évolution vers Schéma V2 (Ajout 'browser') ---")
    schema_v2_str = load_schema("user_event_v2.avsc")
    
    # Nous utilisons un nouveau sérialiseur basé sur la V2
    avro_serializer_v2 = AvroSerializer(schema_registry_client, schema_v2_str)

    event_v2 = {
        "user_id": "user_456",
        "event_type": "CLICK",
        "event_timestamp": int(time.time() * 1000),
        "metadata": {
            "page": "/home",
            "product_id": "prod_999"
        },
        "browser": "Chrome" # <--- Le nouveau champ !
    }

    producer.produce(
        topic=TOPIC,
        key=StringSerializer()("user_456"),
        value=avro_serializer_v2(event_v2, SerializationContext(TOPIC, MessageField.VALUE)),
        on_delivery=delivery_report
    )
    producer.flush()

    print("Fin de la production.")

if __name__ == '__main__':
    main()