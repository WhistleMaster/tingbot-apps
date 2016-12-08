# coding: utf-8
# v1.0.1

import tingbot
from tingbot import *

import urllib2, urllib
from urlparse import urlparse
from datetime import datetime
import sys, os, re

import hashlib

state = {}

screen_list = {
    0: 'main'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

state['displayInfo'] = True
state['running'] = True

content_list = {
    0: {'name': 'National Geographic', 'url': 'http://photography.nationalgeographic.com/photography/photo-of-the-day'},
    1: {'name': 'NASA', 'url': 'http://apod.nasa.gov/apod'},
}
current_content= 0

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

@touch(xy=(70,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        previous_content() 
            
@touch(xy=(250,17), size=(20,32), align='center')
def on_touch(xy, action):
    if action == 'down':
        next_content()
    
@touch(xy=(0,16), size=(45,31), align='left')
def on_touch(xy, action):
    if action == 'down':
        toggle_running()
            
@touch(xy=(320,16), size=(45,31), align='right')
def on_touch(xy, action):
    if action == 'down':
        toggle_info()
        
@left_button.press
def on_left():
    previous_content()

@midleft_button.press
def on_midleft():
    next_content()

@midright_button.press
def on_midright():
    toggle_info()
    
@right_button.press
def on_rigt():
    toggle_running()
    
@every(seconds=10)
def play_content():

    if state['running']:
        next_content()

def next_content():
    global current_content
    
    current_content = (current_content + 1) % len(content_list)

def previous_content():
    global current_content
    
    current_content = (current_content - 1) % len(content_list)
    
def toggle_info():
    state['displayInfo'] = not state['displayInfo']

def toggle_running():
    state['running'] = not state['running']
    
@every(minutes=30)
def refresh_image():
    
    photos = []
    
    for content in content_list:
        photo = {}
        
        doc=urllib2.urlopen(content_list[content]['url'])
        site=doc.read()
        
        if content_list[content]['name'] == 'National Geographic':
            
            result=re.search("<meta property=\"og:image\" content=\"(.*?)\"/>",site,re.DOTALL)
            
            if result is not None:
                image_url=result.group(1)
                
                photo['image_url'] = image_url
                
                result=re.search("<meta property=\"og:title\" content=\"(.*?)\"/>",site,re.DOTALL)
                
                if result is not None:
                    photo['image_name'] = result.group(1)
                else:
                    photo['image_name'] = ''
                    
                photos.append(photo)
                    
        elif content_list[content]['name'] == 'NASA':
            result=re.search("<a href=\"(image.*?)\"",site,re.DOTALL)
                
            if result is not None:
                image_url=result.group(1)
                
                if not image_url.startswith('http'):
                    photo['image_url'] = 'http://apod.nasa.gov/apod/' + result.group(1)
                else:
                    photo['image_url'] = result.group(1)
                
                result=re.search("<meta name=\"keywords\" content=\"(.*?)\">",site,re.DOTALL)
                    
                if result is not None:
                    photo['image_name'] = result.group(1)
                else:
                    photo['image_name'] = ''
                    
                photos.append(photo)
                
    state['photos'] = photos
    
    download_images()

def download_images():
    for photo in state['photos']:
        url = photo['image_url']
        
        sha = hashlib.sha1(url)
        filename = '/tmp/' + sha.hexdigest()

        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename)

        photo['image'] = Image.load_filename(filename)

def show_main():
    photo = state['photos'][current_content]
    image = photo['image']

    width_sf = 320.0 / image.size[0]
    height_sf = 240.0 / image.size[1]

    sf = max(width_sf, height_sf)

    screen.image(image, scale=sf)
    
    if state['displayInfo']:
        screen.rectangle(
            xy=(0,16),
            align='left',
            size=(320,31),
            color='black',
        )
        
        screen.text(
            content_list[current_content]['name'],
            xy=(160, 15),
            align='center',
            color='white',
            font='font/Arial Rounded Bold.ttf',
            font_size=14, 
        )
        
        if state['running']:
            startStop = 'Stop'
        else:
            startStop = 'Start'
        
        screen.text(
            startStop,
            xy=(10,17),
            align='left',
            color='white',
            font='font/JohnstonITCStd-Light.ttf',
            font_size=14,    
        )
        
        screen.text(
            'Hide',
            xy=(310,17),
            align='right',
            color='white',
            font='font/JohnstonITCStd-Light.ttf',
            font_size=14,   
        )
        
        screen.image(
            'img/left.png',
            xy=(70, 15),
            align='center'
        )
        screen.image(
            'img/right.png',
            xy=(250, 15),
            align='center'
        )
        
        screen.rectangle(
            color='black',
            size=(320, 20),
            align='bottom',
        )
        
        screen.text(
            truncate(photo['image_name'], 40),
            align='left',
            xy=(5, 231),
            color='white',
            font_size=14,
            font='font/JohnstonITCStd-Light.ttf',
        )

def show_startup():
    screen.fill(color='black')
    screen.text(
        'Loading...',
        xy=(160, 225),
        font_size=12,
        color='white',
    )
	
@every(seconds=1.0/30)
def loop():
    if 'photos' not in state:
        show_startup()
        return
    
    if state['screen'] == 'main':
        show_main()

tingbot.run()