# Tetris Blocks
# By: Angelo Hoeung
# This is a simple, pygame version of Tetris that allows players to place randomly generated blocks in a grid and earn points when an entire row is filled
# This is honestly pretty bad -> It's FULL of global variables

from pygame import *
from random import *
from math import *
from tkinter import *

screen = display.set_mode((1024,768))
init()

blocks = [[[1,1,1], # -> 3D list that outlines which squares are filled for each block
           [1,0,0]],
          [[2,2,2],
           [0,0,2]], # -> different numbers for each list to correspond with colours
          [[3,3,3],
           [0,3,0]],
          [[4,4],
           [4,4]],
          [[5,5,5,5]],
          [[6,6,0],
           [0,6,6]],
          [[0,7,7],
           [7,7,0]]]

block = choice(blocks) # current block
nBlock = choice(blocks) # next block
blockSize = 26
blockX = 512
blockY = 100
delayLR = 0 # delay for left, right, down
delayD = 0
score = 0
grid = [[0]*10 for i in range(20)] # 10 by 20 grid
pressed = False # for start screen
state = True # for pausing

#--------------------------IMAGES AND MUSIC-------------------------------------
green = transform.scale(image.load("images/green.png"),(blockSize,blockSize))
blue = transform.scale(image.load("images/blue.png"),(blockSize,blockSize))
cyan = transform.scale(image.load("images/cyan.png"),(blockSize,blockSize))
purple = transform.scale(image.load("images/purple.png"),(blockSize,blockSize))
orange = transform.scale(image.load("images/orange.png"),(blockSize,blockSize))
red = transform.scale(image.load("images/red.png"),(blockSize,blockSize))
yellow = transform.scale(image.load("images/yellow.png"),(blockSize,blockSize))
menu = image.load("images/menu.png")
lose = image.load("images/lose.png")
title = image.load("images/title.png")
pause = image.load("images/pause.png")
music = mixer.music.load("Tetris.mp3")
mixer.music.play(-1)
#-------------------------------------------------------------------------------

colours = [blue,orange,purple,yellow,cyan,green,red] # list of each colour block

def drawAll():
    screen.blit(title,(0,0)) # title screen

    for x in range(len(block)):
        for y in range(len(block[0])):
            if block[x][y] > 0: # fills in part of block if it's not 0
                screen.blit(colours[block[x][y] - 1],(blockX + x*blockSize,blockY + y*blockSize,blockSize,blockSize))
                # blits the block with its corresponding colour
                
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y] > 0:
                screen.blit(colours[grid[x][y] - 1],(512 - 5*blockSize + y*blockSize,100 + x*blockSize,blockSize,blockSize)) # fills in all elements in grid more than 0 and finds those block's colours in the colour list

    for x in range(11):
        for y in range(21):
            draw.line(screen,(214,212,211),(512 - 5*blockSize + x*blockSize,100),(512 - 5*blockSize + x*blockSize,100 + 20*blockSize)) # creates the grid lines
            draw.line(screen,(214,212,211),(512 - 5*blockSize,100 + y*blockSize),(512 + 5*blockSize,100 + y*blockSize))

    helvetica = font.SysFont("Helvetica",26,True)
    points = helvetica.render("Score: " + str(score),True,(255,255,255))
    nextBlock = helvetica.render("Next: ",True,(255,255,255))
    high = helvetica.render("High Score: " + str(readhighscore()),True,(255,255,255))
    screen.blit(high,(680,115))
    screen.blit(points,(680,145))
    screen.blit(nextBlock,(680,260)) # text displays score, highscore, and next

    for x in range(len(nBlock)):
        for y in range(len(nBlock[0])):
            if nBlock[x][y] > 0:
                screen.blit(colours[nBlock[x][y] - 1],(690 + x*blockSize,300 + y*blockSize,blockSize,blockSize)) # displays the next block on the right of the grid
    draw.rect(screen,(255,255,255),(688,298,blockSize*2 + 2,blockSize*4 + 2),2) # rect for where next block is
    
    if checkLoss():
        screen.blit(lose,(0,0)) # shows "you lose" when losing
        mixer.music.pause()

    display.flip()
                
# Rotates the block by rotating its list
def rotate():
    return [[block[y][x] for y in range(len(block))]
            for x in range(len(block[0])-1,-1,-1)] # Returns 2D list with length as amount of old rows, and length of each list as amount of old columns | Each element of each list is the last element of each old list grouped into seperate lists
                                                   # Example: [[1,1,1],[1,0,0]] would become [[1,0],[1,0],[1,1]]
# Detects the downward collision of each block
def collision():
    collide = False
    for x in range(len(block)):
        for y in range(len(block[0])):
            if block[x][y] > 0:
                if blockY >= bottom: # collision occurs when block is at bottom
                    collide = True
                elif blockY < bottom:
                    if grid[int((blockY - 100)/blockSize + y + 1)][int((blockX - (512 - 5*blockSize))/blockSize + x)] > 0: # this calculates the current location of the block in the grid. if there's a block below, collision occurs
                        collide = True

    if collide:
        for x in range(len(block)):
            for y in range(len(block[0])):
                if block[x][y] > 0:
                    grid[int((blockY - 100)/blockSize + y)][int((blockX - (512 - 5*blockSize))/blockSize + x)] = block[x][y] # the block stops falling when colliding
                        
    return collide

