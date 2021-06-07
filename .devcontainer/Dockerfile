FROM rappoai/rasa:telegram

USER root

RUN apt-get update && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y --no-install-recommends \
    sudo \
    ssh \
    git \
    nodejs && \
    pip install debugpy -t /tmp

USER 1001
