# @Author: Edmund Lam <edl>
# @Date:   18:59:11, 18-Apr-2018
# @Filename: fun.py
# @Last modified by:   edl
# @Last modified time: 19:59:33, 04-Nov-2018


import asyncio
from utils import msgutils, strutils
from discow.handlers import add_message_handler
from discord import Embed
from random import randint, shuffle, choice
import requests as req
from bs4 import BeautifulSoup
import re
import string

print("\tInitializing Fun Commands")

async def invite(Bot, msg):
    inv = await Bot.create_invite(msg.channel, max_age=360, max_uses=0, unique=False)
    outstr = "You have been invited to **"+msg.server.name+"**!\nJoin with this link:\n"+inv.url
    await Bot.send_message(msg.channel, outstr)

async def rps(Bot, msg):
    valid = ["rock", "paper", "scissors"]
    mine = valid[randint(0, 2)]
    yours = strutils.parse_command(msg.content, 1)[1]
    result = ""
    if mine == yours:
        result = "It's a tie!"
    else:
        comb = mine+yours
        if comb in ["rockpaper", "scissorsrock", "paperscissors"]:
            result = strutils.format_response("{_mention} wins!", _msg=msg)
        else:
            result = "I win!"
    if yours in valid:
        await Bot.send_message(msg.channel, strutils.format_response("**{_mention}** chooses **{yours}**, while I choose **{mine}**. {result}", yours=yours, mine=mine, _msg = msg, result=result))
    else:
        await Bot.send_message(msg.channel, "Your input was invalid. Please choose **rock**, **paper**, or **scissors.**")

