# hadolint global ignore=DL3041,DL3013,DL4006
FROM amazonlinux:2023@sha256:d8323b3ea56d286d65f9a7469359bb29519c636d7d009671ac00b5c12ddbacf0

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
