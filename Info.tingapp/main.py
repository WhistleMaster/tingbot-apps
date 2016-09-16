# coding: utf-8

import tingbot
from tingbot import *
import os

import socket, fcntl, struct, math, time, platform

state = {}

screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

state['wifi'] = {}
state['wifi']['interface'] = 'wlan0'
state['info'] = {}

network_image = Image.load('img/network.png')
wifi_image = Image.load('img/wifi.png')

def kbytes_to_string(size,precision=2):
    suffixes=['KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1
        size = size/1024.0
    return "%.*f %s"%(precision,size,suffixes[suffixIndex])

@tingbot.every(minutes=1)
def refresh_info():
    temp = os.popen("vcgencmd measure_temp | awk -F= '{print $2}'").read().strip().split()
    state['info']['cpu_temp'] = temp[0][:-2]

    clock = os.popen("vcgencmd measure_clock arm | awk -F= '{print $2}'").read().strip()
    state['info']['cpu_clock'] = int(clock) / 1000**2

    state['info']['hostname'] = os.popen("hostname").read().strip()
    
    state['info']['cpu_model'] = os.popen("cat /proc/cpuinfo | grep -m 1 'model name' | awk -F: '{ print $2 }'").read().strip()
    
    state['info']['mem_total'] = os.popen("free | grep \"Mem:\" | awk '{ print $2 }'").read().strip()
    
    state['info']['mem_used'] = os.popen("free | grep \"Mem:\" | awk '{ print $3 }'").read().strip()
    
    state['info']['mem_free'] = os.popen("free | grep \"Mem:\" | awk '{ print $4 }'").read().strip()
    
    state['info']['swap_total'] = os.popen("free | grep \"Swap:\" | awk '{ print $2 }'").read().strip()
    
    state['info']['swap_used'] = os.popen("free | grep \"Swap:\" | awk '{ print $3 }'").read().strip()
    
    state['info']['swap_free'] = os.popen("free | grep \"Swap:\" | awk '{ print $4 }'").read().strip()

@tingbot.every(seconds=10)
def is_connected():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        state['network_found'] = 'Yes'
    except:
        state['network_found'] = 'No'

@tingbot.every(seconds=10)
def refresh_cpu_usage():
    state['info']['cpu_usage'] = os.popen("uptime | awk -F 'average:' '{ print $2}'").read().strip()

@tingbot.every(seconds=10)
def refresh_wifi_strength():
    f=os.popen('sudo iwconfig wlan0 | grep -e "Link Quality"')
    line = f.read().strip()

    splitted_line = line.split()
    link = splitted_line[1].split('=')
    signal = link[1].split('/')
    
    signal_level = signal[0]
    signal_total = signal[1]
    
    state['wifi']['quality'] = int(round(float(signal_level) / float(signal_total) * 100))
    
@tingbot.every(minutes=1)
def refresh_network():
    state['wifi']['ipaddress'] = os.popen("ifconfig %s | grep 'inet addr' | awk -F: '{print $2}' | awk '{print $1}'" % state['wifi']['interface']).read()
    state['wifi']['netmask'] = os.popen("ifconfig %s | grep 'Mask' | awk -F: '{print $4}'" % state['wifi']['interface']).read()
    state['wifi']['gateway'] = os.popen("route -n | grep '^0.0.0.0' | awk '{print $2}'").read()
    state['wifi']['ssid'] = os.popen("iwconfig %s | grep 'ESSID' | awk '{print $4}' | awk -F\\\" '{print $2}'" % state['wifi']['interface']).read()

def display_time():

    current_time = time.strftime("%H:%M")
    current_date = time.strftime("%d/%m/%Y")
    
    screen.text(
        current_time,
        xy=(10,10),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    screen.text(
        current_date,
        xy=(310,10),
        align='right',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    if 'info' not in state or not state['info']:
        return 
    
    screen.text(
        state['info']['hostname'],
        xy=(160,10),
        align='center',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )

def display_wifi_strength():
    
    if 'wifi' not in state or 'quality' not in state['wifi']:
        return
    
    quality = state['wifi']['quality']
    
    bars = []
    
    x_pos = 289
    y_pos = 28
    
    x_size = 2
    y_size = 3
    
    if quality > 75:
        bars.append('green')
        bars.append('green')
        bars.append('green')
        bars.append('green')
    elif quality > 50:
        bars.append( 'green')
        bars.append('green')
        bars.append('green')
        bars.append((16,85,45))
    elif quality > 25:
        bars.append('green')
        bars.append('green')
        bars.append((16,85,45))
        bars.append((16,85,45))
    elif quality > 0:
        bars.append('green')
        bars.append((16,85,45))
        bars.append((16,85,45))
        bars.append((16,85,45))
    
    screen.rectangle( xy=(x_pos,y_pos), align='topleft', size=(x_size,y_size), color=bars[0])
    
    y_size += 2
    x_pos += 5
    y_pos -= 2
    
    screen.rectangle( xy=(x_pos,y_pos), align='topleft', size=(x_size,5), color=bars[1])
    
    y_size += 2
    x_pos += 5
    y_pos -= 2
    
    screen.rectangle( xy=(x_pos,y_pos), align='topleft', size=(x_size,7), color=bars[2])
    
    y_size += 2
    x_pos += 5
    y_pos -= 2
    
    screen.rectangle( xy=(x_pos,y_pos), align='topleft', size=(x_size,9), color=bars[3])
    
    screen.text(
        "%s %%" % quality,
        xy=(263, 29),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
        
def display_network():
    
    if 'wifi' not in state or not state['wifi'] or 'network_found' not in state:
        return

    x_pos = 17
    y_pos = 30
    screen.text(
        state['wifi']['ssid'],
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=12,  
    )

    y_pos += 12 + 5
    screen.text(
        "Network",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos += 10
    screen.text(
        "IP address",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )

    y_pos += 10 
    screen.text(
        "Netmask",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )

    y_pos += 10
    screen.text(
        "Gateway",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos = 30
    
    y_pos += 12 + 5
    x_pos += 70
    screen.text(
        state['network_found'],
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos += 10
    screen.text(
        state['wifi']['ipaddress'],
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos += 10
    screen.text(
        state['wifi']['netmask'],
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos += 10
    screen.text(
        state['wifi']['gateway'],
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )

def display_info():
    
    if 'info' not in state or not state['info']:
        return

    x_pos = 17
    y_pos = 103
    screen.text(
        'CPU',
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=12,  
    )

    y_pos += 12 + 5
    screen.text(
        "Model",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos += 10
    screen.text(
        "Temp.",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )

    y_pos += 10 
    screen.text(
        "Clock",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )

    y_pos += 10
    screen.text(
        "Usage",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos = 103
    
    y_pos += 12 + 5
    x_pos += 70
    screen.text(
        state['info']['cpu_model'],
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    y_pos += 10
    screen.text(
        state['info']['cpu_temp'] + u' \N{DEGREE SIGN}C',
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    y_pos += 10
    screen.text(
        str(state['info']['cpu_clock']) + ' MHz',
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    y_pos += 10
    screen.text(
        state['info']['cpu_usage'],
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    ##########
    
    x_pos = 17
    y_pos = 176
    screen.text(
        "Memory",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=12,  
    )

    y_pos += 12 + 5
    screen.text(
        "Available",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos += 10
    screen.text(
        "Free",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )

    y_pos += 10 
    screen.text(
        "Used",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos = 176
    
    y_pos += 12 + 5
    x_pos += 70
    screen.text(
        kbytes_to_string(float(state['info']['mem_total'])),
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    y_pos += 10
    screen.text(
        kbytes_to_string(float(state['info']['mem_free'])),
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    y_pos += 10
    screen.text(
        kbytes_to_string(float(state['info']['mem_used'])),
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    ##########
    
    x_pos = 187
    y_pos = 176
    screen.text(
        "Swap",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=12,  
    )

    y_pos += 12 + 5
    screen.text(
        "Available",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos += 10
    screen.text(
        "Free",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )

    y_pos += 10 
    screen.text(
        "Used",
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,  
    )
    
    y_pos = 176
    
    y_pos += 12 + 5
    x_pos += 70
    screen.text(
        kbytes_to_string(float(state['info']['swap_total'])),
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    y_pos += 10
    screen.text(
        kbytes_to_string(float(state['info']['swap_free'])),
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )
    
    y_pos += 10
    screen.text(
        kbytes_to_string(float(state['info']['swap_used'])),
        xy=(x_pos,y_pos),
        align='left',
        color='green',
        font='font/Minecraftia-Regular.ttf',
        font_size=8,
    )

def showMain():
    display_time()
    
    screen.rectangle( xy=(10,17), align='topleft', size=(301,68), color='green')
    screen.rectangle( xy=(11,18), align='topleft', size=(299,66), color='black')
    
    display_network()
    display_wifi_strength()
    
    screen.rectangle( xy=(10,90), align='topleft', size=(301,68), color='green')
    screen.rectangle( xy=(11,91), align='topleft', size=(299,66), color='black')
    screen.rectangle( xy=(10,163), align='topleft', size=(301,68), color='green')
    screen.rectangle( xy=(11,164), align='topleft', size=(299,66), color='black')
    
    display_info()

@every(seconds=1.0/30)
def loop():
    if 'wifi' not in state or not state['wifi'] or 'info' not in state or not state['info']:
        screen.fill(color='black')
        screen.text(
            'Loading...',
            xy=(160, 120),
            font_size=12,
            color='green',
        )
        return
    
    if state['screen'] == 'main':
        showMain()

tingbot.run()
