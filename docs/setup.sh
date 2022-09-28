#!/bin/bash

# script configuration - change these values to match your environment
DOMAIN=<string> # the domain to serve traffic with
REPO_DIR=/home/<string>/<string> # the repo to clone and use for the app deployment (no trailing slash)
VM_USER=<string> # the name of the vm user
REPO_NAME=<string> # the name of the repo to clone
ORG_NAME=<string> # the name of the organization to use for the repo

# add dependencies
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install make -y

# install docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
# install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# clone the repo
git clone https://github.com/$ORG_NAME/$REPO_NAME.git $REPO_DIR
sudo chown -R $VM_USER:$VM_USER $REPO_DIR

# firewall connections for ssh
sudo ufw allow 22

# firewall connections for web traffic
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow http
sudo ufw allow https

# enable the firewall
sudo ufw --force enable

# run updates again
sudo apt-get update && sudo apt-get upgrade -y

# switch to the main vm user
sudo -i -u $VM_USER bash << EOF
echo "export DOMAIN=$DOMAIN" >> ~/.profile
(crontab -l ; echo "@reboot $REPO_DIR/script/deploy") | crontab -
EOF

# Add DOMAIN to the root user as well
echo "export DOMAIN=$DOMAIN" >> ~/.profile

echo "bootstrap complete"
