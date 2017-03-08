#!/usr/bin/env bash

base="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $base/env-setup.sh

log "[Init]: Ensuring programs are executable..."
chmod +x $base/*.sh

set -e
set -u

log "[Init]: Installing common dependencies..."

update_packages
install_packages wget unzip jq