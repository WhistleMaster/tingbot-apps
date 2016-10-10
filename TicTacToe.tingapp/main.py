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

screenList = {
    0: 'main'
}
currentScreen = 0
state['screen'] = screenList[currentScreen]

mainBoard = [[None, None, None], [None, None, None], [None, None, None]]
playerTurn = random.choice('XO')
gameOver = False
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
        
        if not gameOver and not start and not first:
            (x, y) = xy
            (boxx, boxy) = getBoxAtPixel(x, y)

@touch(size=(320, 240-44), align="bottom")
def on_touch(xy, action):
    if action == 'down':
        global first
        
        if gameOver:
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
    global mainBoard, gameOver, playerTurn, boxx, boxy, bot, start, first
    
    mainBoard = [[None, None, None], [None, None, None], [None, None, None]]
    playerTurn = random.choice('XO')
    boxx = None
    boxy = None
    
    gameOver = False
    start = True
    first = True
    
    bot = False

    screen.fill(color=(30, 160, 146))
    
def showMain():
    global mainBoard, boxx, boxy, playerTurn, gameOver, start
    
    if start:
        displayMessage("1 P                         2 P")
    elif first:
        displayMessage("%s starts" % playerTurn)

    if not gameOver and not start and not first:
        drawBoard(mainBoard)
        
        if playerTurn == 'O' and bot:
            (boxx, boxy) = getBotMove(mainBoard)
    
        if boxx != None and boxy != None:
            if mainBoard[boxx][boxy] == None:
                mainBoard[boxx][boxy] = playerTurn
                drawXO(playerTurn, boxx, boxy)
                
                if playerTurn == 'X':
                    playerTurn = 'O'
                else:
                    playerTurn = 'X'
                
                if hasWon(mainBoard):
                    if playerTurn == 'X':
                        displayMessage('X winner!')
                    else:
                        displayMessage('O winner!')
                    gameOver = True
                elif hasDraw(mainBoard):
                    displayMessage('Draw!')
                    gameOver = True

def displayMessage(message):
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

def getBoxAtPixel(x, y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            (left, top) = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
                
    return (None, None)

def drawBoard(board):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            (left, top) = leftTopCoordsOfBox(boxx, boxy)
            screen.rectangle(
                    xy=(left,top),
                    align='topleft',
                    size=(BOXSIZE,BOXSIZE),
                    color=(38, 188, 172),
                )
            if board[boxx][boxy] != None:
                drawXO(board[boxx][boxy], boxx, boxy)

def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * (BOXSIZE + GAPSIZE) + GAPSIZE + XOFFSET
    top = boxy * (BOXSIZE + GAPSIZE) + GAPSIZE + YOFFSET
    return (left, top)

def getBotMove(board):
    
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            board_copy = copy.deepcopy(board)
            if board_copy[boxx][boxy] == None:
                board_copy[boxx][boxy] = 'O'
                if hasWon(board_copy):
                    return (boxx, boxy)
    
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            board_copy = copy.deepcopy(board)
            if board_copy[boxx][boxy] == None:
                board_copy[boxx][boxy] = 'X'
                if hasWon(board_copy):
                    return (boxx, boxy)

    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            if board[boxx][boxy] == None:
                return (boxx, boxy)

    if board[1][1] == None:
        return (1, 1)
        
def drawXO(playerTurn, boxx, boxy):
    (left, top) = leftTopCoordsOfBox(boxx, boxy)
    if playerTurn == 'X':
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

def hasWon(board):
    
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

def hasDraw(board):
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
        showMain()
    
tingbot.run()