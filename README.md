# rasa-bot-template
Rasa bot template repository.

# Build steps

## Environment Variables

Set the Telegram bot token and Telegram bot username in .env file.

## Launch with Docker

#### Install Docker
Install docker and docker-compose (see instructions on https://www.docker.com/)

### Quick Launch (no debugging)

```bash
docker-compose up
```

### Launch and Attach (supports debugging)

You will need VS Code with Python extension installed. (https://code.visualstudio.com/download)

1.  #### Sync Rasa source code
    ```bash
    git clone https://github.com/rappo-ai/rasa.git
    ```
    Make sure you sync rasa repository as a sibling folder to mockabot-rasa repository.

1.  #### Build and run the debug Docker image
    ```bash
    docker-compose -f docker-compose.debug.yml up --build
    ```

1.  #### Attach to Rasa SDK server (actions server)
    In VSCode 'Run and Debug' tab, select 'docker attach rasa run actions' and click Start Debugging.

1.  #### Attach to Rasa open-source server (core/nlu server)
    In VSCode 'Run and Debug' tab, select 'docker attach rasa run' and click Start Debugging.
