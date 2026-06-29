#!/usr/bin/env bash

set -euo pipefail

# This script should be run directly from the online repository like this:
# curl -L https://github.com/eyalbor/dotfiles/raw/main/online_install.sh | bash
#
# Prerequisits:
# sudo apt-get install curl

cd ~

# mac comes with a built-in git
if [ "$(uname -s)" != "Darwin" ]; then
  echo "========================================"
  echo "Installing git"
  sudo apt-get install git
fi

repo_root="https://github.com/eyalbor/dotfiles"
if [ "$1" == "use-ssh" ]; then
  repo_root="git@github.com:eyalbor/dotfiles"
fi

echo "========================================"
echo "Cloning dotfiles"
git clone $repo_root .dotfiles

echo "========================================"
echo "Installing"
cd ~/.dotfiles
./bootstrap.sh
