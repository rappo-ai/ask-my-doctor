FROM rappoai/rasa:telegram

USER root

RUN apt-get update && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y --no-install-recommends \
    sudo \
    ssh \
    git \
    nodejs && \
    . /opt/venv/bin/activate && \
    pip install black

USER 1001
