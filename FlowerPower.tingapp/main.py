# coding: utf-8
# v1.1.1

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

screen_list = {
    0: 'garden',
    1: 'plant',
    2: 'sensor'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

current_plant = 0

color_code_mapper = {
    4: 'brown',
    6: 'green',
    7: 'blue'
}

sensor_info_list = {
    0: {'name': 'Name', 'data': 'nickname'},
    1: {'name': 'Serial', 'data': 'system_id'},
    2: {'name': 'Battery', 'data': 'current_value'},
    3: {'name': 'Firmware', 'data': 'firmware_version'},
    4: {'name': 'Last upload', 'data': 'last_sample_upload'},
}

plant_list = {
    0: {'name': 'water', 'data': 'soil_moisture'},
    1: {'name': 'fert', 'data': 'fertilizer'},
    2: {'name': 'temp', 'data': 'air_temperature'},
    3: {'name': 'sun', 'data': 'light'},
}

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

@left_button.press
def on_left():
    plant_screen()  

@midleft_button.press
def on_midleft():
    previous_plant()

@midright_button.press
def on_midright():
    next_plant()

@right_button.press
def on_right():
    sensor_screen()

@touch(xy=(75,15), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        previous_page()
            
@touch(xy=(245,15), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        next_page()

@touch(xy=(0,17), size=(30,31), align='left')
def on_touch(xy, action):
    if action == 'down':
        plant_screen()
            
@touch(xy=(320,17), size=(30,31), align='right')
def on_touch(xy, action):
    if action == 'down':
        sensor_screen()
        
def previous_plant():
    global current_plant
    
    current_plant = (current_plant - 1) % len(state['garden_configuration'])
    
def next_plant():
    global current_plant
    
    current_plant = (current_plant - 1) % len(state['garden_configuration'])
    
def plant_screen():
    if state['screen'] != 'plant':
            state['screen'] = screen_list[1]
    else:
        state['screen'] = screen_list[0]
    
def sensor_screen():
    if state['screen'] != 'sensor':
            state['screen'] = screen_list[2]
    else:
        state['screen'] = screen_list[0]

@tingbot.every(hours=1)
def authenticate():
    req = requests.get('https://api-flower-power-pot.parrot.com/user/v1/authenticate',
    
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
def load_garden():
    if 'access_token' not in state or not state['access_token']:
        return
    
    req = requests.get('https://api-flower-power-pot.parrot.com/garden/v2/configuration',
    headers={'Authorization': 'Bearer ' + state['access_token']},
    params={'include_s3_urls': 1})
    
    response = req.json()
    decoded = json.dumps(response)
    deco = json.loads(decoded)
    
    state['garden_configuration'] = deco["locations"]
    
    req = requests.get('https://api-flower-power-pot.parrot.com/garden/v1/status',
    headers={'Authorization': 'Bearer ' + state['access_token']})
    
    response = req.json()
    decoded = json.dumps(response)
    deco = json.loads(decoded)

    state['garden_status'] = deco["locations"]
    
    download_garden_images()

def get_sensor_color():
    return color_code_mapper[state['garden_configuration'][current_plant]['sensor']['color']] or 'unknown'

def show_sensor():
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
        xy=(75, 15),
        align='center',
        scale=0.7
    )
    screen.image(
        'img/right_white_arrow.png',
        xy=(245, 15),
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
    sensor_serial = state['garden_configuration'][current_plant]['sensor']['sensor_identifier']

    for i in range(0,5):

        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,41), #51
            color=(83,185,182),
        )
        
        screen.text(
            sensor_info_list[i]['name'],
            xy=(20,row_y+23), #27
            align='left',
            color='white',
            font='font/PoplarStd.otf',
            font_size=18,
        )
        
        if i == 2:
            infoText = str(state['garden_status'][current_plant]['battery']['gauge_values'][sensor_info_list[i]['data']]) + '%'
        elif i == 4:
            infoText = state['garden_status'][current_plant][sensor_info_list[i]['data']]
        else:
            infoText = state['garden_configuration'][current_plant]['sensor'][sensor_info_list[i]['data']]

        screen.text(
            infoText,
            xy=(300,row_y+23), #27
            align='right',
            color='white',
            font='font/PoplarStd.otf',
            font_size=18,
            max_width=200,
            max_lines=2
        )

        row_y += 42 #52

def show_plant():
    screen.fill(color=(212,212,212))
    
    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color=(44,86,85),
    )

    screen.text(
        truncate(state['garden_configuration'][current_plant]['plant_nickname'].upper(),13),
        xy=(160, 19),
        align='center',
        color='white',
        font='font/PoplarStd.otf',
        font_size=22, 
    )
    
    screen.image(
        'img/left_white_arrow.png',
        xy=(75, 15),
        align='center',
        scale=0.7
    )
    screen.image(
        'img/right_white_arrow.png',
        xy=(245, 15),
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

    for i in range(0,4):

        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color='white',
        )
        
        if i == 0:
            instruction = state['garden_status'][current_plant]['watering'][plant_list[i]['data']]['instruction_key']
        else:
            instruction = state['garden_status'][current_plant][plant_list[i]['data']]['instruction_key']
        
        if instruction is not None:
            if 'good' in instruction:
                status = 'good'
            elif 'too_low' in instruction:
                status = 'warning'
            elif 'too_high' in instruction:
                status = 'critical'
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
        
        image = 'img/instruction_%s_%s.png' % (plant_list[i]['name'], status)
        
        screen.image(
            image,
            xy=(10,row_y+27),
            align='left',
            scale=1
        )
        
        if i == 0:
            infoText = state['garden_status'][current_plant]['watering'][plant_list[i]['data']]['gauge_values']['current_value']
        else:
            infoText = state['garden_status'][current_plant][plant_list[i]['data']]['gauge_values']['current_value']
        
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
        
def show_garden():
    screen.fill(color=(212,212,212))
    
    image = state['garden_configuration'][current_plant]['pictures'][0]['image']
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
        'img/sensor-image_%s.png' % get_sensor_color(),
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
        xy=(75, 15),
        align='center',
        scale=0.7
    )
    screen.image(
        'img/right_white_arrow.png',
        xy=(245, 15),
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
        truncate(state['garden_configuration'][current_plant]['plant_nickname'].upper(),13),
        align='left',
        xy=(5, 228),
        color='white',
        font_size=22,
        font='font/PoplarStd.otf',
    )
    
    if state['garden_configuration'][current_plant]['in_pot']:
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
    
    if state['garden_configuration'][current_plant]['is_indoor']:
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
 
def download_garden_images():
    for i in range(0,len(state['garden_configuration'])):
        url = state['garden_configuration'][i]['pictures'][0]['url']
        filename = '/tmp/int-' + os.path.basename(urlparse(url).path)

        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename)

        state['garden_configuration'][i]['pictures'][0]['image'] = Image.load_filename(filename)

def show_startup():
    screen.fill(color=(212,212,212))
    screen.image('img/f_logo_w.png')
    screen.text(
        'Loading...',
        xy=(160, 175),
        font_size=18,
        font='font/PoplarStd.otf',
        color='black',
    )
    
@every(seconds=1.0/30)
def loop():
    if 'access_token' not in state or not state['access_token']:
        show_startup()
        return

    if 'garden_configuration' not in state or not state['garden_configuration'] or 'garden_status' not in state or not state['garden_status']:
        load_garden()
        return
    
    if state['screen'] == 'garden':
        show_garden()
    elif state['screen'] == 'plant':
        show_plant()
    elif state['screen'] == 'sensor':
        show_sensor()
        
tingbot.run()