# Detects the left and right collision of each block
def LRcollide():
    for x in range(len(block)):
        for y in range(len(block[0])):
            if block[x][y] > 0:
                try: # I got this from w3schools.com. This basically tries to find if there's a block left or right of current block unless there is an index error, then there's no LR block collision
                    if grid[int((blockY - 100)/blockSize + y)][int((blockX - (512 - 5*blockSize))/blockSize + x - 1)] > 0:
                        return 1
                    if grid[int((blockY - 100)/blockSize + y)][int((blockX - (512 - 5*blockSize))/blockSize + x + 1)] > 0:
                        return 2
                except IndexError:
                    return 0
    if collision() or blockX == 512 and blockY == 100: # stops the player from never being able to move in certain instances
        return 0
    return 0

# New random block
def newBlock():
    block = choice(blocks) # random block
    delayLR = 0 # Added to prevent bug of not being able to move blocks under certain conditions
    delayD = 0
    return block

# Deletes full rows and shifts rows downwards
def clearRow():
    point = False
    for x in range(len(grid)):
        if 0 not in grid[x]: # entire row filled with blocks
            del grid[x]
            grid.insert(0,[0]*10) # deletes row and adds new blank one at top
            point = True # score will be increased
    return point

# Prevents block from rotating if there isn't enough room to do so
def rotateCollision():
    for x in range(len(rotate())):
        for y in range(len(rotate()[0])):
            if rotate()[x][y] > 0:
                try:
                    if grid[int((blockY - 100)/blockSize + y)][int((blockX - (512 - 5*blockSize))/blockSize + x)] > 0: # if the location that the rotation will be is already occupied, there is a collision
                        return True
                except IndexError: # when at the borders of the grid, there's a collision
                    return True
    return False

# Checks if the player loses
def checkLoss():
    if grid[len(block)-1][5] > 0: # the only way to lose is if the part where the block could be occupying (middle of grid, from top of grid to the block height) is occupied already
        return True
    return False

# Reads high score from text file
def readhighscore():
    file = open("highscore.txt","r")
    num = file.read()
    file.close()
    return int(num) # returns the number in highscore file

# Writes score to text file if score is higher
def writehighscore():
    if readhighscore() < score:
        file = open("highscore.txt","w")
        file.write(str(score)) # overwrites highscore if score is higher
        file.close()



running = True
myClock = time.Clock()
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                # quit() <- Was creating error
                running = False
                break
            if e.key == K_p:
                state = not state # pauses game
                screen.blit(pause,(1024/2 - 400,768/2 - 300))
                display.update()
            elif e.key == K_r and checkLoss():
                score = 0
                grid = [[0]*10 for i in range(20)]
                delayLR = 0
                delayD = 0
                mixer.music.play(-1)
            else:
                # state = True
                if e.key == K_UP:
                    if not collision() and not rotateCollision(): # rotates only when no collisions
                        '''if blockY + blockSize*len(rotate()[0]) > 100 + blockSize*20:
                            blockY = 100 + blockSize*20 - blockSize*len(rotate()[0])   
                        if blockX >= 512 + blockSize*len(rotate()[0]):
                            blockX = 512 + blockSize*(5 - len(rotate()))''' # this didn't work properly, but it allowed you to rotate at the right border of the grid
                        block = rotate()

    mb = mouse.get_pressed()
    keys = key.get_pressed()
    bottom = 100 + 20*blockSize - blockSize*len(block[0]) # the grid's bottom minus the block's height
    if state:
        
        if pressed == False:
            screen.blit(menu,(0,0)) # when not key pressed, shows menu
            display.update()
            
        if 1 in keys or 1 in mb: # mouse click or key pressed
            pressed = True
            
        if pressed: # starts game when anything pressed
            delayLR += 1
            if delayLR == 5: # delays the left and right movement
                if not collision():
                    if keys[K_RIGHT]:
                        if LRcollide() != 2: # allows right movement when no collision on right
                            blockX = min(blockX + blockSize,512 + 5*blockSize - blockSize*len(block)) # allows movement in increments and stops movement at right border
                    if keys[K_LEFT]:
                        if LRcollide() != 1: # allows left movement when no collision on left
                            blockX = max(blockX - blockSize,512 - 5*blockSize) # allows movement in increments and stops movement at left border
                    delayLR = 0

            if keys[K_DOWN]:
                speed = 5 # moves down automatically, and goes faster when pressing down
            else:
                speed = 30

            delayD += 1
            if delayD >= speed: # delays the down movement
                if not collision():
                    blockY += 26
                    delayD = 0

            if collision():
                block = nBlock
                nBlock = newBlock() # the block equals next block and next block is randomized
                blockX = 512 # block is at top centre
                blockY = 100
            
            if clearRow():
                score += 1 # when rows are cleared, adds to score

            writehighscore()
            drawAll()
            myClock.tick(60)

quit()
