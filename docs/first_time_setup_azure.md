# First time setup

The very first time you go to build this application in production for Azure you will need to do the following

1. Start setup by ssh'ing to your VM and adding the proper credentials to run the app
    1. SSH into the vm

        ```bash
        ssh -i key.pem <name>@<public_ip_address>
        ```

    2. Run through the commands in the bash script [`setup.sh`](setup.sh) in this docs dir

2. Run `source ~/.profile` to update env vars (if `echo $DOMAIN` isn't set)

3. Optionally, create a DNS record that points to the VM's public IP address
4. SSH to the VM and set the desired basic auth user and password to protect the API endpoints - [caddy docs](https://caddyserver.com/docs/caddyfile/directives/basicauth)

    ```bash
    # something like this...
    echo "export BASIC_AUTH_USER=$<value>" >> ~/.profile
    echo "export BASIC_AUTH_PASS=$<hashed_value>" >> ~/.profile # see caddy docs above for hashed value
    ```

5. Make sure to add both the basic auth values you set above as encrypted secrets in the cloudflare workers as well!
6. Start your container stack `script/deploy`

## Basic Auth Note

The `BASIC_AUTH_PASS` value you export in Caddy is a hashed value resulting from the `caddy hash-password` command. You can run this command on your local machine and then copy the hashed value into the `~/.profile` file on the VM.

The actual values you provide when using basic auth is a plaintext version of the `BASIC_AUTH_USER` variable and the original (plaintext) `BASIC_AUTH_PASS` variable

## TLS

If you are using a domain name and have it configured as the DOMAIN env var, then Caddy will attempt to auto-provision a TLS certificate with Let's Encrypt.

You will need to ensure you completed the step above to enable a DNS record pointing to your VM

## GitHub Actions Secrets

There are a few secrets you need to set in GitHub Actions so that our CI/CD pipeline can run:

- SSH_HOST
  - Key: `SSH_HOST`
  - Value: `<public ip address or hostname>`

- SSH_USERNAME
  - Key: `SSH_USERNAME`
  - Value: `<username of the vm user>`

- SSH_KEY
  - Key: `SSH_KEY`
  - Value: `<ssh private key>`

- SSH_PORT
  - Key: `SSH_PORT`
  - Value: `<public port ssh is running on>`
