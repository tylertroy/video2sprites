# video2spritegen
A tutorial demonstrating animation techniques for game development using freely-available videos, and software.  

It is commonly said that gameplay is everything but sometimes ugly graphics can detract from an otherwise fun game. As much as we might care to deny, many programmers are bereft of an eye for graphical design. Worse yet, your "classic" graphics in all of their 8-bit pallete glory might actually prevent a would-be player from ever taking the time to give your game a go.

Thankfully in the age of the world wide web, many free graphical resources are available to spruce up your game-play gem. With the help of a little Linux piping and the myriad of free sofwares you can create beautiful sprite-based animations with the stroke of a key or two.

In this tutorial we're going to programatically generate a series of sprites from free-to-use videos and combine them into a sprite sheet for incorporation into your game creations. We'll be using the bash shell in Linux and pygame but these techniques can be adapted to your favorite OS or game development platform. Let's start with the tools you'll need.

## Tools

This tutorial assumes you have the following installed. There are many resources available to guide you their installation processes for the various OSs but I'll leave that in your capable hands. 

* [youtube-dl](https://rg3.github.io/youtube-dl/)
* [ffmpeg](https://www.ffmpeg.org/)
* [imagemagick](http://www.imagemagick.org/script/index.php)
* [gimp](https://www.gimp.org/)
* [python 2.7](https://www.python.org/download/releases/2.7/)
* [pygame](http://pygame.org/)

## Getting the content

First we'll need a video with a nice animation. There is a cornocopia of videos useful for game content, predominantly created for film makers but perfect for our use! Essentially you'll want videos with the graphical content against a single color background. You can find something suitable for your game by searching for the relevant graphical description followed by "green screen" or "black screen". For our example we're going to use the rotating asteroid found [here](https://www.youtube.com/watch?v=63XcV-0ascA).

Let's grab this video with youtube-dl but feel free to get it anyway you like. First navigate to the directory where you want to download the content then execute the following.

```bash
youtube-dl -F https://www.youtube.com/watch?v=63XcV-0ascA
```

The `-F` argument will provide a list of the available formats and their format IDs for that video. I prefer something with high resolution because we can always downscale later so let's go with 137. We indicate the format ID with `-f <code>` and specify an output name with `-o <filename>`.

```bash
youtube-dl -f 137 -o asteroid.mp4 https://www.youtube.com/watch?v=63XcV-0ascA 
```
## Extracting the Frames

Now we will use ffmpeg to extract the frames from the video.

```bash
ffmpeg -i asteroid.mp4 -r 20 asteroid_%03d.png
```

The `-r` argument specifies the rate in Hz which you can think about as fps. The `_%03d` indicates the number of integer digits for file naming so it will be a maximum of 999. You should modify this appropraitely for the number of frames you expect for your video for a given frame rate. In this case 38s at 20fps gives about 720 frames at 1980x720 pixels/frame.

Usually there will be some intro content and in the case of this video, multiple loops so now were going to inspect the frames to work out which ones we should delete to achieve a smooth animation loop.

The first 163 frames containing the intro can be deleted. Now we'll identify the frame range representing one loop.  This is best achieved by opening two image viewers side by side and cycling though one viewer until you find the loop. In our case frames 164 to 273 leaving us with 110 frames. Here's an example frame.

![](https://github.com/tylertroy/video2spritegen/blob/master/asteroid.png "Single Frame")

## Cropping

Because of the aspect ratio much of the content in each frame will be empty and this will represent wasted memory when you use the images in your game. So we're going to crop the content to the minimum size. This again relies on inspection of the frames to work out what crop dimensions will keep all the content in each frame. You should identify the frame containing the widest and longest content and determine the crop dimensions using an image editor such as Gimp. In this case I determined the appropriate dimensions to be 650 width x 836 height at position 663 left, 139 top.

Now let's use imagemagick's convert tool to crop the frames.

```bash
ls *png | sed 's/asteroid//' | xargs -I{} echo convert asteroid{} -crop 650x836+663+139 cropped{} | sh
```
You should inspect the cropped frames to make sure you haven't clipped any of the content. If there is a clipped frame just rerun the above using different dimensions until you get it right. Here's a sample frame cropped.

![](https://github.com/tylertroy/video2spritegen/blob/master/crop.png "Cropped Single Frame")

## Chroma Key

Now we remove the background color to make it transparent again using imagmagick's convert tool. You should first determine the background color in hexadecimal (HTML) notation. I did this with Gimp's color picker tool and found a value of `00fc00`. You should start with a test image, say the first frame. This way you can play with the conditions until you get it right for batch processing.   	

```bash
convert asteroid_164.png -fuzz 40% -transparent \#00fc00 chroma_163.png
```

You can see the result of changing the fuzz factor below, using between 10, and 40 %, from left to right. 

![](https://github.com/tylertroy/video2spritegen/blob/master/chroma_compare.png "Comparison of 10 to 40% fuzz")

You should set a good factor that removes all of the background color in your frames. Once you're happy with the results of the test image you can batch process the chroma keying.

```bash
ls cropped*.png | sed 's/cropped//' | xargs -I{} echo convert cropped{} -fuzz 40% -transparent \\#00fc00 chroma{} | sh
```
## Edge Bluring

You can skip this step if you're happy with the results from the previous step, especially if you plan to significantly reduce the size of each frame. Nevertheless a higher fuzz factor can result in jagged edges that can look a little nasty but we can clean up the edges with some edge bluring. Again it's good to start with a test image to get the right settings before batch processing.

```bash
convert chroma_164.png -alpha set -virtual-pixel transparent -channel A -blur 0x2 -level 50%,100% +channel edge.png
```

The `-blur 0x2` argument defines defines the standard deviation of the gaussian blur as a proportion of the image size. When your set, you can batch process this command.

```bash
ls chroma*.png | sed 's/chroma//' | xargs -I{} echo convert chroma{} -alpha set -virtual-pixel transparent -channel A -blur 0x2 -level 50%,100% +channel edge{} | sh
```
The zoomed image below demonstrates the benefit of edge blurring.

![](https://github.com/tylertroy/video2spritegen/blob/master/edge_compare.png "With and Without Edge Blurring")

## Resize & Frame Rate

At this stage we have still have 110 frames totalling 42MB which is likely too large for a single graphical element in your game so we can reduce our image size and remove every nth element to have fewer total frames. Let's start with resizing. It is nice to start with big images because larger images resample better upon scaling. This is easily achieved with our old friend imagemagick. 

```bash
ls edge*.png | sed 's/edge//' | xargs -I{} echo convert edge{} -resize 30% scaled{} | sh
```

You should scale your image to the appropriate size for your application by modifying the -resize 30% term. This significanly reduces our set size to 6.3 MB. we still have 110 frames which might be a bit excessive so we can remove every nth frame. This may not be suitable for your animation, it all depends on what you're going for.

```bash
ls scaled*.png | awk 'NR % 2 == 1 { print }' | xargs rm
```

Here we are removing every 2nd frame. For every 3rd frame you would use `3 == 1`, etc. This leaves us with 55 items for 3MB in total. A much more reasonable size for a game element. Here's an example of the finished product.

![](https://github.com/tylertroy/video2spritegen/blob/master/scaled.png "final example")

## Generate Sprite Sheet

Finally we should combine these frames into a single sprite sheet because loading 55 files (let alone many animated elements) will be slow! To generate a sprite sheet we can use imagemagick's montage tool.

```bash
montage scaled*.png -tile 1x55 -geometry 195x251+0+0 -background transparent "asteroid_195x(251x55).png"
```

Here we create a sprite sheet of 1 row and 55 columns where the dimension of each image specified as 195 width and 251 height. It's useful to indicate the size of each sprite in the sheet in the file name so you don't have to work it out later. Once you've created the sprite sheet you can delete all the other frames you created along the way.

```bash
rm *_???.png
```

## Putting it All Together

```bash
# Download Video
youtube-dl -f 137 -o asteroid.mp4 https://www.youtube.com/watch?v=63XcV-0ascA

# Extract Frames
ffmpeg -i asteroid.mp4 -r 20 asteroid_%03d.png

# Crop frames
ls *png | sed 's/asteroid//' | xargs -I{} echo convert asteroid{} -crop 650x836+663+139 cropped{} | sh

# Chroma Key Frames
ls cropped*.png | sed 's/cropped//' | xargs -I{} echo convert cropped{} -fuzz 40% -transparent \\#00fc00 chroma{} | sh

# Blur up the edges (optional)
ls chroma*.png | sed 's/chroma//' | xargs -I{} echo \
convert chroma{} -alpha set -virtual-pixel transparent -channel A -blur 0x2 -level 50%,100% +channel edge{} | sh

# Rescale
ls edge*.png | sed 's/edge//' | xargs -I{} echo convert edge{} -resize 30% scaled{} | sh

# Remove every nth frame
ls scaled*.png | awk 'NR % 2 == 1 { print }' | xargs rm 

# Generate sprite sheet
montage scaled*.png -tile 1x55 -geometry 195x251+0+0 -background transparent "asteroid_195x(251x55).png"

# Remove working frames
rm *_???.png
```

## Using your sprites in a your Game

Here is a basic example using our animation sprite sheet with pygame. The SpriteSheet class is merely a convenient way to cycle through each frame of the sprite sheet. I also included another graphical element I created using the same technique. If you did not download this new element `'bluering_95x(114x150).png'` you should remove the lines marked ###. 

```python
import pygame
import itertools
import os
import sys
from numpy import linspace

class SpriteSheet(pygame.sprite.Sprite):
    def __init__(self, sheet_path, unit_height):
       """ Sprite sheet enables stepping between frames"""
       pygame.sprite.Sprite.__init__(self)
       self.image = pygame.image.load(sheet_path)
       self.image = pygame.Surface.convert_alpha(self.image)
       self.unit_height = unit_height
       self.rect = self.image.get_rect()
       self.draw_area = pygame.Rect((0, 0, self.image.get_width(), \
           unit_height))
    def update(self):
        """ Return the next sub rect for current frame. 
        """
        if self.draw_area.top < self.image.get_height() - self.unit_height:
            self.draw_area.top += self.unit_height
        else:
            self.draw_area.top = 0
    def draw(self, surface):
        """ Blit current frame defined by self.draw_area to surface. 
        """
        surface.blit(self.image, self.rect, self.draw_area) 

if __name__ == '__main__':
    pygame.init()

    size = width, height = 1280, 700
    speed = [1, 1]
    black = 0, 0, 0

    screen = pygame.display.set_mode(size)

    asteroid = SpriteSheet('asteroid_195x(251x55).png', unit_height=251)
    bluering = SpriteSheet('bluering_95x(114x150).png', unit_height=114) ###
    asteroid.rect.topleft = (50, 50)
    bluering.rect.topleft = (400, 50) ###

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()
        screen.fill(black)
        
        asteroid.update()
        bluering.update() ###
        
        asteroid.draw(screen)
        bluering.draw(screen) ###
        
        pygame.display.flip()
        pygame.time.wait(25)
```

## A note for Windows users

All of the programs and libraries I have used here (youtube-dl, imagemagick, ffmpeg, gimp, python, pygame) are freely-available for windows however the batch processing commands using Linux piping, `|`, wont work in `cmd.exe`. There is probabably a way to achieve similar results in Windows' Powershell but I'm not familiar enough with that to provide a good solution here. If anyone feels like forking a windows adapted version of this tutorial that would be great! Alternatively you can try installing Linux, you won't be disappointed! 
