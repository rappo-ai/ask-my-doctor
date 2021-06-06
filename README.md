# ask-my-doctor
AskMyDoctor source code repository.

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

It is recommended to have Python 3.8.5 installed on your system for creating the venv as the Rasa docker image currently uses Python 3.8.5 and you may get strange debugging errors with a different version of Python.

1.  #### Install poetry (Python dependency management tool, installed globally)
    ```bash
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
    ```

1.  #### Sync Rasa source code and switch to Telegram branch
    ```bash
    git clone https://github.com/rappo-ai/rasa.git
    cd rasa
    git checkout telegram
    ```
    Make sure you sync rasa repository as a sibling folder to mockabot-rasa repository.

1.  #### Create a virtual env and activate it
    ```bash
    /path/to/python3.8.5 -m venv ./.venv
    source .venv/bin/activate
    ```

1.  #### Build and install Rasa
    ```bash
    cd rasa
    make install
    ```

1.  #### Build and run the debug Docker image
    ```bash
    cd ask-my-doctor
    docker-compose -f docker-compose.debug.yml up --build
    ```

1.  #### Open the VS Code workspace
    In VSCode, File -> Open Workspace -> /path/to/ask-my-doctor/ask-my-doctor.code-workspace

1.  #### Attach to Rasa SDK server (actions server)
    In VSCode 'Run and Debug' tab, select 'docker attach rasa run actions' and click Start Debugging.

1.  #### Attach to Rasa open-source server (core/nlu server)
    In VSCode 'Run and Debug' tab, select 'docker attach rasa run' and click Start Debugging.
