# hadolint global ignore=DL3041,DL3013
FROM amazonlinux:2023

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
RUN python3 main.py --loaddata

ENTRYPOINT ["python3", "main.py"]
