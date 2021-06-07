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

You will need VS Code with Remote - Containers extension installed. (https://code.visualstudio.com/download)

1.  #### Launch this repo as a Remote - Container in VS Code
    In VSCode, execute command 'Remote-Containers: Rebuild and Reopen in Container' through the Command Palette

1.  #### Launch Rasa core/nlu server
    In VSCode 'Run and Debug' tab, select 'rasa run' and click Start Debugging.

    Note: The actions server does not launch automatically with the core/nlu server. You need to manually start the action server as well. Your bot will still work but actions will not execute.

1.  #### Launch to Rasa actions server
    In VSCode 'Run and Debug' tab, select 'rasa run actions' and click Start Debugging.
