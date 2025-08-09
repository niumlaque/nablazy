FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    pipx \
    ffmpeg \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages flask requests yt-dlp

RUN groupadd -g 1000 nablazy && useradd -u 1000 -g nablazy -s /bin/bash -d /home/nablazy nablazy \
    && echo "nablazy ALL=(ALL) NOPASSWD: /bin/chown" >> /etc/sudoers

WORKDIR /app

COPY app/ /app/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && mkdir -p /app/downloads \
    && chown -R nablazy:nablazy /app

USER nablazy

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "app.py"]

