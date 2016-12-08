# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *

import os
import urllib
import hashlib
import requests, json
import threading
import pygame

from urlparse import urlparse
from HTMLParser import HTMLParser

import lib.prettydate
import lib.image

loading_thread = None

feed_list = tingbot.app.settings['feed_list']

current_feed = 0
current_post = 0

state = {}

screen_list = {
    0: 'main'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

state['scale'] = 'fit'

@touch()
def on_touch(action):
    if action == 'down':
        if state['scale'] == 'fit':
            state['scale'] = 'fill'
        else:
            state['scale'] = 'fit'

@midleft_button.press
def on_left():
    previous_feed()

@midright_button.press
def on_right():
    next_feed()
    
@left_button.press
def on_left():
    previous_post()

@right_button.press
def on_right():
    next_post()

def next_post():
    global current_post
    
    current_post = (current_post + 1) % len(state['posts'])

def previous_post():
    global current_post
    
    current_post = (current_post - 1) % len(state['posts'])
    
def next_feed():
    global current_feed, current_post, state, loading_thread
    
    current_feed = (current_feed + 1) % len(feed_list)
    current_post = 0
    
    state['posts'] = None
    
    loading_thread = threading.Thread(target=refresh_feed, args=())
    loading_thread.start()

def previous_feed():
    global current_feed, current_post, state, loading_thread
    
    current_feed = (current_feed - 1) % len(feed_list)
    current_post = 0
    
    state['posts'] = None
    
    loading_thread = threading.Thread(target=refresh_feed, args=())
    loading_thread.start()

@every(minutes=10)
def refresh_feed():

    req = requests.get(feed_list[current_feed]['url'], headers = {'User-agent': 'Tingbot agent'})
    
    response = req.json()
    decoded = json.dumps(response)
    deco = json.loads(decoded)
    
    state['posts'] = deco['data']['children']
    
    download_images()

def download_images():
    for post in state['posts']:
        if 'preview' in post['data']:
            url = HTMLParser().unescape(post['data']['preview']['images'][0]['source']['url'])
    
            sha = hashlib.sha1(url)
            filename = '/tmp/' + sha.hexdigest()
    
            if not os.path.exists(filename):
                urllib.urlretrieve(url, filename)
                
            post['image'] = pygame.image.load(filename)

def show_startup():
    screen.fill(color='white')
    screen.image('img/logo_reddit.png')
    screen.text(
        'Loading...',
        xy=(160, 180),
        font_size=12,
        color='black',
    )
    
def show_loading():
    screen.fill(color=(255, 69, 0))
    screen.image('img/reddit.png', scale=0.5)
    screen.text(
        'Loading %s...' % feed_list[current_feed]['name'],
        xy=(160, 180),
        font_size=12,
        color='white'
    )
    screen.update()
    
def show_main():
    screen.fill(color='white')
    
    post = state['posts'][current_post]['data']

    if 'image' in state['posts'][current_post]:
        image_blur = lib.image.blurSurf(state['posts'][current_post]['image'], 50)
        screen.image(image_blur, xy=(160,113), max_width=320, max_height=240, scale='fill')
        
        image = state['posts'][current_post]['image']
        screen.image(image, xy=(160,113), max_width=320, max_height=185, scale=state['scale'])
        
        if state['scale'] == 'fill':
            screen.image('img/magnifier.png', xy=(310,30), scale=0.5)
        
        screen.update()
    else:
        screen.image('img/tw__ic_tweet_photo_error_light.png', xy=(160,113))

    screen.rectangle(
        color=(255, 69, 0),
        size=(320, 20),
        align='top',
    )
    
    screen.image('img/notification_reddit.png', xy=(5,9), align="left", scale=0.7)
    
    screen.text(
        'r/' + post['subreddit'] + u' • ' + lib.prettydate.pretty_date(float(post['created_utc'])),
        align='left',
        xy=(26, 11),
        color='white',
        font_size=12,
        font='font/Proxima_Nova_Regular.otf',
    )
    
    screen.text(
        '%s / %s | %s' % (current_post+1, len(state['posts']), feed_list[current_feed]['name']),
        align='right',
        xy=(315, 11),
        color='white',
        font_size=12,
        font='font/Proxima_Nova_Regular.otf',
    )
    
    screen.rectangle(
        color=(255, 69, 0),
        size=(320, 35),
        align='bottom',
    )
    
    screen.text(
        post['title'].encode('ascii', 'ignore').decode('ascii'),
        align='topleft',
        xy=(5, 209),
        color='white',
        font_size=12,
        font='font/Proxima_Nova_Regular.otf',
        max_width=310,
        max_lines=2
    )
    
@every(seconds=1.0/30)
def loop():
    if 'posts' not in state:
        show_startup()
        return
    elif not state['posts']:
        show_loading()
        return

    if state['screen'] == 'main':
        show_main()
        
tingbot.run()