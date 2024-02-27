# hadolint global ignore=DL3041,DL3013,DL4006
FROM amazonlinux:2023@sha256:db247dc601fcaa65b35d1074f4f34c8f31552ccd185a4002ffa152965e499c61

WORKDIR /app
COPY . /app

RUN dnf update -y; \
    dnf upgrade -y; \
    dnf install -y python3.11; \
    dnf clean all

RUN curl -sL https://bootstrap.pypa.io/get-pip.py | python3.11 - ; \
    python3.11 -m pip install --no-cache-dir -r requirements.in

RUN python3.11 main.py --loaddata

ENTRYPOINT ["python3.11", "main.py"]
