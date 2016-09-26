# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *
import urllib, json
from datetime import datetime
from dateutil import parser
import time

state = {}

screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

baseUrl = "http://" + tingbot.app.settings['IP'] + "/admin/"
reqUrl = None
response = None

statsList = {
    0: {'statName': 'Ads blocked', 'statJSON': 'ads_blocked_today'},
    1: {'statName': 'DNS queries', 'statJSON': 'dns_queries_today'},
    2: {'statName': 'Pi-holed', 'statJSON': 'ads_percentage_today'},
    3: {'statName': 'Domain list size', 'statJSON': 'domains_being_blocked'},
}

@tingbot.every(minutes=1)
def refresh():
    reqUrl = baseUrl + "api.php"
    response = urllib.urlopen(reqUrl)
    
    state['stats'] = json.loads(response.read())
 
def showMain():
    screen.fill(color=(26,26,26))

    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color=(60,141,188),
    )
    
    screen.image(
        'img/icon.png',
        xy=(10,16),
        scale=0.5,
        align='left',
    )
    
    screen.text(
        'Pi-hole',
        xy=(160, 15),
        align='center',
        color='white',
        font='font/Arial Rounded Bold.ttf',
        font_size=18, 
    )
    
    row_y = 31

    for i in range(0,4):

        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color=(39,40,34),
        )
        
        screen.text(
            statsList[i]['statName'],
            xy=(20,row_y+27),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )
        
        if i == 2:
            statText = state['stats'][statsList[i]['statJSON']] + "%"
        else:
            statText = state['stats'][statsList[i]['statJSON']]
        
        screen.text(
            statText,
            xy=(300,row_y+27),
            align='right',
            color='white',
            font='font/JohnstonITCStd-Bold.ttf',
            font_size=18,
        )

        row_y += 52

@every(seconds=1.0/30)
def loop():
    if 'stats' not in state or not state['stats']:
        screen.fill('white')
        screen.image('img/logo.png')
        screen.text(
            'Loading...',
            xy=(160, 220),
            font_size=12,
            color='white',
        )
        return
    
    if state['screen'] == 'main':
        showMain()

tingbot.run()