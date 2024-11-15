FROM tiangolo/uvicorn-gunicorn:python3.9 AS uvicorn-builder
FROM openvino/ubuntu18_runtime:2021.4

USER root

# Log start of copying scripts
COPY --from=uvicorn-builder /start.sh /start.sh
COPY --from=uvicorn-builder /start-reload.sh /start-reload.sh

# Update pip
ENV DEBIAN_FRONTEND=noninteractive
RUN python3 -m pip install --upgrade pip

# Install build tools and OpenCV dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    libgl1-mesa-glx \
    libglib2.0-0

# Log the installation of Python dependencies
COPY requirements.txt requirements.txt
RUN python3 -m pip install -U -r requirements.txt

ENV HOST=0.0.0.0
ENV PORT=80
ENV WORKERS_PER_CORE=1
ENV WEB_CONCURRENCY=1
ENV LOG_LEVEL=debug
ENV ACCESS_LOG=True
ENV ERROR_LOG=True

EXPOSE 80

# Log the copying of application files
COPY src/main /app
WORKDIR /app

# Setup OpenVINO and start the app
CMD source /opt/intel/openvino/bin/setupvars.sh && \
    echo "OpenVINO environment setup completed." && \
    /start.sh --log-level debug --access-log
