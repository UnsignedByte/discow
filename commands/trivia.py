# @Author: Edmund Lam <edl>
# @Date:   18:59:11, 18-Apr-2018
# @Filename: trivia.py
# @Last modified by:   edl
# @Last modified time: 18:18:38, 11-Nov-2018


import requests
from base64 import b64decode
from enum import Enum
from discow.handlers import add_private_message_handler, bot_data, add_message_handler
from utils import msgutils, strutils
import asyncio
from discord import Embed
from commands.economy import increment, give, set_element
from random import randint
from commands.quiz import Question

print("\tInitializing Trivia Command")
print("\t\tCreating Trivia Classes")
def getCategories():
    categories = {}
    cats = requests.get('https://opentdb.com/api_category.php').json()['trivia_categories']
    for a in cats:
        categories[(a['name'].split(':', 1)[1].strip().lower() if ':' in a['name'] else a['name'].lower())] = a['id']
    return categories

class Data(Enum):
    difficulties = {
        'easy':'easy',
        'e':'easy',
        'medium':'medium',
        'm':'medium',
        'normal':'medium',
        'hard':'hard',
        'h':'hard',
        'difficult':'hard',
        'random':None,
        'r':None,
        'any':None
    }
    categories = getCategories()

class Trivia:
    def getquestion(self, category=None, difficulty=None, type=None, amount=1):
        obj = {k: v for k, v in locals().items() if v is not None}
        obj.update({'encode':'base64'})
        del obj['self']
        response = requests.get('https://opentdb.com/api.php', params=obj).json()
        if response['response_code'] == 0:
            return list({k: (list(b64decode(n).decode('utf-8') for n in v) if isinstance(v, list) else b64decode(v).decode('utf-8')) for k, v in x.items()} for x in response["results"])
        elif response['response_code'] == 1:
            return 'No results'
        elif response['response_code'] == 2:
            return 'Invalid Parameter'
        elif response['response_code'] == 3:
            return self.getquestion(category=category, difficulty=difficulty, type=type, amount=amount)
        elif response['response_code'] == 4:
            return self.getquestion(category=category, difficulty=difficulty, type=type, amount=amount)

triviaAPI = Trivia()
print("\t\tFinished Trivia Classes")

async def trivia(Bot, msg):
    cont = strutils.strip_command(msg.content)
    cont = (cont.split(' ') if ' ' in cont else [cont])
    diff = None
    cat = None
    if cont[0].lower() in Data.difficulties.value:
        diff = Data.difficulties.value[cont.pop(0).lower()]
    elif cont[-1].lower() in Data.difficulties.value:
        diff = Data.difficulties.value[cont.pop().lower()]
    cont = ' '.join(cont)
    if not cont.isspace():
        if cont.lower() in Data.categories.value:
            cat = Data.categories.value[cont.lower()]
        else:
            em = Embed(title="Unknown Category", description="Could not find the specified category. Valid categories include:\n\n"+'\n'.join(Data.categories.value.keys()), colour=0xff7830)
            await Bot.send_message(msg.channel, embed=em)
            return
    question = triviaAPI.getquestion(category=cat, difficulty=diff)[0]
    options = {question["correct_answer"]:True}
    options.update({(k, False) for k in question["incorrect_answers"]})
    questionOBJ = Question(question['question'], options, True)
    questionOBJ.optshuf()
    em = Embed(title="Trivia Question", description = questionOBJ.getstr(), colour=0xff7830)
    msgEmbed = await Bot.send_message(msg.channel, embed=em)
    def check(s):
        return len(s.content) == 1 and 0<=ord(s.content.lower())-ord('a')<len(options)
    response = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
    selection = ord(response.content.lower())-ord('a')
    em.description = questionOBJ.getstr(selected=selection, showCorrect=True)
    if list(questionOBJ.options.values())[selection] == True:
        increment(msg.author.id, "answerstreak", 1)
        reward = randint(0, 250*bot_data['user_data'][msg.author.id]['answerstreak']*(['easy', 'medium', 'hard'].index(question['difficulty'])+1))
        give(reward, msg.author.id)
        em.description+='\n\nYou answered correctly! Your answer streak is now `'+str(bot_data['user_data'][msg.author.id]['answerstreak'])+'` and you have recieved '+'{0:.2f}'.format(reward/100)+' Mooney!\nYou now have '+'{0:.2f}'.format(bot_data['user_data'][msg.author.id]["money"]/100)+' Mooney.'
    else:
        set_element(msg.author.id, "answerstreak", 0)
        em.description+='\n\nYour answer was incorrect! Your answer streak is now `0`.'
    await msgutils.edit_embed(Bot, msgEmbed, em)

add_message_handler(trivia, 'trivia')
add_private_message_handler(trivia, 'trivia')
print("\tTrivia Command Initialized")
