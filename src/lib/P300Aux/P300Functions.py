# P300Functions.py
# Copyright (C) 2009  Matthias Treder
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
P300Functions.py

Provides some convenient functions when using a P300 speller.
These functions cover the following topics:
- checking keyboard input
- presenting a graphical (numbers) or auditory countdown
- displaying messages, fading, zooming images, and clearing the screen
- setting & randomizing states
- producing flash sequences

Many of these functions use pygame

"""


import pygame

from lib.P300VisualElement.Textbox import Textbox


" *** Interfacing with the keyboard *** "

def check_key():
    """
    Checks if a key was hit, if yes return the key. The first key
    will be returned if multiple keys were hit
    """
    for event in pygame.event.get():
        if event.type is (pygame.KEYDOWN):
            return event.key 
    return None


def wait_for_key():
    """
    Similar to check key, but if no key was pressed, the 
    function waits for key input
    """   
    pygame.event.clear()            # Clear the old events
    while 1:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type is (pygame.KEYDOWN):
                return event.key

# ****************************
# Graphical and auditory countdown
# ****************************

def countdown(self, centerxy, screen, start_time=3):
    """
    Presents a countdown, starting by start_time in seconds.
    If a centerxy is not provided, the object will be centered 
    on the screen center.
    """
    font = pygame.font.Font(None, self.textsize)
    for i in range(start_time):
        # Get number and back background
        nr = font.render(str(start_time - i), True, self.textcolor)
        rect = nr.get_rect(center=centerxy)
        back = pygame.Surface((rect.width, rect.height))
        # Paint background and number 
        back.fill(self.bgcolor)
        screen.blit(back, back.get_rect(center=centerxy))
        screen.blit(nr, rect)
        pygame.display.flip()
        pygame.time.wait(1000)

def OLD_auditory_countdown(sound, nr_beeps=3):
    """
    Presents an auditory countdown, giving nr_beeps beeps in
    1 second intervals.As sound, provide an instance of
    pygame.Sound
    """
    for i in range(nr_beeps):
        sound.play()
        pygame.time.wait(1000)


# **************************
# Displaying messages
# & some graphics FX
# **************************

def show_message(self, text, box=False):
    """
    Uses pygame to puts text on the screen. Optionally, the size and color
    of the message can be provided. The text will be centered.
    If box is false, text will be a single line, otherwise it will be presented
    in a textbox
    """
    if not box:
        self.screen.blit(self.background, self.background_rect)
        font = pygame.font.Font(None, self.textsize)
        textimage = font.render(text, True, self.textcolor);
        textrect = textimage.get_rect(center=(self.screenWidth / 2, self.screenHeight / 2))
        self.screen.blit(textimage, textrect)
        pygame.display.flip()
    else:
        edgecolor = 100, 100, 255
        boxsize = (500, 300)
        textbox = Textbox(pos=(self.screenWidth / 2, self.screenHeight / 2), text=text, textsize=self.textsize, size=boxsize, edgecolor=edgecolor)
        textbox.refresh()
        self.screen.blit(self.background, self.background_rect)
        self.screen.blit(textbox.image, textbox.rect)
        pygame.display.flip()
    
def fadeout_message(self, text, box=False, opts=None):
    """
    A fancy fading-out message. 
    You can provide options in form of a dictionary:
    * "show_time" : how long the text is displayed before fadeout
    * "fadeout_time" : how long the fadeout takes
    * "wait_for_key" : waits for key-press before fadeout (in this case, 
        the value in show_time is not used)
    * "textsize", "textcolor" - size and color of text
    """
    back, TRANSPARENT = None, (1, 2, 3)
    show_time, fadeout_time, wait_for_key = 1500, 500, False
    textsize = self.textsize
    textcolor = self.textcolor
    if opts is not None:
        if opts.has_key("show_time"): show_time = opts["show_time"]
        if opts.has_key("fadeout_time"): fadeout_time = opts["fadeout_time"]
        if opts.has_key("wait_for_key"): wait_for_key = opts["wait_for_key"]
        if opts.has_key("textsize"): textsize = opts["textsize"]
        if opts.has_key("textcolor"): textcolor = opts["textcolor"]
    textimage, textrect = None, None
    if not box:
        font = pygame.font.Font(None, textsize)
        textimage = font.render(text, True, textcolor);
        textrect = textimage.get_rect(center=(self.screenWidth / 2, self.screenHeight / 2))
    else:
        edgecolor = 100, 100, 255
        boxsize = (500, 300)
        textbox = Textbox(pos=(self.screenWidth / 2, self.screenHeight / 2), text=text, textsize=textsize, size=boxsize, edgecolor=edgecolor)
        textbox.refresh()
        textimage = textbox.image
        textrect = textbox.rect
    # Make a transparent back upon which the text is set (otherwise transparency fails)
    back = pygame.Surface((textrect.width, textrect.height))
    back.fill(TRANSPARENT)
    back.set_colorkey(TRANSPARENT)
    back.blit(textimage, (0, 0, textrect.width, textrect.height))
    
    self.screen.blit(self.background, [0, 0])
    self.screen.blit(back, textrect)
    pygame.display.flip()
    if wait_for_key: self.wait_for_key()
    else: pygame.time.delay(show_time)
    
    current_time = pygame.time.get_ticks() 
    end_time = current_time + fadeout_time
    # Start fading out in 50 ms steps
    while current_time < end_time:
        fade = 255 * (end_time - current_time) / fadeout_time   # Fading value 255 - 0
        back.set_alpha(round(fade))
        #bef = pygame.time.get_ticks()
        self.screen.blit(self.background, [0, 0])
        #aft = pygame.time.get_ticks()
        #print "Time :",str(aft-bef)
    
        self.screen.blit(back, textrect)
        pygame.display.flip()
        pygame.time.delay(50)
        current_time = pygame.time.get_ticks()
    
    self.screen.blit(self.background, [0, 0])
    pygame.display.flip()
        
def fade_image(self, surface, rect, fade_time=1000, fade_in=True, transparent=(1, 2, 3)):
    """
    Fades the image that is given by the surface and the rect (the latter specifies
    where it is to be put on the screen). If you want to fade a whole display 
    consisting of multiple objects, you should use the pygame.blit method to
    blit it onto a single surface and provide this surface here.
    Note that the color (1,2,3) is used for transparency here, so if you use
    this color it will become transparent. You can reset the transparent color
    in these cases.
    If fade_in is set to false, the object is faded out.
    Note: This method is VERY slow with DOUBLEBUF.
    """
    # Make a transparent back upon which the text is set (otherwise transparency fails)
    back = pygame.Surface((rect.width, rect.height))
    back.fill(transparent)
    back.set_colorkey(transparent)
    back.blit(surface, (0, 0, rect.width, rect.height))
    #back.convert()

    current_time = pygame.time.get_ticks() 
    end_time = current_time + fade_time
    # Fade in 50 ms steps
    #cnt=0            # Count the number of iterations through the loop
    while current_time < end_time:
        if fade_in:
            fade = 255 * (1 - (end_time - current_time) / float(fade_time))   # Fade in
        else:
            fade = 255 * (end_time - current_time) / float(fade_time)   # Fade out
        back.set_alpha(round(fade))
        self.screen.blit(self.background, [0, 0])
        #bef = pygame.time.get_ticks()
        self.screen.blit(back, rect)
        #aft = pygame.time.get_ticks()
        pygame.display.flip()
        self.clock.tick(self.fps)
        current_time = pygame.time.get_ticks()
         
def fade_and_zoom(self, surface, start_rect, end_rect, anim_time=1000, fade_in=True, transparent=(1, 2, 3)):
    """
    Fades and zooms/scales the image given by surface at the same time. start_rect
    specifies the rect (position, size) of the object in the beginning and end_rect
    in the end of the operation.
    If you want to fade-zoom a whole display consisting of multiple objects, you 
    should use the pygame.blit method to blit it onto a single surface and provide 
    this surface here.
    Note that the color (1,2,3) is used for transparency here, so if you use
    this color it will become transparent. You can reset the transparent color
    in these cases.
    If fade_in is set to false, the object is faded out.
    Note: This method is VERY slow with DOUBLEBUF.
    """
    # Make a transparent back upon which the text is set (otherwise transparency fails)
    image_rect = surface.get_rect()
    back = pygame.Surface((image_rect.width, image_rect.height))
    back.fill((0, 0, 0))
    back.fill(transparent)
    back.set_colorkey(transparent)
    back.blit(surface, image_rect)

    f = 0          # Gives how many percent/what fraction of the animation is finished  
    start_time = current_time = pygame.time.get_ticks() 
    # Fade in 20 ms steps
    while current_time < start_time + anim_time:
        f = (current_time - start_time) / float(anim_time)
        fade = (255 * f if fade_in else 255 * (1 - f))
        back.set_alpha(round(fade))
        # Get new rect
        left, top = int(f * end_rect.left + (1 - f) * start_rect.left), int(f * end_rect.top + (1 - f) * start_rect.top)
        width, height = int(f * end_rect.width + (1 - f) * start_rect.width), int(f * end_rect.height + (1 - f) * start_rect.height)
        new_rect = pygame.Rect(left, top, width, height)
        # Get new surface version
        new_back = pygame.transform.smoothscale(back, (width, height)) 
        # Paint everything
        self.screen.blit(self.background, [0, 0])
        self.screen.blit(new_back, new_rect)
        pygame.display.flip()
        self.clock.tick(self.fps)
        current_time = pygame.time.get_ticks()

def clear_screen(self):
    """
    Fills the screen with the background color 
    """
    self.screen.blit(self.background, [0, 0])
    pygame.display.flip()

# *************
# Manipulate states
# *************

def reset_states(self):
    """ Resets all elements to their default state (state 0) """
    for element in self.elements: element.state = 0

def randomize_states(self):
    """ Sets each elements into a random state """
    for element in self.elements: element.update(random.randint(0, element.nr_states - 1))

#  ***************
# Make flash sequences 
# ****************

def random_flash_sequence(self, set=None, min_dist=0, seq_len=None, repetition=False):
    """
    Generates a random sequence of flashes. If flash_sequence is not 
    empty, min_dist is taken into account for the previously included elements.
    The new sequence is appended to flash_sequence.
    * set 
        provide a list of indices of groups on which the sequence is 
        to be based. If None, all existing groups are taken
    * min_dist  
        the minimum number of intermediate flashes between two flashes 
        of the same element
    * repetition
        if true, groups are drawn with repetition (ie, indices can be repeated) 
    """
    if set is None:
        set = range(len(self.groups))       # Take all groups
    if seq_len is None:
        seq_len = len(set)                  # If no argument provided, take length of sequence

    for i in range(seq_len):
        subset = set[:]         # Give a copy of set (otherwise they both reference the same list)
        # Find the no go's (indices which were used in the 
        # previous sequence and can't be used now) and remove them
        for j in range(min_dist):
            if len(self.flash_sequence) > j:           
                try:        # if element is not in the subset, an exception is cast 
                    subset.remove(self.flash_sequence[ - 1 - j])
                except:
                    pass
        # From the remaining subset, randomly chose element and append to sequence
        e = self.random.sample(subset, 1)
        e = e[0]                # Element is a list, use [0] to unpack it
        self.flash_sequence.append(e)
        # If no repetitions, remove this element from sets
        if not repetition: set.remove(e)