# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *
import lib.pywapi
import time

state = {}

screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

state['location'] = 'SZXX0013'
state['kphToMph'] = 1.60934400061

colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)

state['weather'] = None

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

@tingbot.every(minutes=10)
def refresh_data():
    state['weather'] = lib.pywapi.get_weather_from_weather_com(state['location'])
    return

def showMain():
    
    weather_com_result = state['weather']
    
    today = weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " + weather_com_result['forecasts'][0]['date'][4:] + " " + weather_com_result['forecasts'][0]['date'][:3]
    today_text = weather_com_result['current_conditions']['text']
    try: 
        int(weather_com_result['current_conditions']['wind']['speed'])
        windSpeed = int(weather_com_result['current_conditions']['wind']['speed'])
        currWind = weather_com_result['current_conditions']['wind']['text'] + " " + "{:.0f}".format(windSpeed) + " " + weather_com_result['units']['speed']
    except ValueError:
        windSpeed = weather_com_result['current_conditions']['wind']['speed']
        currWind = windSpeed
    currTemp = weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + weather_com_result['units']['temperature'] + " (" + weather_com_result['current_conditions']['feels_like'] + u'\N{DEGREE SIGN}' + weather_com_result['units']['temperature']+")"
    currPress = weather_com_result['current_conditions']['barometer']['reading'][:-3] + weather_com_result['units']['pressure']
    uv = "UV {}".format(weather_com_result['current_conditions']['uv']['text'])
    humid = "Hum {}%".format(weather_com_result['current_conditions']['humidity'])
    
    forecastDays = {}
    forecaseHighs = {}
    forecaseLows = {}
    forecastPrecips = {}
    forecastWinds = {}

    for i in range(0, 5):
    
        if not(weather_com_result['forecasts'][i]):
            break
        forecastDays[i] = weather_com_result['forecasts'][i]['day_of_week'][0:3] + " " + weather_com_result['forecasts'][i]['date'][4:]
        forecaseHighs[i] = weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "C"
        forecaseLows[i] = weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "C"
        forecastPrecips[i] = weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
        
        try:
            forecastWinds[i] = weather_com_result['forecasts'][i]['day']['wind']['text'] + " " + "{:.0f}".format(int(weather_com_result['forecasts'][i]['day']['wind']['speed']))
        except ValueError:
            forecastWinds[i] = weather_com_result['forecasts'][i]['day']['wind']['speed']

    screen.fill(color=(0,0,0))
    
    screen.text(
        time.strftime("%H"),
        xy=(235,33),
        align='left',
        color='white',
        font='font/DejaVuSansMono-Bold.ttf',
        font_size=66,  
    )
    screen.text(
        time.strftime("%M"),
        xy=(235,95),
        align='left',
        color='white',
        font='font/DejaVuSansMono-Bold.ttf',
        font_size=66, 
    )
    
    screen.image(
        "img/" + (weather_com_result['current_conditions']['icon']) + ".png",
        xy=(5, 55),
        align='left'
    )
    
    screen.text(
        today_text,
        xy=(65,115),
        align='center',
        color='white',
        font='font/DejaVuSansMono.ttf',
        font_size=14,
        max_width=115,
        max_lines=1
    )

    textAnchorX = 140
    textAnchorY = 15
    textYoffset = 20
    
    screen.text(
        today,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/DejaVuSansMono-Bold.ttf',
        font_size=14,  
    )
    textAnchorY+=textYoffset
    screen.text(
        currTemp,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/DejaVuSansMono.ttf',
        font_size=14,  
    )
    textAnchorY+=textYoffset
    screen.text(
        currWind,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/DejaVuSansMono.ttf',
        font_size=14,  
    )
    textAnchorY+=textYoffset
    screen.text(
        currPress,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/DejaVuSansMono.ttf',
        font_size=14,  
    )
    textAnchorY+=textYoffset
    screen.text(
        uv,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/DejaVuSansMono.ttf',
        font_size=14,  
    )
    textAnchorY+=textYoffset
    screen.text(
        humid,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/DejaVuSansMono.ttf',
        font_size=14,  
    )
    
    screen.line(start_xy=(8,130), end_xy=(310,130), width=1, color='grey')

    textAnchorX = 10
    textXoffset = 63
    
    for i in forecastDays:
        textAnchorY = 145
        screen.text(
            forecastDays[int(i)],
            xy=(textAnchorX,textAnchorY),
            align='left',
            color='white',
            font='font/DejaVuSansMono-Bold.ttf',
            font_size=14,  
        )
        textAnchorY+=textYoffset
        screen.text(
            forecaseHighs[int(i)],
            xy=(textAnchorX,textAnchorY),
            align='left',
            color='white',
            font='font/DejaVuSansMono.ttf',
            font_size=14,  
        )
        textAnchorY+=textYoffset
        screen.text(
            forecaseLows[int(i)],
            xy=(textAnchorX,textAnchorY),
            align='left',
            color='white',
            font='font/DejaVuSansMono.ttf',
            font_size=14,  
        )
        textAnchorY+=textYoffset
        screen.text(
            forecastPrecips[int(i)],
            xy=(textAnchorX,textAnchorY),
            align='left',
            color='white',
            font='font/DejaVuSansMono.ttf',
            font_size=14,  
        )
        textAnchorY+=textYoffset
        screen.text(
            forecastWinds[int(i)],
            xy=(textAnchorX,textAnchorY),
            align='left',
            color='white',
            font='font/DejaVuSansMono.ttf',
            font_size=14,  
        )
        textAnchorX+=textXoffset

@every(seconds=1.0/30)
def loop():
    if 'weather' not in state or not state['weather']:
        screen.fill(color='black')
        screen.text(
            'Loading...',
            xy=(160, 220),
            font_size=12,
            color='grey',
        )
        return
    
    if state['screen'] == 'main':
        showMain()

tingbot.run()