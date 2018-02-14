# coding: utf-8
# v1.0.1

import tingbot
from tingbot import *
import urllib, json
from datetime import datetime
from dateutil import parser
import time

state = {}

screen_list = {
    0: 'main'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

base_url = "http://" + tingbot.app.settings['IP'] + "/admin/"
req_url = None
response = None

stats_list = {
    0: {'name': 'Ads blocked', 'json': 'ads_blocked_today'},
    1: {'name': 'DNS queries', 'json': 'dns_queries_today'},
    2: {'name': 'Pi-holed', 'json': 'ads_percentage_today'},
    3: {'name': 'Domain list size', 'json': 'domains_being_blocked'},
}

@tingbot.every(minutes=1)
def refresh():
    req_url = base_url + "api.php"
    response = urllib.urlopen(req_url)
    
    state['stats'] = json.loads(response.read())
 
def show_main():
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
            stats_list[i]['name'],
            xy=(20,row_y+27),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=17,
        )
        
        if i == 2:
            statText = '%.2f%%' % state['stats'][stats_list[i]['json']]
        else:
            statText = state['stats'][stats_list[i]['json']]
        
        screen.text(
            statText,
            xy=(300,row_y+27),
            align='right',
            color='white',
            font='font/JohnstonITCStd-Bold.ttf',
            font_size=18,
        )

        row_y += 52
		
def show_startup():
    screen.fill('white')
    screen.image('img/logo.png')
    screen.text(
        'Loading...',
        xy=(160, 220),
        font_size=12,
        color='white',
    )
	
@every(seconds=1.0/30)
def loop():
    if 'stats' not in state or not state['stats']:
        show_startup()
        return
    
    if state['screen'] == 'main':
        show_main()

tingbot.run()