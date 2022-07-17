import re
import random

async def rollnotation(notation):
    notation = await cleanroll(notation)

    addgroup = notation.split('+')
    rolls = []
    total = 0

    for add in addgroup:
        subgroup = add.split('-')
        groupdiff = 0
        for sub in range(len(subgroup)):
            advantage = await advtonum(subgroup[sub])
            subgroup[sub] = re.sub("[AD]","", subgroup[sub])
            if 'd' not in subgroup[sub]:
                if sub == 0:
                    groupdiff = int(subgroup[sub])
                else:
                    groupdiff -= int(subgroup[sub])

            else:
                rolltotal=0
                for i in range(int(subgroup[sub][0])):
                    roll = await rolldice(subgroup[sub])
                    rolls.append(roll)
                    rolltotal += roll
                if not advantage == 0:
                    advrolltotal=0
                    for i in range(int(subgroup[sub][0])):
                        advroll = await rolldice(subgroup[sub])
                        rolls.append(advroll)
                        advrolltotal += advroll
                    rolltotal = max(rolltotal*advantage, advrolltotal*advantage)*advantage
                    
                if sub == 0:
                    groupdiff += rolltotal
                else:
                    groupdiff -= rolltotal

        total += groupdiff

    return (notation, rolls, total)

async def rolldice(dice):
    dicesplit = dice.split('d')
    if dice[-1] == 'd':
        return 0
    if dice[0] == 'd':
        dicesplit.append(dicesplit[0])
        dicesplit[0] = 1
    for i in range(int(dicesplit[0])):
        roll = random.randint(1,int(dicesplit[1]))
    return roll

async def advtonum(advantage):
    if advantage[0] == 'A':
        return 1
    elif advantage[0] == 'D':
        return -1
    else:
        return 0

async def cleanroll(notation):
    notation.strip()
    notation = re.sub("[^d0-9+-AD]","", notation)
    notationsplit = notation.split('+')
    for add in notationsplit:
        subsplit = add.split('-')
        for sub in subsplit:
            sub.replace('d', 'R').replace('R', 'd', 1).replace('R', '')
        subjoin = '-'.join(subsplit)
    addjoin = '+'.join(notationsplit)
    return notation