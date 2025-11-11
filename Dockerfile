# hadolint global ignore=DL3041,DL3013,DL4006
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.9.20251110.1@sha256:c929105619fbc4cb4cb2d0667a02b549a3408be98e89d9c61437ca702d04d829

WORKDIR /app
COPY . /app

RUN dnf install -y python3.11 python3.11-pip; \
    pip3.11 install --no-cache-dir -r requirements.in; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
