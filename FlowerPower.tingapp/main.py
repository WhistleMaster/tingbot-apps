# coding: utf-8
# v1.0

import tingbot
from tingbot import *
import urllib, json
from datetime import datetime
from dateutil import parser
import requests
import time
import sys, os, re
from urlparse import urlparse

username = tingbot.app.settings['username']
password = tingbot.app.settings['password']
client_id = tingbot.app.settings['client_id']
client_secret = tingbot.app.settings['client_secret']

state = {}

screenList = {
    0: 'garden',
    1: 'plant',
    2: 'sensor'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

currentPlant = 0

colorCodeMapper = {
    4: 'brown',
    6: 'green',
    7: 'blue'
}

sensorInfoList = {
    0: {'infoName': 'Name', 'infoData': 'nickname'},
    1: {'infoName': 'Serial', 'infoData': 'sensor_serial'},
    2: {'infoName': 'Battery', 'infoData': 'battery_level'},
    3: {'infoName': 'Firmware', 'infoData': 'firmware_version'},
}

plantList = {
    0: {'infoName': 'water', 'infoData': 'soil_moisture'},
    1: {'infoName': 'fert', 'infoData': 'fertilizer'},
    2: {'infoName': 'temp', 'infoData': 'air_temperature'},
    3: {'infoName': 'sun', 'infoData': 'light'},
}

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

@left_button.press
def on_left():
    previous_page()

@midleft_button.press
def on_midleft():
    next_page()

@midright_button.press
def on_midright():
    previous_screen()

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

@touch(xy=(0,17), size=(30,31), align='left')
def on_touch(xy, action):
    if action == 'down':
        if state['screen'] != 'plant':
            state['screen'] = screenList[1]
        else:
            state['screen'] = screenList[0]
            
@touch(xy=(320,17), size=(30,31), align='right')
def on_touch(xy, action):
    if action == 'down':
        if state['screen'] != 'sensor':
            state['screen'] = screenList[2]
        else:
            state['screen'] = screenList[0]
        
def previous_page():
    global currentPlant
    
    currentPlant = (currentPlant - 1) % len(state['garden'])
    
def next_page():
    global currentPlant
    
    currentPlant = (currentPlant - 1) % len(state['garden'])
    
def previous_screen():
    global currentScreen
    
    currentScreen = (currentScreen - 1) % len(screenList)
    state['screen'] = screenList[currentScreen]
    
def next_screen():
    global currentScreen
    
    currentScreen = (currentScreen + 1) % len(screenList)
    state['screen'] = screenList[currentScreen]

@tingbot.every(hours=1)
def authenticate():
    req = requests.get('https://apiflowerpower.parrot.com/user/v1/authenticate',
    
    data={'grant_type': 'password',
    'username': username,
    'password': password,
    'client_id': client_id,
    'client_secret': client_secret,
    })
    
    response = req.json()
    decoded = json.dumps(response)
    deco = json.loads(decoded)
    
    state['access_token'] = deco["access_token"]

@tingbot.every(hours=1)
def loadGarden():
    if 'access_token' not in state or not state['access_token']:
        return
    
    req = requests.get('https://apiflowerpower.parrot.com/sensor_data/v4/garden_locations_status',
    headers={'Authorization': 'Bearer ' + state['access_token']})
    
    response = req.json()
    decoded = json.dumps(response)
    deco = json.loads(decoded)
    
    tempGardenData1 = deco["locations"]
    tempSensorData1 = deco["sensors"]
    
    req = requests.get('https://apiflowerpower.parrot.com/sensor_data/v3/sync',
    headers={'Authorization': 'Bearer ' + state['access_token']},
    params={'include_s3_urls': 1})
    
    response = req.json()
    decoded = json.dumps(response)
    deco = json.loads(decoded)
    
    tempGardenData2 = deco["locations"]
    tempSensorData2 = deco["sensors"]
    
    sensors = []
    for i in range(0,len(deco["sensors"])):
        sensor = tempSensorData1[i].copy()
        sensor.update(tempSensorData2[i])
        sensors.append(sensor)
    
    state['sensors'] = sensors
    
    garden = []
    for i in range(0,len(deco["locations"])):
        plant = tempGardenData1[i].copy()
        plant.update(tempGardenData2[i])
        garden.append(plant)
    
    state['garden'] = garden
    
    downloadGardenImages()

def getSensor():
    for i in range(0,len(state['sensors'])):
        if state['garden'][currentPlant]['sensor_serial'] == state['sensors'][i]['sensor_serial']:
            return i

def getSensorColor():
    for i in range(0,len(state['sensors'])):
        if state['garden'][currentPlant]['sensor_serial'] == state['sensors'][i]['sensor_serial']:
            return colorCodeMapper[state['sensors'][i]['color']] or 'unknown'

def showSensor():
    screen.fill(color=(212,212,212))
    
    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color=(44,86,85),
    )

    screen.text(
        "Sensor".upper(),
        xy=(160, 19),
        align='center',
        color='white',
        font='font/PoplarStd.otf',
        font_size=22, 
    )
    
    screen.image(
        'img/left_white_arrow.png',
        xy=(100, 15),
        align='center',
        scale=0.7
    )
    screen.image(
        'img/right_white_arrow.png',
        xy=(220, 15),
        align='center',
        scale=0.7
    )
    
    screen.image(
        'img/ico_sensor.png',
        xy=(310, 13),
        align='right',
        scale=0.5
    )
    
    screen.image(
        'img/info_icon.png',
        xy=(10, 16),
        align='left',
        scale=0.5
    )
    
    row_y = 31
    sensor_serial = state['garden'][currentPlant]['sensor_serial']

    for i in range(0,4):

        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color=(83,185,182),
        )
        
        screen.text(
            sensorInfoList[i]['infoName'],
            xy=(20,row_y+27),
            align='left',
            color='white',
            font='font/PoplarStd.otf',
            font_size=17,
        )
        
        if i == 2:
            infoText = str(state['sensors'][getSensor()][sensorInfoList[i]['infoData']]['level_percent']) + '%'
        else:
            infoText = state['sensors'][getSensor()][sensorInfoList[i]['infoData']]

        screen.text(
            infoText,
            xy=(300,row_y+27),
            align='right',
            color='white',
            font='font/PoplarStd.otf',
            font_size=18,
            max_width=200,
            max_lines=2
        )

        row_y += 52

