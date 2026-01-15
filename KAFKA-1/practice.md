# Установка Apache Kafka в WSL

## Рекомендуемая версия для обучения (2026)

**Для обучения в 2026 году рекомендуется использовать Apache Kafka 4.1.1** (последняя стабильная версия на январь 2026).

### Почему Kafka 4.1.1?

- **Последние исправления и патчи безопасности** - актуальная стабильная версия
- **Полностью KRaft-архитектура** - Zookeeper полностью удален начиная с версии 4.0, это будущее Kafka
- **Современные функции** - включает все актуальные возможности и улучшения
- **Релевантность знаний** - изучение актуальной версии даст знания, применимые в реальных проектах

**Альтернатива:** Kafka 4.0.1 также подходит, но 4.1.1 предпочтительнее из-за дополнительных улучшений.

**Важно:** В версиях Kafka 4.0+ Zookeeper больше не используется - только KRaft mode. Это упрощает установку и настройку.

## Предварительные требования

### 1. Установка Java

Kafka требует Java для работы. Рекомендуется использовать Java 11 или 17 (LTS версии).

**Вариант 1: Установка OpenJDK 17 (рекомендуется)**

```bash
sudo apt update
sudo apt install -y openjdk-17-jre-headless
```

**Вариант 2: Установка OpenJDK 11**

```bash
sudo apt update
sudo apt install -y openjdk-11-jre-headless
```

**Проверка установки Java:**

```bash
java -version
```

**Примечание:** Если OpenJDK 16 недоступен в репозиториях (что часто бывает), используйте версию 11 или 17 - они полностью совместимы с Kafka.

### 2. Установка Kafka

#### Скачивание Kafka

```bash
# Перейдите в директорию для установки
cd ~
# или в вашу рабочую директорию
cd /mnt/c/W26/project/mpgu_practice/KAFKA-1

# Скачайте Kafka 4.1.1 (рекомендуемая версия для обучения в 2026)
# Правильный формат URL: /kafka/ВЕРСИЯ/kafka_SCALA_ВЕРСИЯ-KAFKA_ВЕРСИЯ.tgz

# Способ 1: Прямое скачивание с проверкой целостности
wget https://downloads.apache.org/kafka/4.1.1/kafka_2.13-4.1.1.tgz

# Проверка размера файла (должен быть примерно 70-80 МБ)
ls -lh kafka_2.13-4.1.1.tgz

# Если файл скачался не полностью или поврежден, удалите его и скачайте заново:
# rm kafka_2.13-4.1.1.tgz
# wget https://downloads.apache.org/kafka/4.1.1/kafka_2.13-4.1.1.tgz

# Альтернативный способ (если прямой URL не работает):
# 1. Откройте в браузере: https://kafka.apache.org/downloads
# 2. Найдите версию 4.1.1 и скачайте бинарный дистрибутив (Binary downloads)
# 3. Или используйте зеркало:
# wget https://archive.apache.org/dist/kafka/4.1.1/kafka_2.13-4.1.1.tgz

# Распакуйте архив
# Если получили ошибку "unexpected end of file" - файл скачан не полностью
# Удалите поврежденный файл и скачайте заново
tar -xzf kafka_2.13-4.1.1.tgz

# Переименуйте директорию для удобства (опционально)
mv kafka_2.13-4.1.1 kafka
cd kafka
```

#### Настройка переменных окружения (опционально)

**Где находятся файлы `~/.bashrc` и `~/.zshrc`?**

- **`~`** — это символ домашней директории пользователя (в WSL обычно `/home/ваше_имя_пользователя/`)
- **`~/.bashrc`** — файл конфигурации для bash (например: `/home/user/.bashrc`)
- **`~/.zshrc`** — файл конфигурации для zsh (например: `/home/user/.zshrc`)

**Как найти и отредактировать файл:**

```bash
# 1. Узнать путь к домашней директории
echo $HOME
# или просто
echo ~

# 2. Проверить, какой shell используется
echo $SHELL

# 3. Проверить существование файла
ls -la ~/.bashrc
ls -la ~/.zshrc

# 4. Открыть файл для редактирования (выберите один из способов)
nano ~/.bashrc          # простой текстовый редактор
vim ~/.bashrc           # если установлен vim
code ~/.bashrc           # если установлен VS Code
```

