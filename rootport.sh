#!/bin/bash
sudo lspci -D -vvv | awk '
/^[0-9a-f:.]+/ {bdf=$1}
/Root Port/ {print bdf}
'
