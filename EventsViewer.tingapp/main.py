# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *

import sqlite3 as lite
import uuid

state = {}

screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

eventsList = 0
currentEvent = 0

state['database'] = lite.connect('data.db')
state['database'].text_factory = str

state['webhook_name'] = tingbot.app.settings['webhook_name']
if not state['webhook_name']:
    tingbot.app.settings['webhook_name'] = str(uuid.uuid4())
    tingbot.app.settings.save()
    state['webhook_name'] = tingbot.app.settings['webhook_name']
print state['webhook_name'] 

@left_button.hold
@midleft_button.hold
@midright_button.hold
@right_button.hold
def on_hold():
    deleteall()

@left_button.press
def on_left():
    previous_page()

@midleft_button.press
def on_midleft():
    previous_page()

@midright_button.press
def on_midright():
    next_page()

@right_button.press
def on_right():
    next_page()

@touch(xy=(5,10), size=(80,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        clear()

@touch(xy=(80,16), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        previous_page()
            
@touch(xy=(240,16), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        next_page()

def deleteall():
    if 'database' in state and state['database']:
        state['cursor'] = state['database'].cursor()
        state['cursor'].execute("DELETE FROM Data")
        state['database'].commit()
    refresh_events()

def clear():
    global currentEvent
    
    if 'database' in state and state['database']:
        state['cursor'] = state['database'].cursor()
        state['cursor'].execute("DELETE FROM Data WHERE Id = (?)", (state['events'][currentEvent][0],))
        state['database'].commit()
        previous_page()
    refresh_events()
    
def previous_page():
    global currentEvent
    
    if state['events'] != 0:
        currentEvent = (currentEvent - 1)
        if currentEvent < 0: 
            currentEvent = currentEvent + 1
    
def next_page():
    global currentEvent
    
    if state['events'] != 0:
        currentEvent = (currentEvent + 1)
        if currentEvent >= len(state['events']):
            currentEvent = currentEvent - 1

# http://webhook.tingbot.com/webhook_name
@webhook(bytes(state['webhook_name']))
def on_webhook(data):
    if 'database' in state and state['database']:
        state['cursor'].execute("SELECT * FROM Data WHERE Event = ? ORDER BY Id DESC LIMIT 1", (data,))
        exists = state['cursor'].fetchone()
        if exists is None:
            state['cursor'].execute("INSERT INTO Data VALUES(NULL, ?)", (data,))
            state['database'].commit()
 
@every(seconds=1)
def refresh_events():
    if 'database' in state and state['database']:
        state['cursor'] = state['database'].cursor()
        state['cursor'].execute('SELECT * FROM Data ORDER BY Id DESC')
        state['events'] = state['cursor'].fetchall()

def showMain():
    screen.fill(color='white')
    
    screen.rectangle(
        xy=(0,0),
        align='topleft',
        size=(320,32),
        color=(79,185,246),
    )
    
    screen.text(
        'Events Viewer',
        xy=(160, 15),
        align='center',
        color='white',
        font='font/Arial Rounded Bold.ttf',
        font_size=18, 
    )
    
    if len(state['events']) == 0:
        screen.text(
            "No event...",
            xy=(320/2,(240+32)/2-20),
            align='center',
            color='black',
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )
        screen.text(
            "Your webhook UUID:",
            xy=(320/2,(240+32)/2),
            align='center',
            color='black',
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )
        screen.text(
            state['webhook_name'],
            xy=(320/2,(240+32)/2+20),
            align='center',
            color='black',
            font='font/JohnstonITCStd-Bold.ttf',
            font_size=14,
        )
    else:
        screen.image(
            'img/left.png',
            xy=(80, 16),
            align='center'
        )
        screen.image(
            'img/right.png',
            xy=(240, 16),
            align='center'
        )
        
        screen.text(
            "%s / %s" % (currentEvent+1, len(state['events'])),
            xy=(315,10),
            align='topright',
            color='white',
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )
        
        screen.text(
            "Clear",
            xy=(5,10),
            align='topleft',
            color='white',
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )

        screen.rectangle(
            xy=(0,32),
            align='topleft',
            size=(320,240-32),
            color='white',
        )
        
        screen.text(
            state['events'][currentEvent][1],
            xy=(5,32+2),
            align='topleft',
            color='black',
            font='font/JohnstonITCStd-Light.ttf',
            font_size=18,
            max_width=310,
            max_lines=12
        )

@every(seconds=1.0/30)
def loop():
    if 'events' not in state:
        screen.fill(color='white')
        screen.text(
            'Loading...',
            xy=(160, 225),
            font_size=12,
            color='black',
        )
        return
    
    if state['screen'] == 'main':
        showMain()

try:
    tingbot.run()
finally:
    if state['database']:
        state['database'].close()