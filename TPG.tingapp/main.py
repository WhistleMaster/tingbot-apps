# coding: utf-8
# v1.1.0

import tingbot
from tingbot import *
import urllib, json
from datetime import datetime
from dateutil import parser
import time

state = {}

apiKey = tingbot.app.settings['apiKey']

stopList = {
    0: {'stopCode': 'CORD', 'stopName': 'Concorde'},
    1: {'stopCode': 'HBOR', 'stopName': 'H.-Bordier'},
    2: {'stopCode': 'AAIN', 'stopName': 'Av. de l\'Ain'}
}
currentStop = 0
stopCode = stopList[currentStop]['stopCode']
stopName = stopList[currentStop]['stopName']

screenList = {
    0: 'departures',
    1: 'disruptions'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

currentDisruption = 0
disruptionsList = 0

baseUrl = "http://prod.ivtr-od.tpg.ch/v1/"
reqUrl = None
response = None

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

def chunks(s, n):
    for start in range(0, len(s), n):
        yield s[start:start+n]

def hex_to_rgb(value):
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    
@left_button.press
def on_left():
    previous_screen()

@midleft_button.press
def on_midleft():
    previous_page()

@midright_button.press
def on_midright():
    next_page()

@right_button.press
def on_right():
    next_screen()

@touch(xy=(100,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        previous_page()
            
@touch(xy=(220,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        next_page()

@touch(xy=(160,17), size=(64,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        if state['screen'] == 'disruptions':
            refreshDepartures()
            showDepartures()
    
@touch(xy=(0,16), size=(320,31), align='left')
def on_touch(xy, action):
    if action == 'down':
        if state['screen'] == 'disruptions':
            refreshDisruptions()
            showDisruptions()

def previous_page():
    global currentStop, stopCode, stopName, currentDisruption
    
    if state['screen'] == 'departures':
        currentStop = (currentStop - 1) % len(stopList)
        stopCode = stopList[currentStop]['stopCode']
        stopName = stopList[currentStop]['stopName']
        refreshDepartures()
    else:
        if disruptionsList != 0:
            currentDisruption = (currentDisruption - 2)
            if currentDisruption < 0: currentDisruption = currentDisruption + 2
        refreshDisruptions()
    
def next_page():
    global currentStop, stopCode, stopName, currentDisruption
    
    if state['screen'] == 'departures':
        currentStop = (currentStop + 1) % len(stopList)
        stopCode = stopList[currentStop]['stopCode']
        stopName = stopList[currentStop]['stopName']
        refreshDepartures()
    else:
        if disruptionsList != 0:
            currentDisruption = (currentDisruption + 2)
            if currentDisruption >= disruptionsList: currentDisruption = currentDisruption - 2
        refreshDisruptions()
    
def previous_screen():
    global currentScreen
    
    currentScreen = (currentScreen - 1) % len(screenList)
    state['screen'] = screenList[currentScreen]
    
    refreshDepartures()
    refreshDisruptions()
    
def next_screen():
    global currentScreen
    
    currentScreen = (currentScreen + 1) % len(screenList)
    state['screen'] = screenList[currentScreen]
    
    refreshDepartures()
    refreshDisruptions()

@tingbot.every(minutes=1)
def refreshDisruptions():
    reqUrl = baseUrl + "GetDisruptions.json" + "?key=%s" % apiKey
    response = urllib.urlopen(reqUrl)
    
    state['disruptions'] = json.loads(response.read())

@tingbot.every(seconds=30)
def refreshDepartures():
    reqUrl = baseUrl + "GetNextDepartures.json" + "?key=%s" % apiKey + "&stopCode=%s" % stopCode
    response = urllib.urlopen(reqUrl)

    state['departures'] = json.loads(response.read())
    
def getLineColor(lineNum):
    reqUrl = baseUrl + "GetLinesColors.json" + "?key=%s" % apiKey
    response = urllib.urlopen(reqUrl)

    data = json.loads(response.read())
    
    return [item for item in data["colors"] 
                if item["lineCode"] == lineNum]

def showDisruptions():
    global disruptionsList
    
    screen.fill(color=(26,26,26))
    
    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color=(255,0,0),
    )
    
    disruptions = state['disruptions']
    
    d = parser.parse(disruptions['timestamp'])
    screen.text(
        d.strftime("%d-%m-%Y %H:%M:%S"),
        xy=(310,17),
        align='right',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,
    )
    
    row_y = 31
    line_num = 1
    
    if len(disruptions['disruptions']) == 0:
        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color=(39,40,34),
        )
        
        screen.text(
            'Perturbations',
            xy=(10,15),
            align='left',
            color='white',
            font='font/Arial Rounded Bold.ttf',
            font_size=14,
        )
        
        screen.text(
            "Aucune",
            xy=(10,row_y+27),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )
    else:
        disruptionsList = len(disruptions['disruptions'])

        pageNum = (disruptionsList + 2 - 1) // 2
        currentNum = (currentDisruption + 2) // 2
        
        screen.text(
            'Perturbations (%s)' % disruptionsList,
            xy=(10,15),
            align='left',
            color='white',
            font='font/Arial Rounded Bold.ttf',
            font_size=14,
        )
        
        screen.text(
            "%s / %s" % (currentNum, pageNum),
            xy=(170,17),
            align='right',
            color='white',
            font='font/JohnstonITCStd-Light.ttf',
            font_size=14,
        )
        
        for i in range(currentDisruption, disruptionsList):
            if line_num > 2:
                break
            
            screen.rectangle(
                xy=(0,row_y),
                align='topleft',
                size=(320,102),
                color=(39,40,34),
            )
            
            disruption = disruptions['disruptions'][i]
            bus_number = disruption['lineCode']
            disruption_nature = disruption['nature']
            disruption_consequence = disruption['consequence']
            
            screen.text(
                bus_number,
                xy=(25,row_y+17),
                align='center',
                color='white',
                font='font/JohnstonITCStd-Bold.ttf',
                font_size=26,
            )
            
            screen.text(
                truncate(disruption_nature, 30),
                xy=(50,row_y+17),
                align='left',
                color=(220,220,220),
                font='font/JohnstonITCStd-Bold.ttf',
                font_size=17,
            )
            
            row_y_b = 25
            chunk_num = 1
            
            for chunk in chunks(disruption_consequence, 33):
                if chunk_num > 3:
                    break
                
                screen.text(
                    chunk,
                    xy=(50,row_y+17+row_y_b),
                    align='left',
                    color=(220,220,220),
                    font='font/JohnstonITCStd-Light.ttf',
                    font_size=17,
                )
                row_y_b += 25
                chunk_num += 1
        
            row_y += 104
            line_num += 1
    
def showDepartures():
    screen.fill(color=(26,26,26))
    
    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color=(255,128,0),
    )
    
    screen.text(
        'Bus',
        xy=(10,15),
        align='left',
        color='white',
        font='font/Arial Rounded Bold.ttf',
        font_size=14,    
    )
    
    screen.text(
        stopName,
        xy=(310,17),
        align='right',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,   
    )
    
    screen.image(
        'img/TPG_logo.png',
        xy=(160, 17),
        align='center'
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

    departures = state['departures']
    
    row_y = 31
    line_num = 1
    
    for departure in departures['departures']:
        if line_num > 4:
            break
        
        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color=(39,40,34),
        )
        
        bus_number = departure['line']['lineCode']
        bus_destination = departure['line']['destinationName']
        bus_minutes = departure['waitingTime']
        
        if 'disruptions' in departure:
            screen.image('img/warning.png', xy=(63,row_y+24))
            
        screen.text(
            bus_number,
            xy=(10,row_y+27),
            align='left',
            color=hex_to_rgb(getLineColor(bus_number)[0]['background']),
            font='font/JohnstonITCStd-Bold.ttf',
            font_size=26,
        )
        
        screen.text(
            bus_destination,
            xy=(80,row_y+27),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )
        
        if bus_minutes.find('no more') != -1:
            screen.image('img/no_more.png', xy=(280,row_y+27))
        elif bus_minutes.find('&gt;') != -1:
            screen.text(
                '> 1h',
                xy=(305,row_y+27),
                align='right',
                color='white',
                font='font/JohnstonITCStd-Bold.ttf',
                font_size=18,
            )
        elif bus_minutes == "0":
             screen.image('img/bus.png', xy=(280,row_y+27))
        elif not bus_minutes.isdigit():
            screen.text(
                '%s' % bus_minutes,
                xy=(305,row_y+27),
                align='right',
                color='white',
                font='font/JohnstonITCStd-Bold.ttf',
                font_size=18,
            )
        else:
            screen.text(
                '%s min' % bus_minutes,
                xy=(305,row_y+27),
                align='right',
                color='white',
                font='font/JohnstonITCStd-Bold.ttf',
                font_size=18,
            )

        row_y += 52
        line_num += 1

@every(seconds=1.0/30)
def loop():
    if ('disruptions' not in state) or ('departures' not in state):
        screen.fill('white')
        screen.image('img/TPG_startup.png')
        screen.text(
            'Loading...',
            xy=(160, 180),
            font_size=12,
            color='black',
        )
        return
    
    if state['screen'] == 'departures':
        showDepartures()
    elif state['screen'] == 'disruptions':
        showDisruptions()

tingbot.run()