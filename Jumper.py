#Jumper
#Jump over baddies as they come at you
#By Collin Maryniak (omegaxk314@gmail.com)

import pygame, sys, random
from pygame.locals import *

pygame.init()
mainclock = pygame.time.Clock()

#Set up the window
WINDOWWIDTH = 1200 #Default is 1200
WINDOWHEIGHT = 900 #Default is 900
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Jumper')

center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)

#Colors
BLACK = (0, 0, 0)
MAGENTA = (255, 0, 255)

#Load Assets
bgimg = pygame.image.load('Resources/arcade background.png').convert_alpha()
bgimg = pygame.transform.scale(bgimg, (WINDOWWIDTH, WINDOWHEIGHT))

playerimg = pygame.image.load('Resources/player.png').convert_alpha()
playerrect = playerimg.get_rect()
playerrect.center = (center)

baddieimg = pygame.image.load('Resources/baddie.png').convert_alpha()

font = 'freesansbold.ttf'

bgmusic = pygame.mixer.music.load('Resources/Boss battle theme EXE (1).wav')

#Game constants
baddieminsize = 20
baddiemaxsize = 40
baddieminspeed = 6
baddiemaxspeed = 8
baddiespawnrate = 140
baddies = []
bframe = 0
gravity = 1.4
fps = 60
pmh = center[0] + 100
jumpheight = -18

game_over = False

def main():
	pygame.mixer.music.play(-1, 0.0)
	waitforstart()
	while True:
		rungame()
		gameover()


def rungame():
	global score, playery, fallspeed, game_over, baddieminspeed, baddiemaxspeed, baddies

	#Reset the game variables
	score = 0
	playery = pmh
	fallspeed = 0
	game_over = False
	baddieminspeed = 6
	baddiemaxspeed = 8
	diff = 1
	baddies = []
	nextdiff = diff + 300

	DISPLAYSURF.blit(bgimg, (0, 0))
	playerrect.center = (center[0], playery)
	DISPLAYSURF.blit(playerimg, playerrect)
	pygame.display.update()

	#Game loop
	while True: 
		if not game_over:
			for event in pygame.event.get(): #Event handling loop
				if event.type == QUIT:
					terminate()
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						terminate()
					if event.key == K_SPACE:
						#Make sure the player is not in the air before letting him jump
						if not playery < pmh:
							fallspeed = jumpheight

				if event.type == MOUSEBUTTONDOWN:
					#Make sure the player is not in the air before letting him jump
					if not playery < pmh:
						fallspeed = jumpheight

			DISPLAYSURF.blit(bgimg, (0, 0))

			#Display the player
			player_gravity()
			playerrect.center = (center[0], playery)
			DISPLAYSURF.blit(playerimg, playerrect)

			#Add the baddies and display them
			getnewbaddie()
			drawbaddies()
			movebaddie()

			#Draw the score text
			drawtext('Score: ' + str(score), font, 20, DISPLAYSURF, WINDOWWIDTH - 75, 20, MAGENTA)

			#Use diff and nextdiff to amp up the difficulty every couple of seconds
			diff += 1
			if diff > nextdiff:
				nextdiff = 500
				diff = 0
				baddiemaxspeed += 3
				baddieminspeed += 3

			pygame.display.update()
			mainclock.tick(fps)

		else:
			return


def waitforstart():
	#Draws the instructions on the screen and waits for a player to press a key
	DISPLAYSURF.blit(bgimg, (0, 0))
	drawtext('INSTRUCTIONS', font, 40, DISPLAYSURF, center[0], center[1] - 160, MAGENTA)
	drawtext('Press space or click the mouse to jump. The goal is to jump over the green baddies without being hit.', font, 20, DISPLAYSURF, center[0], center[1] - 100, MAGENTA)
	drawtext('The baddies will come at you quickly. The baddies will get faster the longer you have survived.', font, 20, DISPLAYSURF, center[0], center[1] - 60, MAGENTA)
	drawtext('Press any key to start', font, 40, DISPLAYSURF, center[0], center[1], MAGENTA)
	pygame.display.update()
	waitforkeypress()
	return


