# Dockerfile
FROM apache/airflow:2.9.2

# OS deps as root
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends default-jre procps \
 && rm -rf /var/lib/apt/lists/*

# (optional but nice; default-jre installs Java 17 on Debian)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Python deps as airflow user
USER airflow
RUN pip install --no-cache-dir pyspark==3.5.1
