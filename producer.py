import time
import random
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

    # 3. Chargement des schémas
    schema_v1_str = load_schema("user_event_v1.avsc")
    schema_v2_str = load_schema("user_event_v2.avsc")
    
    avro_serializer_v1 = AvroSerializer(schema_registry_client, schema_v1_str)
    avro_serializer_v2 = AvroSerializer(schema_registry_client, schema_v2_str)

    # Données pour génération aléatoire
    users = [f"user_{i}" for i in range(1, 11)]
    event_types = ["LOGIN", "CLICK", "LOGOUT", "PURCHASE", "VIEW"]
    browsers = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
    devices = ["mobile", "desktop", "tablet"]
    locations = ["Paris", "London", "New York", "Tokyo", "Berlin"]
    
    print("\n🚀 Producteur démarré - Génération continue d'événements")
    print("📊 70% Schéma V2 (avec browser) | 30% Schéma V1 (sans browser)")
    print("Ctrl+C pour arrêter\n")
    print("=" * 60)

    counter = 0
    try:
        while True:
            counter += 1
            user_id = random.choice(users)
            event_type = random.choice(event_types)
            
            # 70% de chance d'utiliser V2, 30% V1
            use_v2 = random.random() < 0.7
            
            if use_v2:
                # Événement V2 avec browser
                event = {
                    "user_id": user_id,
                    "event_type": event_type,
                    "event_timestamp": int(time.time() * 1000),
                    "metadata": {
                        "device": random.choice(devices),
                        "location": random.choice(locations)
                    },
                    "browser": random.choice(browsers)
                }
                
                producer.produce(
                    topic=TOPIC,
                    key=StringSerializer()(user_id),
                    value=avro_serializer_v2(event, SerializationContext(TOPIC, MessageField.VALUE)),
                    on_delivery=delivery_report
                )
                schema_version = "V2"
            else:
                # Événement V1 sans browser
                event = {
                    "user_id": user_id,
                    "event_type": event_type,
                    "event_timestamp": int(time.time() * 1000),
                    "metadata": {
                        "device": random.choice(devices),
                        "location": random.choice(locations)
                    }
                }
                
                producer.produce(
                    topic=TOPIC,
                    key=StringSerializer()(user_id),
                    value=avro_serializer_v1(event, SerializationContext(TOPIC, MessageField.VALUE)),
                    on_delivery=delivery_report
                )
                schema_version = "V1"
            
            producer.poll(0)
            
            # Affichage périodique
            if counter % 5 == 0:
                producer.flush()
                print(f"✅ {counter} événements envoyés...")
            
            # Pause entre les messages (2 secondes)
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du producteur...")
        producer.flush()
        print(f"✓ Total: {counter} événements envoyés")

if __name__ == '__main__':
    main()