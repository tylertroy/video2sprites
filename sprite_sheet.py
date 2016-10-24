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