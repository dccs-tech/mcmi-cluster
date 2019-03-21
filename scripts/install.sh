#!/usr/bin/env bash
#
# Install cluster management related packaging
#
TERRAFORM_VERSION=0.12.0-alpha4
wget -nv https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip -o terraform_${TERRAFORM_VERSION}_terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/local/bin \
    && rm -f terraform_${TERRAFORM_VERSION}_terraform_${TERRAFORM_VERSION}_linux_amd64.zip