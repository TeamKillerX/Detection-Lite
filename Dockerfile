FROM rendyprojects/python:latest

RUN apt -qq update && \
    apt -qq install -y --no-install-recommends ffmpeg \
    curl \
    git \
    gnupg2 \
    unzip \
    wget \
    python3-pip \
    ffmpeg \
    neofetch && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/

WORKDIR /usr/src/app
COPY . .
RUN pip3 install --upgrade pip setuptools==59.6.0
RUN pip3 install -r requirements.txt

RUN chmod -R 777 /usr/src/app

CMD ["bash", "-c", "python3 -m Detection"]
