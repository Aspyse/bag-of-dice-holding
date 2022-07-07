import re
import random

def roll(command):
    command = cleanroll(command)
    dice = command.split('+')
    rolls = []
    total = 0
    for die in dice:
        if 'd' not in die:
            total += int(die)
        else:
            bonk = die.split('d')
            for i in range(int(bonk[0])):
                bruh = random.randint(1,int(bonk[1]))
                rolls.append(bruh)
                total += bruh

    return (command, rolls, total)

def cleanroll(command):
    command.strip()
    command = re.sub("[^d0-9+]","", command)
    return command