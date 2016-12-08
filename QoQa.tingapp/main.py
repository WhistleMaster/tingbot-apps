# coding: utf-8
# v1.0.1

import tingbot
from tingbot import *
import lib.feedparser
from urlparse import urlparse
import os
import urllib
import hashlib

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

def chunks(s, n):
    for start in range(0, len(s), n):
        yield s[start:start+n]
        
feed_list = {
    0: {'name': 'qoqa', 'url': 'http://www.qoqa.ch/fr/feed/product', 'type': 'product', 'color': (236,0,140)},
    1: {'name': 'qwine', 'url': 'http://www.qwine.ch/fr/feed/product', 'type': 'product', 'color': (160,25,92)},
    2: {'name': 'qsport', 'url': 'http://www.qsport.ch/fr/feed/product', 'type': 'product', 'color': (0,157,225)},
    3: {'name': 'qooking', 'url': 'http://www.qooking.ch/fr/feed/product', 'type': 'product', 'color': (255,141,79)},
    4: {'name': 'qwineprimeurs', 'url': 'http://www.qwineprimeurs.ch/fr/feed/product', 'type': 'product', 'color': (160,25,92)},
    5: {'name': 'qstyle', 'url': 'http://www.qstyle.ch/fr/feed/product', 'type': 'product', 'color': (235,0,141)},
    6: {'name': 'qids', 'url': 'http://www.qids.ch/fr/feed/product', 'type': 'product', 'color': (45,182,167)},
    7: {'name': 'qblog', 'url': 'http://www.qblog.ch/fr/feed/post', 'type': 'post', 'color': (235,0,138)},
}
current_feed = 0

state = {}

screen_list = {
    0: 'main'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

@left_button.press
def on_left():
    previous_feed()

@right_button.press
def on_right():
    next_feed()

def next_feed():
    global current_feed
    
    current_feed = (current_feed + 1) % len(feed_list)

def previous_feed():
    global current_feed
    
    current_feed = (current_feed - 1) % len(feed_list)

@every(minutes=10)
def refresh_feed():
    posts = []
    
    for feed in feed_list:
        d = lib.feedparser.parse(feed_list[feed]['url'])
        
        entry = d['entries'][0]
        
        post = {}
        post['title'] = entry['title']
        
        if feed_list[feed]['type'] == 'product':
            post['price'] = entry['g_price']
            post['availability'] = entry['g_availability']
        else:
            post['price'] = 'Qblog'
            post['availability'] = ''

        post['image_url'] = entry['media_content'][0]['url']
        
        posts.append(post)
    
    state['posts'] = posts
    
    download_images()

def download_images():
    for post in state['posts']:
        url = post['image_url']
        
        sha = hashlib.sha1(url)
        filename = '/tmp/' + sha.hexdigest()

        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename)

        post['image'] = Image.load_filename(filename)

def show_main():
    post = state['posts'][current_feed]
    image = post['image']

    width_sf = 320.0 / image.size[0]
    height_sf = 190.0 / image.size[1]

    sf = max(width_sf, height_sf)

    screen.fill(color='white')
    screen.image(
        image,
        xy=(160, 95),
        scale=sf)

    screen.rectangle(
        color=feed_list[current_feed]['color'],
        size=(320, 50),
        align='bottom',

    )
    
    screen.image(
        'img/' + feed_list[current_feed]['name'] + '.png',
        xy=(315, 5),
        align='topright',
        scale=0.3
    )
    
    if feed_list[current_feed]['type'] == 'product':
        title = post['title'].replace(unichr(9734), '|')
        title = title[0:title.index('|')-1]
        
        price = "CHF %s.-" % post['price']
    else:
        title = post['title']
        price = post['price']
    
    screen.text(
        truncate(title, 40),
        align='left',
        xy=(5, 225),
        color='white',
        font_size=14,
        font='font/JohnstonITCStd-Bold.ttf',
    )
    
    screen.text(
        price,
        align='left',
        xy=(5, 203),
        color='white',
        font_size=13,
        font='font/JohnstonITCStd-Bold.ttf',
    )
    
    screen.text(
        post['availability'],
        align='right',
        xy=(315, 200),
        color='white',
        font_size=13,
        font='font/OpenSans-Semibold.ttf',
    )

def show_startup():
    screen.fill(color='white')
    screen.image('img/' + feed_list[0]['name'] + '.png')
    screen.text(
        'Loading...',
        xy=(160, 180),
        font_size=12,
        color='black',
    )

@every(seconds=1.0/30)
def loop():
    if 'posts' not in state:
        show_startup()
        return

    if state['screen'] == 'main':
        show_main()
        
tingbot.run()