**Добавьте в `~/.bashrc` или `~/.zshrc`** (в зависимости от используемого shell):

```bash
export KAFKA_HOME=~/kafka
export PATH=$PATH:$KAFKA_HOME/bin
```

Затем выполните:

```bash
source ~/.bashrc
```

**Что делает `source ~/.bashrc`?**

Команда `source` применяет изменения из файла `~/.bashrc` в текущей сессии терминала без необходимости перезапуска.

- **`source`** — встроенная команда bash, которая выполняет команды из указанного файла в текущей оболочке
- **`~/.bashrc`** — файл конфигурации bash, который обычно выполняется при запуске интерактивной оболочки

**Зачем это нужно?** Когда вы добавляете переменные окружения в `~/.bashrc`, они не применяются автоматически в уже открытом терминале. Команда `source ~/.bashrc` применяет эти изменения немедленно, делая переменные `KAFKA_HOME` и обновленный `PATH` доступными в текущей сессии.

**Альтернатива:** Можно использовать точку вместо `source`:

```bash
. ~/.bashrc
```

После выполнения `source ~/.bashrc` вы сможете использовать команды Kafka (например, `kafka-topics.sh`) без указания полного пути, так как директория `bin` будет добавлена в `PATH`.

### 3. Запуск Kafka

**Важно:** В версиях Kafka 4.0+ (включая 4.1.1) Zookeeper больше не используется. Kafka работает только в режиме KRaft (Kafka Raft).

#### Создание конфигурационного файла для KRaft

Если при запуске Kafka возникает ошибка `java.nio.file.NoSuchFileException: config/kraft/server.properties`, это означает, что файл конфигурации для KRaft режима отсутствует.

**Решение:** Создайте директорию и файл конфигурации:

```bash
# Создайте директорию для конфигурации KRaft
mkdir -p config/kraft

# Скопируйте базовый конфигурационный файл
cp config/server.properties config/kraft/server.properties
```

Или создайте файл `config/kraft/server.properties` вручную с настройками для KRaft режима. Файл должен содержать следующие основные параметры:

```properties
# Режим KRaft (broker и controller в одном процессе)
process.roles=broker,controller

# ID узла
node.id=1

# Endpoints контроллера
controller.quorum.bootstrap.servers=localhost:9093

# Listeners
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
advertised.listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
controller.listener.names=CONTROLLER

# Директория для логов
log.dirs=/tmp/kraft-combined-logs
```

**Примечание:** Полный пример конфигурационного файла можно найти в `config/server.properties` - он уже настроен для KRaft режима и может быть скопирован в `config/kraft/server.properties`.

#### Запуск Kafka в KRaft режиме (Kafka 4.0+)

Для Kafka 4.1.1 используется только KRaft mode:

```bash
# Шаг 1: Генерация cluster-id (только при первом запуске)
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"

# Шаг 2: Форматирование хранилища (только при первом запуске)
# Флаг --standalone используется для одиночного узла (режим разработки/обучения)
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties --standalone

# Успешное форматирование покажет сообщение:
# "Formatting dynamic metadata voter directory ... with metadata.version 4.1-IV1."
# Это означает, что хранилище успешно отформатировано и готово к использованию.

# Шаг 3: Запуск Kafka в фоновом режиме
bin/kafka-server-start.sh -daemon config/kraft/server.properties
```

**Или запуск в отдельном терминале для просмотра логов:**

```bash
# Генерация cluster-id (если еще не сделано)
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"

# Форматирование хранилища (если еще не сделано)
# Флаг --standalone используется для одиночного узла (режим разработки/обучения)
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties --standalone

# Успешное форматирование покажет сообщение:
# "Formatting dynamic metadata voter directory ... with metadata.version 4.1-IV1."
# Это означает, что хранилище успешно отформатировано и готово к использованию.

# Запуск Kafka
bin/kafka-server-start.sh config/kraft/server.properties
```

**Примечание:** Для версий Kafka до 4.0 (например, 3.x) требуется Zookeeper. Инструкции для старых версий см. в разделе 6.

### 4. Проверка работы

#### Создание топика

```bash
bin/kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

#### Просмотр списка топиков

```bash
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

#### Отправка сообщений (Producer)

```bash
bin/kafka-console-producer.sh --topic test-topic --bootstrap-server localhost:9092
```

