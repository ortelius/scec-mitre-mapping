# hadolint global ignore=DL3041,DL3013,DL4006
FROM amazonlinux:2023@sha256:5478f82c47e435ed988fa12a00b623ef3c920fadd669d40c596249cf81960c4c

WORKDIR /app
COPY . /app

RUN dnf install -y --releasever 2023.4.20240416 python3.11; \
    curl -sL https://bootstrap.pypa.io/get-pip.py | python3.11 - ; \
    python3.11 -m pip install --no-cache-dir -r requirements.in; \
    dnf update -y --releasever 2023.4.20240416; \
    dnf upgrade -y --releasever 2023.4.20240416; \
    dnf clean all

ENTRYPOINT ["python3.11", "main.py"]
