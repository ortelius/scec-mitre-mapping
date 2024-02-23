FROM amazonlinux:2023

WORKDIR /app

COPY . /app

RUN dnf update -y; \
    dnf upgrade -y; \
    dnf install -y python3.11; \
    rm /usr/bin/python3; \
    ln -s /usr/bin/python3.11 /usr/bin/python3;
RUN python3 -m ensurepip --upgrade; \
    python3 -m pip install --upgrade pip; \
    pip3 install -r requirements.in
RUN python3 main.py --loaddata

ENTRYPOINT ["python3", "main.py"]
