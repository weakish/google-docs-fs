#!/bin/sh

echo "Moving GData Python Client files to their proper location"
sudo mv /usr/local/lib/dist-packages/gdata* /usr/local/dist-packages
sudo mv /usr/local/lib/atom* /usr/local/dist-packages
