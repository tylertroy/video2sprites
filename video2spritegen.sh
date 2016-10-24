#!/bin/bash

# Download Video
youtube-dl -f 137 -o asteroid.mp4 https://www.youtube.com/watch?v=63XcV-0ascA

# Extract Frames
ffmpeg -i asteroid.mp4 -r 20 asteroid_%03d.png

# Crop frames
ls *png | sed 's/asteroid//' | xargs -I{} echo convert asteroid{} -crop 650x836+663+139 cropped{} | sh

# Chroma Key Frames
ls cropped*.png | sed 's/cropped//' | xargs -I{} echo convert cropped{} -fuzz 40% -transparent \\#00fc00 chroma{} | sh

# Blur up the edges (optional)
ls chroma*.png | sed 's/chroma//' | xargs -I{} echo convert chroma{} -alpha set -virtual-pixel transparent -channel A -blur 0x2 -level 50%,100% +channel edge{} | sh

# Rescale
ls edge*.png | sed 's/edge//' | xargs -I{} echo convert edge{} -resize 30% scaled{} | sh

# Remove every nth frame
ls scaled*.png | awk 'NR % 2 == 1 { print }' | xargs rm 

# Generate sprite sheet
montage scaled*.png -tile 1x55 -geometry 195x251+0+0 -background transparent asteroid_195x(251x55).png

# Remove working frames
rm *_???.png