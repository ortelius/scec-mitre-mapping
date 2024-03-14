# hadolint global ignore=DL3041,DL3013,DL4006
FROM amazonlinux:2023@sha256:6ef0881ab074946ab8d1d68a56f3cae2c6f16b5885737601ff8a9325f806780e

WORKDIR /app
COPY . /app

RUN dnf install -y python3.11; \
    curl -sL https://bootstrap.pypa.io/get-pip.py | python3.11 - ; \
    python3.11 -m pip install --no-cache-dir -r requirements.in; \
    dnf update -y; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["python3.11", "main.py"]
