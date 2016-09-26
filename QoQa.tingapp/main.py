# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *
import lib.feedparser
from urlparse import urlparse
import os
import urllib

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

def chunks(s, n):
    for start in range(0, len(s), n):
        yield s[start:start+n]
        
feedList = {
    0: {'feedName': 'qoqa', 'feedUrl': 'http://www.qoqa.ch/fr/feed/product', 'feedType': 'product', 'feedColor': (236,0,140)},
    1: {'feedName': 'qwine', 'feedUrl': 'http://www.qwine.ch/fr/feed/product', 'feedType': 'product', 'feedColor': (160,25,92)},
    2: {'feedName': 'qsport', 'feedUrl': 'http://www.qsport.ch/fr/feed/product', 'feedType': 'product', 'feedColor': (0,157,225)},
    3: {'feedName': 'qooking', 'feedUrl': 'http://www.qooking.ch/fr/feed/product', 'feedType': 'product', 'feedColor': (255,141,79)},
    4: {'feedName': 'qwineprimeurs', 'feedUrl': 'http://www.qwineprimeurs.ch/fr/feed/product', 'feedType': 'product', 'feedColor': (160,25,92)},
    5: {'feedName': 'qstyle', 'feedUrl': 'http://www.qstyle.ch/fr/feed/product', 'feedType': 'product', 'feedColor': (235,0,141)},
    6: {'feedName': 'qids', 'feedUrl': 'http://www.qids.ch/fr/feed/product', 'feedType': 'product', 'feedColor': (45,182,167)},
    7: {'feedName': 'qblog', 'feedUrl': 'http://www.qblog.ch/fr/feed/post', 'feedType': 'post', 'feedColor': (235,0,138)},
}
currentFeed = 0

state = {}

screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

@left_button.press
def on_left():
    previous_feed()

@right_button.press
def on_right():
    next_feed()

def next_feed():
    global currentFeed
    
    currentFeed = (currentFeed + 1) % len(feedList)

def previous_feed():
    global currentFeed
    
    currentFeed = (currentFeed - 1) % len(feedList)

@every(minutes=10)
def refresh_feed():
    posts = []
    
    for feed in feedList:
        d = lib.feedparser.parse(feedList[feed]['feedUrl'])
        
        entry = d['entries'][0]
        
        post = {}
        post['title'] = entry['title']
        
        if feedList[feed]['feedType'] == 'product':
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
        filename = '/tmp/int-' + os.path.basename(urlparse(url).path)

        if not os.path.exists(filename):
            urllib.urlretrieve(url, filename)

        post['image'] = Image.load_filename(filename)

def showMain():
    post = state['posts'][currentFeed]
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
        color=feedList[currentFeed]['feedColor'],
        size=(320, 50),
        align='bottom',

    )
    
    screen.image(
        'img/' + feedList[currentFeed]['feedName'] + '.png',
        xy=(315, 5),
        align='topright',
        scale=0.3
    )
    
    if feedList[currentFeed]['feedType'] == 'product':
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
    
@every(seconds=1.0/30)
def loop():
    if 'posts' not in state:
        screen.fill(color='white')
        screen.image('img/' + feedList[0]['feedName'] + '.png')
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
