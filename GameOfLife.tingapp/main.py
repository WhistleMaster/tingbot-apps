# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *

import random

import numpy as np
import pygame

life_dict = None

state = {}
screen_list = {
    0: 'main'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

state['running'] = False
state['index'] = 0

def starting_blank():
    global life_dict
    
    life_dict = np.tile(0, (cell_width,cell_height))
    
def starting_grid_random():
    global life_dict
    
    life_dict = np.random.randint(0,2,(cell_width,cell_height))

def starting_gosper_glider_gun():
    global life_dict
    
    life_dict[5,15] = 1
    life_dict[5,16] = 1
    life_dict[6,15] = 1
    life_dict[6,16] = 1

    life_dict[15,15] = 1
    life_dict[15,16] = 1
    life_dict[15,17] = 1
    life_dict[16,14] = 1
    life_dict[16,18] = 1
    life_dict[17,13] = 1
    life_dict[18,13] = 1
    life_dict[17,19] = 1
    life_dict[18,19] = 1
    life_dict[19,16] = 1
    life_dict[20,14] = 1
    life_dict[20,18] = 1
    life_dict[21,15] = 1
    life_dict[21,16] = 1
    life_dict[21,17] = 1
    life_dict[22,16] = 1

    life_dict[25,13] = 1
    life_dict[25,14] = 1
    life_dict[25,15] = 1
    life_dict[26,13] = 1
    life_dict[26,14] = 1
    life_dict[26,15] = 1
    life_dict[27,12] = 1
    life_dict[27,16] = 1
    life_dict[29,11] = 1
    life_dict[29,12] = 1
    life_dict[29,16] = 1
    life_dict[29,17] = 1

    life_dict[39,13] = 1
    life_dict[39,14] = 1
    life_dict[40,13] = 1
    life_dict[40,14] = 1

def starting_rpentomino():
    global life_dict
    
    life_dict[28,12] = 1
    life_dict[29,12] = 1
    life_dict[27,13] = 1
    life_dict[28,13] = 1
    life_dict[28,14] = 1

def starting_diehard():
    global life_dict
    
    life_dict[16,5] = 1
    life_dict[17,5] = 1
    life_dict[17,6] = 1
    life_dict[21,6] = 1
    life_dict[22,6] = 1
    life_dict[23,6] = 1
    life_dict[22,4] = 1
 
def starting_acorn():
    global life_dict
    
    life_dict[12,10] = 1
    life_dict[13,10] = 1
    life_dict[13,8] = 1
    life_dict[15,9] = 1
    life_dict[16,10] = 1
    life_dict[17,10] = 1
    life_dict[18,10] = 1

patterns_list = {
    0: {'name': 'Random', 'function': starting_grid_random},
    1: {'name': 'Gosper Glider Gun', 'function': starting_gosper_glider_gun},
    2: {'name': 'R-pentomino', 'function': starting_rpentomino},
    3: {'name': 'Die-hard', 'function': starting_diehard},
    4: {'name': 'Acorn', 'function': starting_acorn},
    5: {'name': 'Blank', 'function': starting_blank}
}

window_width = 320
window_height = 240-30
cell_size = 5

cell_width = window_width / cell_size
cell_height = window_height / cell_size

life_dict = None

@right_button.press
def on_rigt():
    reset()

@midleft_button.press
def on_midleft():
    previous_pattern()

@midright_button.press
def on_midright():
    next_pattern()
    
@left_button.press
def on_left():
    toggle_running()
    
def previous_pattern():
    global life_dict
    
    state['index'] = (state['index'] - 1) % len(patterns_list)
    starting_blank()
    patterns_list[state['index']]['function']()
   
def next_pattern():
    global life_dict
    
    state['index'] = (state['index'] + 1) % len(patterns_list)
    starting_blank()
    patterns_list[state['index']]['function']()

def reset():
    global life_dict
    
    starting_blank()
    patterns_list[state['index']]['function']()

@touch(size=(320, 240-30), align="top")
def on_touch(xy):
    if state['running']:
        state['running'] = False
        
    mx,my = [xy[i]/cell_size for i in range(2)]
    
    life_dict[mx,my] = 1

@touch(xy=(80,225), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        previous_pattern()
            
@touch(xy=(240,225), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        next_pattern()
    
@touch(xy=(0,227), size=(45,31), align='left')
def on_touch(xy, action):
    if action == 'down':
        toggle_running()
            
@touch(xy=(320,227), size=(45,31), align='right')
def on_touch(xy, action):
    if action == 'down':
        reset()

def toggle_running():
    state['running'] = not state['running']
    
def draw_grid():
    for x in range(0, window_width, cell_size):
        screen.line(start_xy=(x,0), end_xy=(x,window_height), color='grey')
        
    for y in range (0, window_height, cell_size):
        screen.line(start_xy=(0,y), end_xy=(window_width, y), color='grey')

def colour_grid():
    global life_dict
    
    pixel_surface = pygame.surfarray.make_surface(life_dict)
    pixel_surface.set_palette([(255, 255, 255), (221, 221, 221)])
    scaled_surface = pygame.transform.scale(pixel_surface, (cell_width*cell_size, cell_height*cell_size))
    
    screen.image(scaled_surface, align='top')

def iterate():
    global life_dict
    
    life_dict_N = (life_dict[0:-2,0:-2] + life_dict[0:-2,1:-1] + life_dict[0:-2,2:] +
         life_dict[1:-1,0:-2]                + life_dict[1:-1,2:] +
         life_dict[2:  ,0:-2] + life_dict[2:  ,1:-1] + life_dict[2:  ,2:])

    birth = (life_dict_N==3) & (life_dict[1:-1,1:-1]==0)
    survive = ((life_dict_N==2) | (life_dict_N==3)) & (life_dict[1:-1,1:-1]==1)
    life_dict[...] = 0
    life_dict[1:-1,1:-1][birth | survive] = 1
    
    return life_dict
      
def show_main():
    global life_dict
    
    if life_dict is None:
        return
    
    if state['running']:
        life_dict = iterate()

    colour_grid()
    draw_grid()
    
    screen.rectangle(
        color='black',
        size=(320, 30),
        align='bottom',
    )
    
    if state['running']:
        start_stop = 'Stop'
    else:
        start_stop = 'Start'
    
    screen.text(
        start_stop,
        xy=(10,227),
        align='left',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,
    )
    
    screen.image(
        'img/left.png',
        xy=(80, 225),
        align='center'
    )
    screen.image(
        'img/right.png',
        xy=(240, 225),
        align='center'
    )
    
    screen.text(
        patterns_list[state['index']]['name'],
        xy=(160,227),
        align='center',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,
    )
    
    screen.text(
        'Reset',
        xy=(310,227),
        align='right',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,
    )

@once()
def setup():
    screen.fill(color='white')
    
    starting_blank()
    patterns_list[state['index']]['function']()
    
    colour_grid()
    draw_grid()

@every(seconds=1.0/30)
def loop():

    if state['screen'] == 'main':
        show_main()
        
tingbot.run()