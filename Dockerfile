# MERN Notes App Autograder for Coursera
# This Dockerfile builds the complete autograder package

# Fetch ubuntu 20.04 LTS docker image
FROM ubuntu:20.04

# Install Node.js and npm
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python3 for the grader
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Make directories for storing your files.
RUN mkdir /grader
RUN mkdir /grader/solutions

# The commands below copy files into the Docker image.
# Main grader file
COPY autograder/grader.py /grader/grader.py
# Helper functions
COPY autograder/util.py /grader/util.py
COPY autograder/testCases.py /grader/testCases.py

# Important: Docker images are run without root access on our platforms. Its important to setup permissions accordingly.
# Executable permissions: Required to execute grader.py
# Read/write permissions: Required to copy over the submission from shared/submission
RUN chmod a+rwx -R /grader/

# Setup the command that will be invoked when your docker image is run.
ENTRYPOINT ["python3", "/grader/grader.py"]
