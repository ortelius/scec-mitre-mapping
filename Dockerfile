# hadolint global ignore=DL3041,DL3013
FROM fedora:41@sha256:cd58e01738fe9d281934c71e47c8e4e605a008bb233436c356bbcbe478149a74

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
