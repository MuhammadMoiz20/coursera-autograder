FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /grader

COPY autograder/grader.py /grader/grader.py
COPY autograder/util.py /grader/util.py
COPY config.json /grader/config.json

RUN chmod -R a+rx /grader

ENTRYPOINT ["python3", "/grader/grader.py"]
