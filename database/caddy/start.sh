#!/bin/bash

set -e

if [ -z "$DOMAIN" ]
then
    # If DOMAIN is blank, set to localhost
    # Note: in prod, domain will be the actual domain
    export DOMAIN="localhost"
fi

if [ -z "$BASIC_AUTH_USER" ]
then
    # If BASIC_AUTH_USER is blank, set to dev
    # Note: in prod, this will be set to a secret
    export BASIC_AUTH_USER="dev"
fi

if [ -z "$BASIC_AUTH_PASS" ]
then
    # If BASIC_AUTH_PASS is blank, set to dev
    # Note: in prod, this will be set to a secret
    export BASIC_AUTH_PASS="JDJhJDE0JEVwV1dLWHYxVFhsLlF6RG1hM0M3YWVaS2xJUzRLaHVwZXFVaTFqNTRDMUdSc09VRzJQVU95" # 'caddy hash-password' of "dev"
fi

caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
