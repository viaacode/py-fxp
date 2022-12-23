# py-fxp
## Description
- Rabbitmq worker
FXP a file from server 1 to server 2 (FTPext)
### message example
```
        {
          "destination_file": "target-testfile.txt",
          "destination_host": "host2",
          "destination_password": "passwd2",
          "destination_path": "path2",
          "destination_user": "path2",
          "source_file": "testfile.txt",
          "source_host": "host1",
          "source_password": "passwd1",
          "source_path": "path1",
          "source_user": "user1",
          "move": false
        }
```

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
```
python main.py
```
