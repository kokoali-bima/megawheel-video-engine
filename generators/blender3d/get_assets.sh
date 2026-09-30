#!/usr/bin/env bash
# Download third-party CC0 assets used by the Blender 3D mode (not stored in git; see .gitignore).
# Kenney Car Kit 3.1 — CC0 (public domain): https://kenney.nl/assets/car-kit
set -e
cd /root/video-engine
mkdir -p assets/kenney_car_kit && cd assets/kenney_car_kit
if [ ! -f License.txt ]; then
  curl -sSfL -o kit.zip "https://kenney.nl/media/pages/assets/car-kit/1a312ec241-1775131960/kenney_car-kit.zip"
  unzip -q -o kit.zip && rm -f kit.zip
fi
ls "Models/GLB format" | wc -l
