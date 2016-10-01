# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *

import random

import numpy as np
import pygame

state = {}
screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

state['running'] = False
state['index'] = 0

def startingBlank():
    global lifeDict
    
    lifeDict = np.tile(0, (cell_width,cell_height))
    
def startingGridRandom():
    global lifeDict
    
    lifeDict = np.random.randint(0,2,(cell_width,cell_height))

def startingGosperGliderGun():
    global lifeDict
    
    lifeDict[5,15] = 1
    lifeDict[5,16] = 1
    lifeDict[6,15] = 1
    lifeDict[6,16] = 1

    lifeDict[15,15] = 1
    lifeDict[15,16] = 1
    lifeDict[15,17] = 1
    lifeDict[16,14] = 1
    lifeDict[16,18] = 1
    lifeDict[17,13] = 1
    lifeDict[18,13] = 1
    lifeDict[17,19] = 1
    lifeDict[18,19] = 1
    lifeDict[19,16] = 1
    lifeDict[20,14] = 1
    lifeDict[20,18] = 1
    lifeDict[21,15] = 1
    lifeDict[21,16] = 1
    lifeDict[21,17] = 1
    lifeDict[22,16] = 1

    lifeDict[25,13] = 1
    lifeDict[25,14] = 1
    lifeDict[25,15] = 1
    lifeDict[26,13] = 1
    lifeDict[26,14] = 1
    lifeDict[26,15] = 1
    lifeDict[27,12] = 1
    lifeDict[27,16] = 1
    lifeDict[29,11] = 1
    lifeDict[29,12] = 1
    lifeDict[29,16] = 1
    lifeDict[29,17] = 1

    lifeDict[39,13] = 1
    lifeDict[39,14] = 1
    lifeDict[40,13] = 1
    lifeDict[40,14] = 1

def startingRpentomino():
    global lifeDict
    
    lifeDict[28,12] = 1
    lifeDict[29,12] = 1
    lifeDict[27,13] = 1
    lifeDict[28,13] = 1
    lifeDict[28,14] = 1

def startingDiehard():
    global lifeDict
    
    lifeDict[16,5] = 1
    lifeDict[17,5] = 1
    lifeDict[17,6] = 1
    lifeDict[21,6] = 1
    lifeDict[22,6] = 1
    lifeDict[23,6] = 1
    lifeDict[22,4] = 1
 
def startingAcorn():
    global lifeDict
    
    lifeDict[12,10] = 1
    lifeDict[13,10] = 1
    lifeDict[13,8] = 1
    lifeDict[15,9] = 1
    lifeDict[16,10] = 1
    lifeDict[17,10] = 1
    lifeDict[18,10] = 1

patternsList = {
    0: {'name': 'Random', 'function': startingGridRandom},
    1: {'name': 'Gosper Glider Gun', 'function': startingGosperGliderGun},
    2: {'name': 'R-pentomino', 'function': startingRpentomino},
    3: {'name': 'Die-hard', 'function': startingDiehard},
    4: {'name': 'Acorn', 'function': startingAcorn},
    5: {'name': 'Blank', 'function': startingBlank}
}

window_width = 320
window_height = 240-30
cell_size = 5

cell_width = window_width / cell_size
cell_height = window_height / cell_size

lifeDict = None

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
    global lifeDict
    
    state['index'] = (state['index'] - 1) % len(patternsList)
    startingBlank()
    patternsList[state['index']]['function']()
   
def next_pattern():
    global lifeDict
    
    state['index'] = (state['index'] + 1) % len(patternsList)
    startingBlank()
    patternsList[state['index']]['function']()

def reset():
    global lifeDict
    
    startingBlank()
    patternsList[state['index']]['function']()

@touch(size=(320, 240-30), align="top")
def on_touch(xy):
    if state['running']:
        state['running'] = False
        
    mx,my = [xy[i]/cell_size for i in range(2)]
    
    lifeDict[mx,my] = 1

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
    
def drawGrid():
    for x in range(0, window_width, cell_size):
        screen.line(start_xy=(x,0), end_xy=(x,window_height), color='grey')
        
    for y in range (0, window_height, cell_size):
        screen.line(start_xy=(0,y), end_xy=(window_width, y), color='grey')

def colourGrid():
    global lifeDict
    
    pixel_surface = pygame.surfarray.make_surface(lifeDict)
    pixel_surface.set_palette([(255, 255, 255), (221, 221, 221)])
    scaled_surface = pygame.transform.scale(pixel_surface, (cell_width*cell_size, cell_height*cell_size))
    
    screen.image(scaled_surface, align='top')

def iterate():
    global lifeDict
    
    lifeDict_N = (lifeDict[0:-2,0:-2] + lifeDict[0:-2,1:-1] + lifeDict[0:-2,2:] +
         lifeDict[1:-1,0:-2]                + lifeDict[1:-1,2:] +
         lifeDict[2:  ,0:-2] + lifeDict[2:  ,1:-1] + lifeDict[2:  ,2:])

    birth = (lifeDict_N==3) & (lifeDict[1:-1,1:-1]==0)
    survive = ((lifeDict_N==2) | (lifeDict_N==3)) & (lifeDict[1:-1,1:-1]==1)
    lifeDict[...] = 0
    lifeDict[1:-1,1:-1][birth | survive] = 1
    
    return lifeDict
      
def showMain():
    global lifeDict
    
    if lifeDict is None:
        return
    
    if state['running']:
        lifeDict = iterate()

    colourGrid()
    drawGrid()
    
    screen.rectangle(
        color='black',
        size=(320, 30),
        align='bottom',
    )
    
    if state['running']:
        startStop = 'Stop'
    else:
        startStop = 'Start'
    
    screen.text(
        startStop,
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
        patternsList[state['index']]['name'],
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
    
    startingBlank()
    patternsList[state['index']]['function']()
    
    colourGrid()
    drawGrid()

@every(seconds=1.0/30)
def loop():

    if state['screen'] == 'main':
        showMain()
        
tingbot.run()