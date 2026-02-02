FROM apache/spark:3.5.0

USER root

# Install Python & basic tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Spark jobs (optional but recommended)
COPY spark_jobs/ /app/spark_jobs/

# Hadoop AWS + AWS SDK (for MinIO / S3A)
RUN curl -o /opt/spark/jars/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -o /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Let container stay alive (Airflow submits jobs)
CMD ["tail", "-f", "/dev/null"]
