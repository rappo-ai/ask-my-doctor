#!/bin/bash

# Create swapspace
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Setup Firewall
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 8081

# SSH deploy key setup
# tbdrenzil - manually create ~/.ssh/id_gitdeploykey
chmod 600 ~/.ssh/id_gitdeploykey
eval "$(ssh-agent -s)"
touch ~/.ssh/config
echo "Host *
  AddKeysToAgent yes
  IdentityFile ~/.ssh/id_gitdeploykey
" >> ~/.ssh/config
ssh-add ~/.ssh/id_gitdeploykey

# Clone git repo
cd ~
ssh -o "StrictHostKeyChecking no" github.com
git clone git@github.com:rappo-ai/ask-my-doctor.git

# update credentials
# tbdrenzil - manually create ~/ask-my-doctor/.env

# launch docker
cd ~/ask-my-doctor
chmod -R 775 dataset
docker-compose -f docker-compose.base.yml -f docker-compose.yml up --build --force-recreate -d
