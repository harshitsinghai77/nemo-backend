#!/bin/bash
# Pafy cannot be added using poetry because of some weird conflicts.
# use condition logic to manually add the library in requirements.txt if not already exists.

#NOTE: Pafy is not longer needed for the project. Removed dependency from Pafy and 
# moved to YoutubeDL. This code is just for reference if needed in the future.

out=$(tail -n 1 requirements.txt)
library="git+https://github.com/mps-youtube/pafy.git"

if [ "$out" = "$library" ]; then
    echo "$library already exists"
else
    echo "Adding $library"
    echo $library >> requirements.txt
fi