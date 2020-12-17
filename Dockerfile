FROM tiangolo/uvicorn-gunicorn:python3.6 AS uvicorn-builder
FROM openvino/ubuntu18_runtime:2021.1

USER root

# Copy scripts form uvicorn-builder (this is the only purpose of the uvicorn-builder build stage)
COPY --from=uvicorn-builder /start.sh /start.sh
COPY --from=uvicorn-builder /start-reload.sh /start-reload.sh

# Update pip
ENV DEBIAN_FRONTEND noninteractive
RUN python3 -m pip install --upgrade pip

# Install dependencies
COPY requirements.txt requirements.txt
RUN python3 -m pip install -U -r requirements.txt

# Configure webserver settings
ENV HOST 0.0.0.0
ENV PORT 80
ENV WORKERS_PER_CORE 1
ENV WEB_CONCURRENCY 1
ENV LOG_LEVEL debug

EXPOSE 80

COPY src/main /app
WORKDIR /app

# Setup OpenVINO environment vars before starting
CMD source /opt/intel/openvino/bin/setupvars.sh && \
    /start.sh