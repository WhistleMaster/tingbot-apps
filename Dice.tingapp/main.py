import tingbot
from tingbot import *

import random

from time import sleep

state = {}
screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

state['roll'] = False

@right_button.press
def on_rigt():
    roll()

@midleft_button.press
def on_midleft():
    roll()

@midright_button.press
def on_midright():
    roll()
    
@left_button.press
def on_left():
    roll()

def roll():
    state['roll'] = True
    
    state['dice1'] = random.randint(1, 6)
    state['dice2'] = random.randint(1, 6)

def showMain():
    
    screen.fill(color=(57, 101, 74))

    screen.rectangle(
        xy=(0,0),
        align='topleft',
        size=(320,31),
        color='white',
    )
    
    screen.text(
        'Dice Roll',
        xy=(160, 15),
        align='center',
        color='black',
        font='font/Arial Rounded Bold.ttf',
        font_size=18, 
    )
    
    screen.rectangle(
        xy=(320,240),
        align='bottomright',
        size=(320,31),
        color='white',
    )
    
    if state['roll']:
        screen.text(
            "Rolling...",
            xy=(320/2, 240/2+103),
            align='center',
            color='black',
            font='font/Arial Rounded Bold.ttf',
            font_size=18, 
        )
        for x in range(0, 20):
            screen.image("img/%s.png" % random.randint(1, 6), xy=(320/2-70, 240/2), scale=0.8)
            screen.image("img/%s.png" % random.randint(1, 6), xy=(320/2+70, 240/2), scale=0.8)
            screen.update()
            sleep(0.2)
        state['roll'] = False
    
    screen.image("img/%s.png" % state['dice1'], xy=(320/2-70, 240/2), scale=0.8)
    screen.image("img/%s.png" % state['dice2'], xy=(320/2+70, 240/2), scale=0.8)
    
    total = state['dice1'] + state['dice2']

    screen.text(
        total,
        xy=(320/2, 240/2+103),
        align='center',
        color='black',
        font='font/Arial Rounded Bold.ttf',
        font_size=18, 
    )

@once()
def setup():
    
    roll()

@every(seconds=1.0/30)
def loop():
    if 'dice1' not in state or not state['dice1'] or 'dice2' not in state or not state['dice2']:
        screen.fill(color=(57, 101, 74))
        screen.text(
            'Loading...',
            xy=(160, 225),
            font_size=12,
            color='white',
        )
        return
    
    if state['screen'] == 'main':
        showMain()
        
tingbot.run()
