# hadolint global ignore=DL3041,DL3013,DL4006
FROM amazonlinux:2023@sha256:860843fc1dcf21cb06ce7a5cd0a6da92e9cb76bb8e0d1517fd93b6b8e2fa31bc

WORKDIR /app
COPY . /app

RUN dnf install -y python3.11; \
    curl -sL https://bootstrap.pypa.io/get-pip.py | python3.11 - ; \
    python3.11 -m pip install --no-cache-dir -r requirements.in; \
    dnf update -y; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["python3.11", "main.py"]
