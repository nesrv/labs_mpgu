from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: v.encode('utf-8')
)

for i in range(1, 6):
    producer.send('hello-kafka', f'Hello Kafka {i}')
    print(f'Sent: Hello Kafka {i}')

producer.close()