def showPlant():
    screen.fill(color=(212,212,212))
    
    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color=(44,86,85),
    )

    screen.text(
        truncate(state['garden'][currentPlant]['plant_nickname'].upper(),13),
        xy=(160, 19),
        align='center',
        color='white',
        font='font/PoplarStd.otf',
        font_size=22, 
    )
    
    screen.image(
        'img/left_white_arrow.png',
        xy=(100, 15),
        align='center',
        scale=0.7
    )
    screen.image(
        'img/right_white_arrow.png',
        xy=(220, 15),
        align='center',
        scale=0.7
    )
    
    screen.image(
        'img/ico_sensor.png',
        xy=(310, 13),
        align='right',
        scale=0.5
    )
    
    screen.image(
        'img/info_icon.png',
        xy=(10, 16),
        align='left',
        scale=0.5
    )
    
    row_y = 31
    sensor_serial = state['garden'][currentPlant]['sensor_serial']

    for i in range(0,4):

        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color='white',
        )
        
        instruction = state['garden'][currentPlant][plantList[i]['infoData']]['instruction_key']
        
        if instruction is not None:
            if 'good' in instruction:
                status = 'good'
            elif 'too_low' in instruction:
                status = 'warning'
            else:
               status = 'none'
              
            instructionText = instruction.replace('_',' ').upper()
        else:
            status = 'none'
            instructionText = 'None'.upper()
        
        screen.text(
            instructionText,
            xy=(70,row_y+28),
            align='left',
            color=(83,185,182),
            font='font/PoplarStd.otf',
            font_size=18,
            max_width=200,
            max_lines=2
        )
        
        image = 'img/instruction_%s_%s.png' % (plantList[i]['infoName'], status)
        
        screen.image(
            image,
            xy=(10,row_y+27),
            align='left',
            scale=1
        )
        
        infoText = state['garden'][currentPlant][plantList[i]['infoData']]['gauge_values']['current_value']
        
        if infoText is not None:
            if i == 0 :
                infoText="%.2f %%" % infoText
            elif i == 1:
                infoText="%.2f dS/m" % infoText
            elif i == 2:
                infoText="%.2f " % infoText + u'\N{DEGREE SIGN}' + "C"
            elif i == 3:
                infoText="%.2f mol/m2/d" % infoText
        
        screen.text(
            infoText,
            xy=(300,row_y+28),
            align='right',
            color=(83,185,182),
            font='font/PoplarStd.otf',
            font_size=18,
            max_width=200,
            max_lines=2
        )

        row_y += 52
        
