# coding: utf-8
# v1.1.0

import socket
import tingbot
from tingbot import *
import lib.pywapi
import time
import os

state = {}

screen_list = {
    0: 'main'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

state['location'] = 'SZXX0013'
state['kphToMph'] = 1.60934400061

state['weather'] = None

wind_code_mapper = {
    'N': u'#',
    'NNE': u'.',
    'NE': u'.',
    'ENE': u'.',
    'E': u'·',
    'ESE': u'?',
    'SE': u'?',
    'SSE': u'?',
    'S': u'¿',
    'SSW': u'"',
    'SW': u'"',
    'WSW': u'"',
    'W': u'\'',
    'WNW': u';',
    'NW': u';',
    'NNW': u';',
    'CALM': u'”',
    'VAR': u'{'
}

def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

@tingbot.every(minutes=10)
def refresh_data():
    state['weather'] = lib.pywapi.get_weather_from_weather_com(state['location'])
    return

def show_main():
    
    weather_com_result = state['weather']
    
    today = weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " + weather_com_result['forecasts'][0]['date'][4:] + " " + weather_com_result['forecasts'][0]['date'][:3]
    today_text = weather_com_result['current_conditions']['text']
    try:
        wind_speed = int(weather_com_result['current_conditions']['wind']['speed'])
        curr_wind = weather_com_result['current_conditions']['wind']['text'] + " " + "{:.0f}".format(wind_speed) + " " + weather_com_result['units']['speed']
    except ValueError:
        wind_speed = weather_com_result['current_conditions']['wind']['speed']
        curr_wind = wind_speed
    curr_temp = weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + weather_com_result['units']['temperature'] + " (Feels " + weather_com_result['current_conditions']['feels_like'] + u'\N{DEGREE SIGN}' + weather_com_result['units']['temperature']+")"
    curr_press = "Press {}".format(weather_com_result['current_conditions']['barometer']['reading'][:-3] + "" + weather_com_result['units']['pressure'])
    uv = "UV {}".format(weather_com_result['current_conditions']['uv']['text']) + " (Ind. {})".format(weather_com_result['current_conditions']['uv']['index'])
    humid = "Hum {}%".format(weather_com_result['current_conditions']['humidity'])
    
    forecast_days = {}
    forecase_highs = {}
    forecase_lows = {}
    forecast_precips = {}
    forecast_winds = {}

    for i in range(0, 5):
    
        if not(weather_com_result['forecasts'][i]):
            break
        forecast_days[i] = weather_com_result['forecasts'][i]['day_of_week'][0:3] + " " + weather_com_result['forecasts'][i]['date'][4:]
        forecase_highs[i] = weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + weather_com_result['units']['temperature']
        forecase_lows[i] = weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + weather_com_result['units']['temperature']
        forecast_precips[i] = weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
        
        try:
            forecast_winds[i] = "{:.0f}".format(int(weather_com_result['forecasts'][i]['day']['wind']['speed'])) + "" + weather_com_result['units']['speed']
        except ValueError:
            forecast_winds[i] = weather_com_result['forecasts'][i]['day']['wind']['speed']

    screen.fill(color=(0,0,0))
    
    screen.text(
        time.strftime("%H"),
        xy=(235,34),
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
    
    current_icon = "img/" + (weather_com_result['current_conditions']['icon']) + ".png"
    screen.image(
        current_icon,
        xy=(63, 53),
        align='center',
        scale=0.9
    )
    
    screen.text(
        today_text,
        xy=(63,115),
        align='center',
        color='white',
        font='font/Proxima_Nova_Regular.otf',
        font_size=14,
        max_width=115,
        max_lines=1
    )

    textAnchorX = 134
    textAnchorY = 15
    textYoffset = 20
    
    screen.text(
        today,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/Proxima_Nova_Bold.otf',
        font_size=14,
    )
    textAnchorY+=textYoffset
    screen.text(
        curr_temp,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/Proxima_Nova_Regular.otf',
        font_size=14,
    )
    textAnchorY+=textYoffset
    screen.text(
        wind_code_mapper[weather_com_result['current_conditions']['wind']['text']],
        xy=(textAnchorX,textAnchorY-6),
        align='left',
        color='white',
        font='font/artill_clean_icons.otf',
        font_size=30,
    )
    screen.text(
        weather_com_result['current_conditions']['wind']['text'],
        xy=(textAnchorX+20,textAnchorY-5),
        align='left',
        color='white',
        font='font/Proxima_Nova_Regular.otf',
        font_size=12,
    )
    screen.text(
        weather_com_result['current_conditions']['wind']['speed'] + "" + weather_com_result['units']['speed'],
        xy=(textAnchorX+20,textAnchorY+7),
        align='left',
        color='white',
        font='font/Proxima_Nova_Regular.otf',
        font_size=12,
    )
    textAnchorY+=textYoffset
    screen.text(
        curr_press,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/Proxima_Nova_Regular.otf',
        font_size=14,
    )
    textAnchorY+=textYoffset
    screen.text(
        uv,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/Proxima_Nova_Regular.otf',
        font_size=14,
    )
    textAnchorY+=textYoffset
    screen.text(
        humid,
        xy=(textAnchorX,textAnchorY),
        align='left',
        color='white',
        font='font/Proxima_Nova_Regular.otf',
        font_size=14,
    )
    
    screen.line(start_xy=(0,130), end_xy=(320,130), width=1, color='grey')
    #screen.line(start_xy=(126,0), end_xy=(126,130), width=1, color='grey')

    textAnchorX = 5
    textXoffset = 64
    
    for i in forecast_days:
        textAnchorY = 146
        small_icon = "img/" + (weather_com_result['forecasts'][int(i)]['day']['icon']) + ".png"
        if os.path.exists(small_icon):
            screen.image(
                small_icon,
                xy=(textAnchorX+23,textAnchorY),
                align='center',
                scale=0.2
            )
        else:
            screen.image(
                current_icon,
                xy=(textAnchorX+23,textAnchorY),
                align='center',
                scale=0.2
            )
        textAnchorY+=1
        textAnchorY+=textYoffset
        screen.text(
            forecast_days[int(i)],
            xy=(textAnchorX,textAnchorY),
            align='left',
            color='white',
            font='font/Proxima_Nova_Bold.otf',
            font_size=14,  
        )
        textAnchorY+=textYoffset
        screen.text(
            forecase_highs[int(i)],
            xy=(textAnchorX,textAnchorY),
            align='left',
            color='red',
            font='font/Proxima_Nova_Regular.otf',
            font_size=14,  
        )
        screen.text(
            forecase_lows[int(i)],
            xy=(textAnchorX+54,textAnchorY),
            align='right',
            color='blue',
            font='font/Proxima_Nova_Regular.otf',
            font_size=14,  
        )
        textAnchorY+=textYoffset
        screen.image(
            "img/icon_rain.png",
            xy=(textAnchorX-5,textAnchorY-1),
            align='left',
            scale=0.3
        )
        screen.text(
            forecast_precips[int(i)],
            xy=(textAnchorX+15,textAnchorY),
            align='left',
            color='white',
            font='font/Proxima_Nova_Regular.otf',
            font_size=14,
        )
        textAnchorY+=textYoffset
        screen.text(
            wind_code_mapper[weather_com_result['forecasts'][int(i)]['day']['wind']['text']],
            xy=(textAnchorX+5,textAnchorY-5),
            align='center',
            color='white',
            font='font/artill_clean_icons.otf',
            font_size=30,
        )
        screen.text(
            weather_com_result['forecasts'][int(i)]['day']['wind']['text'],
            xy=(textAnchorX+15,textAnchorY-5),
            align='left',
            color='white',
            font='font/Proxima_Nova_Regular.otf',
            font_size=11,
        )
        screen.text(
            forecast_winds[int(i)],
            xy=(textAnchorX+15,textAnchorY+5),
            align='left',
            color='white',
            font='font/Proxima_Nova_Regular.otf',
            font_size=11,
        )

        screen.line(start_xy=(textAnchorX-6,130), end_xy=(textAnchorX-6,240), width=1, color='grey')
        textAnchorX+=textXoffset

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
    if 'weather' not in state or not state['weather']:
        show_startup()
        return
    
    if state['screen'] == 'main':
        show_main()
 
socket.setdefaulttimeout(60)
tingbot.run()