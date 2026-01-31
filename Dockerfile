FROM apache/spark:3.5.0

USER root

#install python & tools
RUN apt-get update && apt-get install -y\
    python3 \ 
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# COPY requirements.txt  /app/requirements.txt
# RUN pip3 install --no-cache-dir -r /app/requirements.txt

#Hadoop AWS + AWS SDK (required for S3 access)
RUN curl -o /opt/spark/jars/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -o /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.554/aws-java-sdk-bundle-1.12.262.jar

# COPY app /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["spark-submit", "--master", "local[*]", "main.py"]
