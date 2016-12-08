# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *

from lib.iwlist import *

state = {}

screen_list = {
    0: 'networks',
}
current_screen = 0
state['screen'] = screen_list[current_screen]

networks_list = 0
current_page = 0

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

@left_button.press
def on_left():
    previous_page()

@midleft_button.press
def on_midleft():
    next_page()

@touch(xy=(0,16), size=(45,31), align='left')
def on_touch(xy, action):
    if action == 'down':
         refresh_wifi_networks()
         
@touch(xy=(100,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        previous_page()
            
@touch(xy=(220,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        next_page()

@tingbot.every(seconds=30)
def refresh_wifi_networks():
    state['networks'] = parse(scan(interface='wlan0'))
    
def previous_page():
    global current_page
    
    if state['screen'] == 'networks':
        if networks_list != 0:
            current_page = (current_page - 4)
            if current_page < 0: current_page = current_page + 4
        show_wifi_networks()

def next_page():
    global current_page
    
    if state['screen'] == 'networks':
        if networks_list != 0:
            current_page = (current_page + 4)
            if current_page >= networks_list: current_page = current_page - 4
        show_wifi_networks()

def show_wifi_networks():
    global networks_list
    
    screen.fill(color=(26,26,26))
    
    screen.rectangle(
        xy=(0,16),
        align='left',
        size=(320,31),
        color=(145,220,90),
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
    
    screen.text(
        'Scan',
        xy=(10,17),
        align='left',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,    
    )
    
    networks = state['networks']
    networks_list = len(networks)
    
    pageNum = (networks_list + 4 - 1) // 4
    currentNum = (current_page + 4) // 4
        
    screen.text(
        'Networks (%s)' % networks_list,
        xy=(160, 15),
        align='center',
        color='white',
        font='font/Arial Rounded Bold.ttf',
        font_size=14, 
    )
    
    screen.text(
        "%s / %s" % (currentNum, pageNum),
        xy=(310,17),
        align='right',
        color='white',
        font='font/JohnstonITCStd-Light.ttf',
        font_size=14,
    )

    row_y = 31
    line_num = 1
    
    for i in range(current_page, networks_list):
        if line_num > 4:
            break
        
        network = networks[i]
        
        screen.rectangle(
            xy=(0,row_y),
            align='topleft',
            size=(320,51),
            color=(39,40,34),
        )
        
        ## 1

        screen.text(
            truncate(network['essid'], 15),
            xy=(10,row_y+12),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Bold.ttf',
            font_size=15,
        )
        
        screen.text(
            "Chan. %s" % network['channel'],
            xy=(180,row_y+12),
            align='center',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=15,
        )
        
        screen.text(
            "%s %s" % (network['frequency'], network['frequency_units']),
            xy=(315,row_y+12),
            align='right',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=15,
        )
        
        ## 2
        
        if network['encryption'] == "on":
            if 'wpa2' in network and 'wpa' in network:
                encryption = "WPA/WPA2"
            elif 'wpa2' in network:
                encryption = "WPA2"
            elif 'wpa' in network:
                encryption = "WPA"
            else:
                encryption = "WEP"
        else:
            encryption = "Open"
        
        screen.text(
            encryption,
            xy=(10,row_y+27),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=15,
        )
        
        if 'cipher' in network:
            screen.text(
                network['cipher'],
                xy=(180,row_y+27),
                align='center',
                color=(220,220,220),
                font='font/JohnstonITCStd-Light.ttf',
                font_size=15,
            )
            
        quality = int(round(float(network['signal_level']) / float(network['signal_total']) * 100))
        
        if quality <= 25:
            col = "red"
        elif quality <= 50:
            col = "yellow"
        elif quality <= 100:
            col = "green"
        
        screen.text(
            " %s %%" % quality,
            xy=(315,row_y+27),
            align='right',
            color=col,
            font='font/JohnstonITCStd-Light.ttf',
            font_size=15,
        )
        
        ## 3
        
        screen.text(
            network['mac'],
            xy=(10,row_y+42),
            align='left',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=15,
        )
        
        if 'auth' in network:
            screen.text(
                network['auth'],
                xy=(180,row_y+42),
                align='center',
                color=(220,220,220),
                font='font/JohnstonITCStd-Light.ttf',
                font_size=15,
            )
        
        screen.text(
            " %s dBm" % network['db'],
            xy=(315,row_y+42),
            align='right',
            color=(220,220,220),
            font='font/JohnstonITCStd-Light.ttf',
            font_size=15,
        )

        row_y += 52
        line_num += 1

def show_startup():
    screen.fill('white')
    screen.image('img/WiFi_startup.png', scale=0.6)
    screen.text(
        'Loading...',
        xy=(165, 195),
        font_size=12,
        color='black',
    )
	
@every(seconds=1.0/30)
def loop():
  
    if 'networks' not in state:
        show_startup()
        return
        
    if state['screen'] == 'networks':
        show_wifi_networks()

tingbot.run()