#### Получение сообщений (Consumer)

```bash
bin/kafka-console-consumer.sh --topic test-topic --from-beginning --bootstrap-server localhost:9092
```

### 5. Остановка Kafka

```bash
# Остановка Kafka (для версий 4.0+)
bin/kafka-server-stop.sh
```

**Примечание:** Для версий Kafka 4.0+ Zookeeper не используется, поэтому его останавливать не нужно.

### 6. Информация о версиях Kafka

#### Kafka 4.0+ (включая 4.1.1) - только KRaft mode

Начиная с версии 4.0, Kafka работает **только** в режиме KRaft. Zookeeper полностью удален. Это упрощает установку и настройку.

### 7. Полезные команды

```bash
# Описание топика
bin/kafka-topics.sh --describe --topic test-topic --bootstrap-server localhost:9092

# Удаление топика
bin/kafka-topics.sh --delete --topic test-topic --bootstrap-server localhost:9092

# Просмотр групп потребителей
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Просмотр логов топика
bin/kafka-console-consumer.sh --topic test-topic --from-beginning --bootstrap-server localhost:9092 --max-messages 10
```

### 9. Решение проблем

**Проблема: `No readable meta.properties files found`**

Эта ошибка возникает, когда хранилище Kafka не было отформатировано перед первым запуском. Решение:

```bash
# 1. Убедитесь, что Kafka остановлен
bin/kafka-server-stop.sh

# 2. Сгенерируйте cluster-id
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"

# 3. Отформатируйте хранилище (ВАЖНО: это удалит все существующие данные!)
# Флаг --standalone используется для одиночного узла
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties --standalone

# 4. Запустите Kafka снова
bin/kafka-server-start.sh config/kraft/server.properties
```

**Важно:** Команда `format` удалит все существующие данные в хранилище Kafka. Используйте её только при первом запуске или когда нужно полностью очистить данные.

**Проблема: `Because controller.quorum.voters is not set... you must specify one of the following: --standalone, --initial-controllers, or --no-initial-controllers`**

Эта ошибка возникает при форматировании хранилища без указания режима контроллера. Для одиночного узла (standalone mode) используйте флаг `--standalone`:

```bash
# Правильная команда форматирования для одиночного узла
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties --standalone
```

**Что означает `--standalone`?** Это упрощенный режим для одиночного узла, где broker и controller работают в одном процессе. Идеально подходит для разработки и обучения.

**Проблема: `java.nio.file.NoSuchFileException: config/kraft/server.properties`**

Эта ошибка возникает, когда файл конфигурации для KRaft режима отсутствует. Решение:

```bash
# Создайте директорию для конфигурации KRaft
mkdir -p config/kraft

# Скопируйте базовый конфигурационный файл (который уже настроен для KRaft)
cp config/server.properties config/kraft/server.properties
```

После этого можно запускать Kafka согласно инструкциям в разделе 3.

### 10. Альтернатива: Docker

Для упрощения можно использовать Kafka через Docker. Для Kafka 4.1.1 используется только KRaft mode (без Zookeeper).

**Создайте файл `docker-compose.yml`:**

```yaml
version: "3.8"
services:
  kafka:
    image: apache/kafka:4.1.1
    container_name: kafka
    ports:
      - "9092:9092"
      - "9093:9093"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      CLUSTER_ID: MkU3OEVBNTcwNTJENDM2Qk
    volumes:
      - kafka-data:/var/lib/kafka/data
    healthcheck:
      test:
        [
          "CMD",
          "kafka-broker-api-versions",
          "--bootstrap-server",
          "localhost:9092",
        ]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  kafka-data:
```

**Запуск:**

```bash
# Запуск Kafka через Docker Compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f kafka

# Остановка
docker-compose down

# Остановка с удалением данных
docker-compose down -v
```

**Примечание:** Если образ `apache/kafka:4.1.1` недоступен, можно использовать:

- `apache/kafka:latest` (последняя версия)
- `confluentinc/cp-kafka:7.6.0` (версия Confluent Platform с поддержкой KRaft)

**Для старых версий Kafka (3.x и ниже) с Zookeeper:**

Если нужна версия с Zookeeper (для совместимости со старыми версиями):

```yaml
version: "3.8"
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```
