#!/bin/sh

EXE_DIR=/usr/local/sbin

set -x
sudo cp led /usr/local/sbin
sudo cp led-batt /usr/local/sbin
sudo cp bash_completion.d/* /etc/bash_completion.d
