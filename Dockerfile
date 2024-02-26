# hadolint global ignore=DL3041,DL3013
FROM amazonlinux:2023@sha256:d8323b3ea56d286d65f9a7469359bb29519c636d7d009671ac00b5c12ddbacf0

WORKDIR /app
COPY . /app

RUN dnf update -y; \
    dnf upgrade -y; \
    dnf install -y python3.11; \
    dnf clean all; \
    rm /usr/bin/python3; \
    ln -s /usr/bin/python3.11 /usr/bin/python3;
RUN python3 -m ensurepip --upgrade; \
    pip3 install --no-cache-dir --requirement requirements.in

ENTRYPOINT ["python3", "main.py"]
