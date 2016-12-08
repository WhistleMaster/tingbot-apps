# coding: utf-8
# v1.0.1

import tingbot
from tingbot import *
import urllib, json
import os, subprocess
import zipfile, shutil, hashlib
from urlparse import urlparse

state = {}

screen_list = {
    0: 'main'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

current_app = 0

req_url = "http://ocean.tingbot.com/apps.json"
response = None

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

@touch()
def on_touch(action):
    if action == 'down':
        app = state['apps'][current_app]
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
    global current_app
    
    current_app = (current_app + 1) % len(state['apps'])

def previous_feed():
    global current_app
    
    current_app = (current_app - 1) % len(state['apps'])
    
@every(minutes=30)
def refresh_store():

    response = urllib.urlopen(req_url)
    apps = json.loads(response.read())
    state['apps'] = apps
    
    download_images()

def download_images():
    for app in state['apps']:
        if not app['icon'].startswith('http'):
            url = 'http://ocean.tingbot.com' + app['icon']
        else:
            url = app['icon']

        sha = hashlib.sha1(url)
        filename = '/tmp/' + sha.hexdigest()
        
        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename)
            
        app['icon'] = Image.load_filename(filename)
        
        if app['icon'].size != (96, 96):
            resized_icon = Image(size=(96, 96))
            resized_icon.image(app['icon'], scale='shrinkToFit')
            app['icon'] = resized_icon

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

def show_main():
    app = state['apps'][current_app]
    
    if 'background_color' in app:
        color = hex_to_rgb(app['background_color'])
    else:
        color = hex_to_rgb('3a3a3c')
        
    screen.fill(color=color)
        
    screen.text(
        "The tingbot ocean",
        xy=(10,15),
        align='left',
        color='white',
        font='font/Minecraftia-Regular.ttf',
        font_size=12,  
    )

    screen.image(app['icon'], xy=(160,85))
    
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

def show_startup():
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
	
@every(seconds=1.0/30)
def loop():
    if 'apps' not in state:
        show_startup()
        return

    if state['screen'] == 'main':
        show_main()
        
tingbot.run()