# hadolint global ignore=DL3041,DL3013,DL4006
FROM public.ecr.aws/amazonlinux/amazonlinux:2023.4.20240429.0@sha256:bcb8bd282c38fa8c58369bd217d25b5f8fbd760c663660c8c630189b988f5d97

WORKDIR /app
COPY . /app

RUN dnf install -y python3.11; \
    curl -sL https://bootstrap.pypa.io/get-pip.py | python3.11 - ; \
    python3.11 -m pip install --no-cache-dir -r requirements.in; \
    dnf update -y; \
    dnf upgrade -y; \
    dnf clean all

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
