# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *
import os
from glob import glob
import ntpath
from time import sleep

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

state = {}
screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

extsList = tingbot.app.settings['extsList']
foldersList = tingbot.app.settings['foldersList']

state['index'] = 0
state['displayInfo'] = False
state['running'] = True

@touch(xy=(100,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        next_photo()
            
@touch(xy=(220,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        previous_photo()
    
@touch(xy=(0,16), size=(45,31), align='left')
def on_touch(xy, action):
    if action == 'down':
        toggle_running()
            
@touch(xy=(320,16), size=(45,31), align='right')
def on_touch(xy, action):
    if action == 'down':
        toggle_info()
        
@left_button.press
def on_left():
    previous_photo()

@midleft_button.press
def on_midleft():
    next_photo()

@midright_button.press
def on_midright():
    toggle_info()
    
@right_button.press
def on_rigt():
    toggle_running()

def toggle_info():
    state['displayInfo'] = not state['displayInfo']
    
    if state['photos']:
        transition()

def toggle_running():
    state['running'] = not state['running']
    
    if state['photos']:
        transition()
    
@every(minutes=30)
def refresh_album():
    photos = []
        
    for folder in foldersList:
        for ext in extsList:
            if os.path.exists(folder):
                photosList = glob(os.path.join(folder, "*.{}".format(ext)))
                photos.extend(photosList)

    photos.sort()

    state['photos'] = photos
    
    if state['photos'] and state['running']:
        transition()

@every(seconds=10)
def play_content():

    if state['running']:
        next_photo()
        
def next_photo():
    if 'photos' not in state or not state['photos']:
        return
    
    photos = state['photos']
    state['index'] = (state['index'] + 1) % len(photos)
    
    transition()

def previous_photo():
    if 'photos' not in state or not state['photos']:
        return
    
    photos = state['photos']
    state['index'] = (state['index'] - 1) % len(photos)

    transition()
      
def transition():
    
    filename = state['photos'][state['index']]
    image = Image.load_filename(filename)

    width_sf = 320.0 / image.size[0]
    height_sf = 240.0 / image.size[1]

    sf = max(width_sf, height_sf)
    
    for x in [x * 0.1 for x in range(0, 10)]:
        screen.image(image, scale=sf, alpha=x)
        screen.update()
        sleep(0.025)

def display_info():
    
    filename = state['photos'][state['index']]
    
    if state['displayInfo']:
        screen.rectangle(
            xy=(0,16),
            align='left',
            size=(320,31),
            color='black',
        )
        
        screen.text(
            'Album',
            xy=(160, 15),
            align='center',
            color='white',
            font='font/Arial Rounded Bold.ttf',
            font_size=14, 
        )
        
        if state['running']:
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
            'Hide',
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
        
        screen.rectangle(
            color='black',
            size=(320, 20),
            align='bottom',
        )
        
        screen.text(
            truncate(ntpath.basename(filename)),
            align='left',
            xy=(5, 229),
            color='white',
            font_size=14,
            font='font/OpenSans-Semibold.ttf',
        )
        
        screen.text(
            "%s/%s" % (state['index']+1, len(state['photos'])),
            align='right',
            xy=(315, 229),
            color='white',
            font_size=14,
            font='font/OpenSans-Semibold.ttf',
        )

def showMain():
    if not state['photos']:
        screen.fill(color='white')
        screen.text(
            'No media...',
            xy=(160, 140),
            font_size=12,
            color='black',
        )
        return
    
    display_info()

@every(seconds=1.0/30)     
def loop():
    if 'photos' not in state:
        screen.fill(color='white')
        screen.image('img/logo.png', scale=0.6)
        screen.text(
            'Loading...',
            xy=(160, 200),
            font_size=12,
            color='black',
        )
        return

    if state['screen'] == 'main':
        showMain()

# run the app
tingbot.run()