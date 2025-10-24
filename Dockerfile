# hadolint global ignore=DL3041,DL3013,DL4006
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.9.20251020.0@sha256:8b571bc151a30c86f76e7216155e7dcbfff0b5f3fbbd349fd0988ed9ec20af84

WORKDIR /app
COPY . /app

RUN dnf install -y python3.11 python3.11-pip; \
    pip3.11 install --no-cache-dir -r requirements.in; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
