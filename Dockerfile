# hadolint global ignore=DL3041,DL3013,DL4006
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.7.20250414.0@sha256:b885fda4d431af6d651ebf90c4c8790add9b1c3bf181d5e8ca559d3d7d64e616

WORKDIR /app
COPY . /app

RUN dnf install -y python3.11 python3.11-pip; \
    pip3.11 install --no-cache-dir -r requirements.in; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
