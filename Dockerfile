FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --no-install-recommends -y bash git curl &&\
  rm -rf /var/lib/apt/lists/*
RUN useradd -s /bin/sh -m -g 1000 -d /app app
WORKDIR /app
COPY . .
RUN chown -R app:1000 /app && chmod g+w -R /app
USER app
ENV PATH PATH=$PATH:/app/.local/bin

RUN pip install -r requirements.txt
ENV PATH=$PATH:/app/.local/bin
CMD ["python", "main.pyc"]
