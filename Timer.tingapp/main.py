# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *
import time

import lib.stopwatch
import lib.countdown

state = {}

screenList = {
    0: 'stopwatch',
    1: 'countdown'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

sw = lib.stopwatch.stopwatch()
currentLap = 0

cd = lib.countdown.countdown()

state['text_visible'] = True

@left_button.press
def on_left():
    start_stop()

@midleft_button.press
def on_midleft():
    lap_reset()

@midright_button.press
def on_midright():
    previous_screen()
    
@right_button.press
def on_right():
    next_screen()
    
@touch(xy=(100,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        next_screen()
            
@touch(xy=(220,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        previous_screen()
    
@touch(xy=(0,16), size=(45,31), align='left')
def on_touch(xy, action):
    if action == 'down':
         start_stop()
            
@touch(xy=(320,16), size=(45,31), align='right')
def on_touch(xy, action):
    if action == 'down':
        lap_reset()

@touch(xy=(250,108), size=(32,32), align='center')
def on_touch(xy, action):
    global cd
    if action == 'down':
        cd.increase(1)

@touch(xy=(290,108), size=(32,32), align='center')
def on_touch(xy, action):
    global cd
    if action == 'down':
        cd.increase(-1)

@touch(xy=(250,160), size=(32,32), align='center')
def on_touch(xy, action):
    global cd
    if action == 'down':
        cd.increase(60)

@touch(xy=(290,160), size=(32,32), align='center')
def on_touch(xy, action):
    global cd
    if action == 'down':
        cd.increase(-60)

@touch(xy=(250,212), size=(32,32), align='center')
def on_touch(xy, action):
    global cd
    if action == 'down':
        cd.increase(3600)

@touch(xy=(290,212), size=(32,32), align='center')
def on_touch(xy, action):
    global cd
    if action == 'down':
        cd.increase(-3600)

def start_stop():
    global sw, cd
    
    if state['screen'] == 'stopwatch':
        if sw.running:
            sw.stop()
        else:
            sw.start()
    elif state['screen'] == 'countdown':
        if cd.running:
            cd.stop()
        else:
            cd.start()

def lap_reset():
    global sw, currentLap, cd
    
    if state['screen'] == 'stopwatch':
        if sw.running:
            sw.stopLapTimer("Lap %s" % currentLap)
            currentLap = (currentLap + 1) % 3
        else:
            sw.reset()
    elif state['screen'] == 'countdown':
        cd.reset()

def previous_screen():
    global currentScreen
    
    currentScreen = (currentScreen - 1) % len(screenList)
    state['screen'] = screenList[currentScreen]
    
def next_screen():
    global currentScreen
    
    currentScreen = (currentScreen + 1) % len(screenList)
    state['screen'] = screenList[currentScreen]

def showStopwatch():
    global sw
    
    screen.fill(color=(26,26,26))

    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color='red',
    )
    
    screen.text(
        'Stopwatch',
        xy=(160, 15),
        align='center',
        color='white',
        font='font/Arial Rounded Bold.ttf',
        font_size=14, 
    )
    
    if sw.running:
        startStop = 'Stop'
    else:
        startStop = 'Start'
    
    screen.text(
        startStop,
        xy=(10,17),
        align='left',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,    
    )
    
    if sw.running:
        lapReset = 'Lap'
    else:
        lapReset = 'Reset'
    
    screen.text(
        lapReset,
        xy=(310,17),
        align='right',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,   
    )
    
    screen.image(
        'img/left.png',
        xy=(100, 15),
        align='center'
    )
    screen.image(
        'img/right.png',
        xy=(220, 15),
        align='center'
    )
    
    row_y = 83

    for lap in range(0,3):

        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color=(39,40,34),
        )
        
        screen.text(
            'Lap %s' % (lap+1),
            xy=(25,row_y+27),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )

        screen.text(
            sw.getFormattedTime("Lap %s" % lap),
            xy=(295,row_y+27),
            align='right',
            color='white',
            font='font/JohnstonITCStd-Bold.ttf',
            font_size=18,
        )

        row_y += 52

    screen.text(
        sw.getFormattedTime(),
        xy=(160,55),
        align='center',
        font='font/digital-7.mono.ttf',
        color='red',
        font_size=54,
    )

@every(seconds=1)
def timerDone():
    global cd
    
    if cd.done:
        state['text_visible'] = not state['text_visible']

def showCountdown():
    global cd
    
    screen.fill(color=(26,26,26))

    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color='blue',
    )
    
    screen.text(
        'Countdown',
        xy=(160, 15),
        align='center',
        color='white',
        font='font/Arial Rounded Bold.ttf',
        font_size=14, 
    )
    
    if cd.running:
        startStop = 'Stop'
    else:
        startStop = 'Start'
    
    screen.text(
        startStop,
        xy=(10,17),
        align='left',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,    
    )
    
    screen.text(
        'Reset',
        xy=(310,17),
        align='right',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,   
    )
    
    screen.image(
        'img/left.png',
        xy=(100, 15),
        align='center'
    )
    screen.image(
        'img/right.png',
        xy=(220, 15),
        align='center'
    )

    row_y = 83

    for line in range(0,3):

        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color=(39,40,34),
        )
        
        if line == 0:
            lineText = "Seconds"
        elif line == 1:
            lineText = "Minutes"
        elif line == 2:
            lineText = "Hours"
            
        screen.text(
            lineText,
            xy=(25,row_y+27),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )
        
        screen.image(
            'img/plus.png',
            xy=(250,row_y+25),
            align='center'
        )
        
        screen.image(
            'img/minus.png',
            xy=(290,row_y+25),
            align='center'
        )

        row_y += 52

    if not state['text_visible'] and not cd.done:
        state['text_visible'] = True
        
    if state['text_visible']:
        screen.text(
            cd.getFormattedTime(),
            xy=(160,55),
            align='center',
            font='font/digital-7.mono.ttf',
            color='blue',
            font_size=54,
        )
    else:
        screen.text(
            cd.getFormattedTime(),
            xy=(160,55),
            align='center',
            font='font/digital-7.mono.ttf',
            color=(26,26,26),
            font_size=54,
        )
  
@every(seconds=1.0/30) 
def loop():
    
    if state['screen'] == 'stopwatch':
        showStopwatch()
    elif state['screen'] == 'countdown':
        showCountdown()

tingbot.run()