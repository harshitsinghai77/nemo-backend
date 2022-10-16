#!/bin/bash
# Pafy cannot be added using poetry because of some weird conflicts.
# use condition logic to manually add the library in requirements.txt if not already exists.

out=$(tail -n 1 requirements.txt)
library="git+https://github.com/mps-youtube/pafy.git"

if [ "$out" = "$library" ]; then
    echo "$library already exists"
else
    echo "Adding $library"
    echo $library >> requirements.txt
fi