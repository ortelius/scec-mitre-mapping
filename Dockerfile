# hadolint global ignore=DL3041,DL3013,DL4006
FROM amazonlinux:2023@sha256:ef9435f95b6fc5e7fd9ea156499e62a86f770d9928dfc83ecaa74af4fac3a663

WORKDIR /app
COPY . /app
RUN dnf update -y; \
    dnf install -y findutils; \
    dnf clean all
RUN find / -name mitre.joblib -print

RUN dnf install -y python3.11; \
    curl -sL https://bootstrap.pypa.io/get-pip.py | python3.11 - ; \
    python3.11 -m pip install --no-cache-dir -r requirements.in; \
    dnf update -y; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["python3.11", "main.py"]