def showGarden():
    screen.fill(color=(212,212,212))
    
    image = state['garden'][currentPlant]['images'][0]['image']
    width_sf = 320.0 / image.size[0]
    height_sf = 240.0 / image.size[1]
    sf = max(width_sf, height_sf)
    
    screen.image(image, scale=sf)
    screen.image(
        'img/sensorTriangleBackground.png',
        xy=(320, 200),
        align='right',
        scale=0.8
    )
    
    screen.image(
        'img/sensor-image_%s.png' % getSensorColor(),
        xy=(316, 195),
        align='right',
        scale=0.5
    )
    
    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color=(44,86,85),
    )

    screen.text(
        "Garden".upper(),
        xy=(160, 19),
        align='center',
        color='white',
        font='font/PoplarStd.otf',
        font_size=22, 
    )
    
    screen.image(
        'img/left_white_arrow.png',
        xy=(100, 15),
        align='center',
        scale=0.7
    )
    screen.image(
        'img/right_white_arrow.png',
        xy=(220, 15),
        align='center',
        scale=0.7
    )
    
    screen.image(
        'img/ico_sensor.png',
        xy=(310, 13),
        align='right',
        scale=0.5
    )
    
    screen.image(
        'img/info_icon.png',
        xy=(10, 16),
        align='left',
        scale=0.5
    )
    
    screen.rectangle(
        color=(83,185,182),
        size=(320, 31),
        align='bottom',
    )
        
    screen.text(
        truncate(state['garden'][currentPlant]['plant_nickname'].upper(),13),
        align='left',
        xy=(5, 228),
        color='white',
        font_size=22,
        font='font/PoplarStd.otf',
    )
    
    if state['garden'][currentPlant]['in_pot']:
        screen.image(
            'img/ico_pot.png',
            xy=(167, 225),
            align='right',
            scale=0.6
        )
        screen.text(
            'Pot'.upper(),
            align='left',
            xy=(170, 228),
            color='white',
            font_size=22,
            font='font/PoplarStd.otf',
        )
    else:
        screen.image(
            'img/ico_soil.png',
            xy=(165, 222),
            align='right',
            scale=0.5
        )
        screen.text(
            'Soil'.upper(),
            align='left',
            xy=(167, 228),
            color='white',
            font_size=22,
            font='font/PoplarStd.otf',
        )
    
    if state['garden'][currentPlant]['is_indoor']:
        screen.image(
            'img/ico_indoor.png',
            xy=(250, 225),
            align='right',
            scale=0.5
        )
        screen.text(
            'Indoor'.upper(),
            align='left',
            xy=(255, 228),
            color='white',
            font_size=22,
            font='font/PoplarStd.otf',
        )
    else:
        screen.image(
            'img/ico_outdoor.png',
            xy=(236, 226),
            align='right',
            scale=0.6
        )
        screen.text(
            'Outdoor'.upper(),
            align='left',
            xy=(241, 228),
            color='white',
            font_size=22,
            font='font/PoplarStd.otf',
        )
 
def downloadGardenImages():
    for i in range(0,len(state['garden'])):
        url = state['garden'][i]['images'][0]['url']
        filename = '/tmp/int-' + os.path.basename(urlparse(url).path)

        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename)

        state['garden'][i]['images'][0]['image'] = Image.load_filename(filename)

@every(seconds=1.0/30)      
def loop():
    if 'access_token' not in state or not state['access_token']:
        screen.fill(color=(212,212,212))
        screen.image('img/f_logo_w.png')
        screen.text(
            'Loading...',
            xy=(160, 175),
            font_size=18,
            font='font/PoplarStd.otf',
            color='black',
        )
        return

    if 'garden' not in state or not state['garden']:
        loadGarden()
        return
    
    if state['screen'] == 'garden':
        showGarden()
    elif state['screen'] == 'plant':
        showPlant()
    elif state['screen'] == 'sensor':
        showSensor()
        
tingbot.run()
