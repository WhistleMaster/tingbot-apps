# coding: utf-8
# v1.0.0

import tingbot
from tingbot import *

import pygame

import copy, random

BOXSIZE = 75
GAPSIZE = 4
BOARDWIDTH = 3
BOARDHEIGHT = 3

XOFFSET = 35
YOFFSET = 0

state = {}

screen_list = {
    0: 'main'
}
current_screen = 0
state['screen'] = screen_list[current_screen]

main_board = [[None, None, None], [None, None, None], [None, None, None]]
player_turn = random.choice('XO')
game_over = False
boxx = None
boxy = None

bot = False
start = True
first = True

@right_button.press
def on_rigt():
    reset()

@midleft_button.press
def on_midleft():
    reset()

@midright_button.press
def on_midright():
    reset()
    
@left_button.press
def on_left():
    reset()
    
@touch()
def on_touch(xy, action):
    if action == 'down':
        global boxx, boxy
        
        if not game_over and not start and not first:
            (x, y) = xy
            (boxx, boxy) = get_box_at_pixel(x, y)

@touch(size=(320, 240-44), align="bottom")
def on_touch(xy, action):
    if action == 'down':
        global first
        
        if game_over:
            reset()
        elif first:
            first = False
            screen.fill(color=(30, 160, 146))
        
@touch(size=(160,44), align='topleft')
def on_touch(xy, action):
    if action == 'down':
        global bot, start
        
        if start:
            bot = True
            start = False
            screen.fill(color=(30, 160, 146))

@touch(size=(160,44), align='topright')
def on_touch(xy, action):
    if action == 'down':
        global bot, start
        
        if start:
            bot = False
            start = False
            screen.fill(color=(30, 160, 146))
            
def reset():
    global main_board, game_over, player_turn, boxx, boxy, bot, start, first
    
    main_board = [[None, None, None], [None, None, None], [None, None, None]]
    player_turn = random.choice('XO')
    boxx = None
    boxy = None
    
    game_over = False
    start = True
    first = True
    
    bot = False

    screen.fill(color=(30, 160, 146))
    
def show_main():
    global main_board, boxx, boxy, player_turn, game_over, start
    
    if start:
        display_message("1 P                         2 P")
    elif first:
        display_message("%s starts" % player_turn)

    if not game_over and not start and not first:
        draw_board(main_board)
        
        if player_turn == 'O' and bot:
            (boxx, boxy) = get_bot_move(main_board)
    
        if boxx != None and boxy != None:
            if main_board[boxx][boxy] == None:
                main_board[boxx][boxy] = player_turn
                draw_XO(player_turn, boxx, boxy)
                
                if player_turn == 'X':
                    player_turn = 'O'
                else:
                    player_turn = 'X'
                
                if has_won(main_board):
                    if player_turn == 'X':
                        display_message('X winner!')
                    else:
                        display_message('O winner!')
                    game_over = True
                elif has_draw(main_board):
                    display_message('Draw!')
                    game_over = True

def display_message(message):
    screen.rectangle(
        align='top',
        size=(320,44),
        color='white',
    )
    
    screen.text(
        message,
        align='top',
        color=(38, 188, 172),
        font='font/Minecraftia-Regular.ttf',
        font_size=30,
    )

def get_box_at_pixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            (left, top) = left_top_coords_of_box(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
                
    return (None, None)

def draw_board(board):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            (left, top) = left_top_coords_of_box(boxx, boxy)
            screen.rectangle(
                    xy=(left,top),
                    align='topleft',
                    size=(BOXSIZE,BOXSIZE),
                    color=(38, 188, 172),
                )
            if board[boxx][boxy] != None:
                draw_XO(board[boxx][boxy], boxx, boxy)

def left_top_coords_of_box(boxx, boxy):
    left = boxx * (BOXSIZE + GAPSIZE) + GAPSIZE + XOFFSET
    top = boxy * (BOXSIZE + GAPSIZE) + GAPSIZE + YOFFSET
    return (left, top)

def get_bot_move(board):
    
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            board_copy = copy.deepcopy(board)
            if board_copy[boxx][boxy] == None:
                board_copy[boxx][boxy] = 'O'
                if has_won(board_copy):
                    return (boxx, boxy)
    
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            board_copy = copy.deepcopy(board)
            if board_copy[boxx][boxy] == None:
                board_copy[boxx][boxy] = 'X'
                if has_won(board_copy):
                    return (boxx, boxy)

    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            if board[boxx][boxy] == None:
                return (boxx, boxy)

    if board[1][1] == None:
        return (1, 1)
        
def draw_XO(player_turn, boxx, boxy):
    (left, top) = left_top_coords_of_box(boxx, boxy)
    if player_turn == 'X':
        screen.line(
            start_xy=(left + 3, top + 3), 
            end_xy=(left + BOXSIZE - 3, top + BOXSIZE - 3), 
            color='white', 
            width=4
        )
        screen.line(
            start_xy=(left + BOXSIZE - 3, top + 3), 
            end_xy=(left + 3, top + BOXSIZE - 3),
            color='white', 
            width=4
        )
    else:
        HALF = int(BOXSIZE / 2)
        pygame.draw.circle(screen.surface, (255, 255, 255), (left + HALF, top + HALF), HALF - 3, 4)

def has_won(board):
    
    for xrow in board:
        if xrow[0] != None and xrow[0] == xrow[1] and xrow[1] == xrow[2]:
            return True
        
        for i in range(3):
            if board[0][i] != None and board[0][i] == board[1][i] and board[1][i] == board[2][i]:
                return True
        
            if board[0][0] != None and board[0][0] == board[1][1] and board[1][1] == board[2][2]:
                return True
        
            if board[2][0] != None and board[2][0] == board[1][1] and board[1][1] == board[0][2]:
                return True
            
    return False

def has_draw(board):
    for i in board:
        if None in i:
            return False
    return True

@once()
def setup():
    
    screen.fill(color=(30, 160, 146))

@every(seconds=1.0/30)
def loop():
    if state['screen'] == 'main':
        show_main()
    
tingbot.run()