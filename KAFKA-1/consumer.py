from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'hello-kafka',
    bootstrap_servers='localhost:19092',
    group_id='hello-group',
    auto_offset_reset='earliest',
    value_deserializer=lambda v: v.decode('utf-8')
)

for msg in consumer:
    print(f'Received: {msg.value}')