#From https://github.com/UnsignedByte/Thesaurus-er
async def thesaurus(Bot, msg):
    #Taken from https://stackoverflow.com/questions/19790188/expanding-english-language-contractions-in-python
    contractions = {
    "ain't": ["am not", "are not", "is not", "has not", "have not"],
    "aren't": ["are not", "am not"],
    "can't": ["cannot"],
    "can't've": ["cannot have"],
    "'cause": ["because"],
    "could've": ["could have"],
    "couldn't": ["could not"],
    "couldn't've": ["could not have"],
    "didn't": ["did not"],
    "doesn't": ["does not"],
    "don't": ["do not"],
    "hadn't": ["had not"],
    "hadn't've": ["had not have"],
    "hasn't": ["has not"],
    "haven't": ["have not"],
    "he'd": ["he had", "he would"],
    "he'd've": ["he would have"],
    "he'll": ["he shall: [he will"],
    "he'll've": ["he shall have", "he will have"],
    "he's": ["he has", "he is"],
    "how'd": ["how did"],
    "how'd'y": ["how do you"],
    "how'll": ["how will"],
    "how's": ["how has", "how is", "how does"],
    "I'd": ["I had", "I would"],
    "I'd've": ["I would have"],
    "I'll": ["I shall", "I will"],
    "I'll've": ["I shall have", "I will have"],
    "I'm": ["I am"],
    "I've": ["I have"],
    "isn't": ["is not"],
    "it'd": ["it had", "it would"],
    "it'd've": ["it would have"],
    "it'll": ["it shall", "it will"],
    "it'll've": ["it shall have", "it will have"],
    "it's": ["it has", "it is"],
    "let's": ["let us"],
    "ma'am": ["madam"],
    "mayn't": ["may not"],
    "might've": ["might have"],
    "mightn't": ["might not"],
    "mightn't've": ["might not have"],
    "must've": ["must have"],
    "mustn't": ["must not"],
    "mustn't've": ["must not have"],
    "needn't": ["need not"],
    "needn't've": ["need not have"],
    "o'clock": ["of the clock"],
    "oughtn't": ["ought not"],
    "oughtn't've": ["ought not have"],
    "shan't": ["shall not"],
    "sha'n't": ["shall not"],
    "shan't've": ["shall not have"],
    "she'd": ["she had", "she would"],
    "she'd've": ["she would have"],
    "she'll": ["she shall", "she will"],
    "she'll've": ["she shall have", "she will have"],
    "she's": ["she has", "she is"],
    "should've": ["should have"],
    "shouldn't": ["should not"],
    "shouldn't've": ["should not have"],
    "so've": ["so have"],
    "so's": ["so as", "so is"],
    "that'd": ["that would", "that had"],
    "that'd've": ["that would have"],
    "that's": ["that has", "that is"],
    "there'd": ["there had", "there would"],
    "there'd've": ["there would have"],
    "there's": ["there has", "there is"],
    "they'd": ["they had", "they would"],
    "they'd've": ["they would have"],
    "they'll": ["they shall", "they will"],
    "they'll've": ["they shall have", "they will have"],
    "they're": ["they are"],
    "they've": ["they have"],
    "to've": ["to have"],
    "wasn't": ["was not"],
    "we'd": ["we had", "we would"],
    "we'd've": ["we would have"],
    "we'll": ["we will"],
    "we'll've": ["we will have"],
    "we're": ["we are"],
    "we've": ["we have"],
    "weren't": ["were not"],
    "what'll": ["what shall", "what will"],
    "what'll've": ["what shall have", "what will have"],
    "what're": ["what are"],
    "what's": ["what has", "what is"],
    "what've": ["what have"],
    "when's": ["when has", "when is"],
    "when've": ["when have"],
    "where'd": ["where did"],
    "where's": ["where has", "where is"],
    "where've": ["where have"],
    "who'll": ["who shall", "who will"],
    "who'll've": ["who shall have", "who will have"],
    "who's": ["who has", "who is"],
    "who've": ["who have"],
    "why's": ["why has", "why is"],
    "why've": ["why have"],
    "will've": ["will have"],
    "won't": ["will not"],
    "won't've": ["will not have"],
    "would've": ["would have"],
    "wouldn't": ["would not"],
    "wouldn't've": ["would not have"],
    "y'all": ["you all"],
    "y'all'd": ["you all would"],
    "y'all'd've": ["you all would have"],
    "y'all're": ["you all are"],
    "y'all've": ["you all have"],
    "you'd": ["you had", "you would"],
    "you'd've": ["you would have"],
    "you'll": ["you shall", "you will"],
    "you'll've": ["you shall have", "you will have"],
    "you're": ["you are"],
    "you've": ["you have"]
    }

    link = "http://www.thesaurus.com/browse/"

    sentence = strutils.strip_command(msg.content)
    em = Embed(title="Thesaurus-ifier", description="Completely overuses the thesaurus on a sentence.\nCheck out the program at [Thesaurus-er](https://github.com/UnsignedByte/Thesaurus-er) by [UnsignedByte](https://github.com/UnsignedByte)!",colour=0x4e91fc)
    em.add_field(name="Input Sentence", value=sentence, inline=False)
    em.add_field(name="Output Sentence", value="Converting...", inline=False)

    m = await msgutils.send_embed(Bot, msg, em)

    for k in sorted(contractions, key=len, reverse=True): # Through keys sorted by length
        sentence = sentence.replace(k, choice(contractions[k]))
    sentence = sentence.split()

    newsentence = []
    for a in sentence:
        newa = a.strip(string.punctuation)
        punc = a.split(newa)
        #From https://stackoverflow.com/questions/367155/splitting-a-string-into-words-and-punctuation
        newa = [item for item in map(str.strip, re.split("(\W+)", newa)) if len(item) > 0]

        lets = []
        for xi in range(0, len(newa)):
            x = newa[xi]
            if xi % 2 == 0:
                try:
                    response = req.get(link+x)
                    response.raise_for_status()
                    html_doc = response.text
                    soup = BeautifulSoup(html_doc, 'html.parser')
                    chosenone = choice(list(map(lambda x:x.decode_contents(formatter="html"), soup.findAll("span", 'text'))))
                    if x[0].isupper():
                        chosenone = chosenone.title()
                    lets.append(chosenone)
                except (req.exceptions.HTTPError, IndexError):
                    lets.append(x)
            else:
                lets.append(x)

        lets = punc[0]+''.join(lets)+punc[1]
        newsentence.append(lets)

    em.set_field_at(1, name="Output Sentence", value=' '.join(newsentence), inline=False)
    await msgutils.edit_embed(Bot, m, em)

add_message_handler(rps, "rps")
add_message_handler(invite, "invite")
add_message_handler(thesaurus, "thesaurus")
print("\tFun Commands Initialized")
