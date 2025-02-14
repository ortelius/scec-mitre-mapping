# hadolint global ignore=DL3041,DL3013,DL4006
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.6.20250211.0@sha256:929dfd2e99503e4b15b9a921cdcd395a0bc9586523eb3e599e7393e0cb78a8eb

WORKDIR /app
COPY . /app

RUN dnf install -y python3.11 python3.11-pip; \
    pip3.11 install --no-cache-dir -r requirements.in; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
