# hadolint global ignore=DL3041,DL3013,DL4006
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.9.20251105.0@sha256:b0f8d1179ea5555f33163cbd33ad91ac5c553d334da210741171fa5e40cbefa9

WORKDIR /app
COPY . /app

RUN dnf install -y python3.11 python3.11-pip; \
    pip3.11 install --no-cache-dir -r requirements.in; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
