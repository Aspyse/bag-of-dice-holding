import re
import random

async def rolldice(notation):
    notation = await cleanroll(notation)

    dice = notation.split('+')
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

    return (notation, rolls, total)

async def cleanroll(notation):
    notation.strip()
    notation = re.sub("[^d0-9+]","", notation)
    return notation