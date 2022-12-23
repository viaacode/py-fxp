# py-fxp
## Description
- Rabbitmq worker
## Setup
- pip install -r requirements.txt
- or Docker build . -t py-fxp:dev
## Config
- create a config.yml file as below for docker or when setting the vars as env or just fill in the vars
```
viaa:
  logging:
    level: INFO

app:
  rabbitmq:
    host: !ENV ${RABBITMQ_HOST}
    port: 5672
    username: !ENV ${RABBITMQ_USERNAME}
    password: !ENV ${RABBITMQ_PASSWORD}
    queue: !ENV ${RABBITMQ_QUEUE}
    prefetch_count: !ENV ${RABBITMQ_PREFETCH}
```
## Start
``` python main.py```
