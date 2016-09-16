# coding: utf-8
# v1.0

import tingbot
from tingbot import *
import urllib, json
import os, subprocess
import zipfile, shutil
from urlparse import urlparse

state = {}

screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

currentApp = 0

reqUrl = "http://ocean.tingbot.com/apps.json"
response = None

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

@touch()
def on_touch(action):
    if action == 'down':
        app = state['apps'][currentApp]
        screen.fill(color='black')
        screen.text(
            'Downloading %s...' % app['name'],
            font_size=14,
            color='white')

        screen.update()
        download_app(app)
        subprocess.check_call(['tbopen', app['path']])
        
@left_button.press
def on_left():
    previous_feed()

@right_button.press
def on_right():
    next_feed()

def next_feed():
    global currentApp
    
    currentApp = (currentApp + 1) % len(state['apps'])

def previous_feed():
    global currentApp
    
    currentApp = (currentApp - 1) % len(state['apps'])
    
@every(minutes=30)
def refresh_store():

    response = urllib.urlopen(reqUrl)
    apps = json.loads(response.read())
    state['apps'] = apps
    
    download_images()

def download_images():
    for app in state['apps']:
        url = 'http://ocean.tingbot.com' + app['icon']
        filename = '/tmp/int-' + os.path.basename(urlparse(url).path)

        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename)

        app['icon'] = Image.load_filename(filename)

def download_app(app):
    url = app['zip_url']
    filename = '/tmp/' + app['name'] + '.zip'

    if not os.path.exists(filename):
        urllib.urlretrieve(url, filename)
    
    with zipfile.ZipFile(filename, "r") as zf:
        for name in zf.namelist():
            localFilePath = zf.extract(name, os.environ.get('APPS_DIR', '/tmp/'))
            if localFilePath.endswith('.tingapp'):
                app_path = localFilePath
        
    #app_path = os.environ.get('APPS_DIR', '/apps/') + os.path.basename(app_path)
    
    #if not os.path.exists(app_path):
    #    shutil.move(app_filename, os.environ.get('APPS_DIR', '/apps/'))

    app['path'] = app_path

def showMain():
    app = state['apps'][currentApp]
    
    color = hex_to_rgb(app['background_color'])
    screen.fill(color=color)
        
    screen.text(
        "The tingbot ocean",
        xy=(10,15),
        align='left',
        color='white',
        font='font/Minecraftia-Regular.ttf',
        font_size=12,  
    )
    
    screen.image(app['icon'], xy=(160,90), scale=0.5)
    
    screen.text(
        app['name'],
        xy=(160, 160),
        color='white',
        font_size=18,
        font='font/JohnstonITCStd-Bold.ttf',
    )
    
    screen.text(
        app['creator'],
        xy=(160, 180),
        color='white',
        font_size=12,
        font='font/JohnstonITCStd-Bold.ttf',
    )
    
    screen.text(
        app['version'],
        xy=(160, 200),
        color='white',
        font_size=12,
        font='font/JohnstonITCStd-Bold.ttf',
    )
    
    screen.text(
        app['modified_date'],
        xy=(160, 220),
        color='white',
        font_size=12,
        font='font/JohnstonITCStd-Bold.ttf',
    )

@every(seconds=1.0/30)    
def loop():
    if 'apps' not in state:
        screen.fill(color='white')
        screen.text(
            "Ocean",
            color='black',
            font='font/Minecraftia-Regular.ttf',
            font_size=36,
        )
    
        screen.text(
            'Loading...',
            xy=(160, 180),
            font_size=12,
            color='black',
        )
        return

    if state['screen'] == 'main':
        showMain()

tingbot.run()