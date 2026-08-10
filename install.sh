#!/bin/bash
set -euo pipefail

sudo apt update    # to hide output and error
sudo apt upgrade -y 
  

if ! command -v git &> /dev/null; then
    sudo apt install git -y 
fi

if ! command -v docker &> /dev/null; then
    sudo apt install docker.io docker-compose -y 
    sudo usermod -aG docker $USER
    newgrp docker
    sudo systemctl enable docker 
    sudo systemctl start docker
    if systemctl is-active --quiet docker; then
      echo "Docker is Running..."
    else
      echo "Docker not Running.... and Exiting..."
      exit 1
    fi
fi