def gameover():
	#Fill the screen black so you can't see the sprites, then add the background image
	DISPLAYSURF.fill(BLACK)
	DISPLAYSURF.blit(bgimg, (0, 0))
	update_high_scores()
	display_high_scores()
	drawtext('Game Over', font, 60, DISPLAYSURF, center[0], center[1] - 300, MAGENTA)
	drawtext('Press "r" to restart, or press "q" to quit.', font, 25, DISPLAYSURF, center[0], center[1] + 140, MAGENTA)
	target = ''
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			if event.type == KEYUP:
				if event.key == K_ESCAPE or event.key == K_q: 
					terminate()
				if event.key == K_r:
					target = 'restart' #Set the target to "restart" so the function knows to stop
					break

		if target == 'restart':
			return

		pygame.display.update()
		mainclock.tick(fps)


def update_high_scores():
	#Adds your score to the leaderboard if it is a high score
	global score, scores
	filename = r"resources/jumper high-scores.txt"
	scores = []
	with open(filename, "r") as file:
		line = file.readline()
		high_scores = line.split()
		for high_score in high_scores:
			if (score > int(high_score)):
				scores.append(str(score) + " ")
				score = int(high_score)
			else:
				scores.append(str(high_score) + " ")

	with open(filename, "w") as file:
		for high_score in scores:
			file.write(high_score)


def display_high_scores():
	global scores
	drawtext("HIGH SCORES", font, 40, DISPLAYSURF, center[0], center[1] - 200, MAGENTA)
	y = center[1] - 135
	position = 1
	#Draw the leaderboard
	for high_score in scores:
		drawtext(str(position) + ". " + high_score, font, 40, DISPLAYSURF, center[0], y, MAGENTA)
		#Increase y and position so the next score is displayed correctly
		y += 50
		position += 1


def movebaddie():
	global score, game_over

	#Moves baddies and checks if they collided with the player
	for baddie in baddies:
		baddie[0].x -= baddie[2] #Uses the third item in the list to find the baddie's speed
		if baddie[0].x < 0:
			score += 1
			baddies.remove(baddie)

		if baddie[0].colliderect(playerrect):
			game_over = True


def drawbaddies():
	for baddie in baddies: 
		newbaddieimg = pygame.transform.scale(baddieimg, (baddie[1], baddie[1])) #Use the second item in the list to set the size
		DISPLAYSURF.blit(newbaddieimg, baddie[0]) #Use the first item in the list as the rect object


def addnewbaddie():
	global baddies

	#Set up the new baddie's rect values
	newbaddie = baddieimg.get_rect()
	newbaddie.x = WINDOWWIDTH - 5
	newbaddie.bottom = pmh

	#Set the new baddie's size and speed
	newbaddiesize = random.randint(baddieminsize, baddiemaxsize)
	newbaddiespeed = random.randint(baddieminspeed, baddiemaxspeed)

	#Combine the rect, size, and speed into a list and add it to the baddies list
	baddielist = [newbaddie, newbaddiesize, newbaddiespeed]
	baddies.append(baddielist)


def getnewbaddie():
	global bframe

	#Basic frame loop that adds a new baddie every couple of frames
	if bframe > baddiespawnrate:
		addnewbaddie()
		bframe = 0
	else:
		bframe += random.randint(1, 5)


def player_gravity():
	global playery, fallspeed 

	playery += fallspeed
	#If player is above normal y pos, then change fallspeed to move him down
	if playery < pmh:
		fallspeed += gravity
	else:
		fallspeed = 0 #Set fallspeed to 0 so the player stops falling
	

def terminate():
	pygame.quit()
	sys.exit()


def waitforkeypress():
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					terminate()
				return


def drawtext(text, font, size, surface, x, y, color):
    fontobj = pygame.font.Font(font, size)
    textobj = fontobj.render(text, size, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


if __name__ == '__main__':
	main()
