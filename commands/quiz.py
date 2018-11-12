# @Author: Edmund Lam <edl>
# @Date:   18:59:11, 18-Apr-2018
# @Filename: quiz.py
# @Last modified by:   edl
# @Last modified time: 18:18:27, 11-Nov-2018


import asyncio
from discord import Embed
from discow.handlers import add_message_handler, bot_data
from utils import msgutils, strutils, objutils
from collections import OrderedDict
from commands.economy import give
from random import shuffle, randint

print("\tInitializing Quiz Command")
quiz_handlers = {}
quiz_users = []

print("\t\tCreating Trivia Classes")

class Question:
    def __init__(self, q, o, s):
        self.question = q
        self.options = o
        self.shuffle = s
    def isCorrect(self, option):
        return list(self.options.values())[option-1]
    def optshuf(self):
        if self.shuffle:
            keeeeys = list(self.options.keys())
            shuffle(keeeeys)
            newoptions = OrderedDict()
            for k in keeeeys:
                newoptions[k] = self.options[k]
            self.options = newoptions
    def getstr(self, selected=None, showCorrect=False):
        if showCorrect:
            outstr = "```css\n{Question: '"+self.question.replace('\'', '’')+"'}"
        else:
            outstr = "```markdown\n# "+self.question
        for a in range(len(self.options)):
            kee = list(self.options.keys())[a]
            if a == selected:
                if showCorrect:
                    outstr+="\n."+chr(a+65)+":  "
                    if self.isCorrect(a+1):
                        outstr+="("+kee.center(48)+")"
                    else:
                        outstr+="["+kee.center(48)+"]"
                else:
                    outstr+="\n<["+chr(a+65)+"]>["+kee.center(45)+"]()"
            else:
                if showCorrect:
                    outstr+="\n{"+chr(a+65)+":} "
                    if self.isCorrect(a+1):
                        outstr+="("+kee.center(48)+")"
                    else:
                        outstr+="["+kee.center(48)+"]"
                else:
                    outstr+="\n<<"+chr(a+65)+">>["+kee.center(45)+"]()"
        return outstr+'```'
print("\t\tFinished Quiz Classes")


async def quiz(Bot, msg):
    if not msg.server.id in bot_data['quiz_data']:
        bot_data['quiz_data'][msg.server.id] = [None, {}]
    else:
        for k in bot_data['quiz_data'][msg.server.id][1].keys():
            if not bot_data['quiz_data'][msg.server.id][1][k]:
                del bot_data['quiz_data'][msg.server.id][1][k]
    try:
        newmsg = strutils.strip_command(msg.content).split(" ")
    except IndexError:
        em = Embed(title="Missing subcommand", description=strutils.format_response("You must specify a subcommand!\nValid options include `cow quiz add` and `cow quiz take`.", _msg=msg), colour=0xff7830)
        await msgutils.send_embed(Bot, msg, em)
        return
    try:
        if not msg.author.id in quiz_users:
            quiz_users.append(msg.author.id)
            try:
                await quiz_handlers[newmsg[0]](Bot, msg)
            except KeyError:
                raise
            finally:
                quiz_users.remove(msg.author.id)
        else:
            await Bot.send_message(msg.channel, "You already have a quiz running!\nPlease cancel that command first.")
    except KeyError:
        em = Embed(title="ERROR", description="Unknown subcommand **%s**." % newmsg[0], colour=0xd32323)
        await Bot.send_message(msg.channel, embed=em)

async def setmod(Bot, msg):
    if (bot_data['quiz_data'][msg.server.id][0] and bot_data['quiz_data'][msg.server.id][0] not in msg.author.roles) and not msg.channel.permissions_for(msg.author).manage_messages:
        em = Embed(title="Insufficient Permissions", description=strutils.format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await msgutils.send_embed(Bot, msg, em)
        return
    try:
        bot_data['quiz_data'][msg.server.id][0] = msg.role_mentions[0]
        await Bot.send_message(msg.channel, "Quiz moderator role has succesfully been set to "+msg.role_mentions[0].mention+".")
    except IndexError:
        await Bot.send_message(msg.channel, "Please mention a role.")

async def take(Bot, msg):
    try:
        cat = strutils.strip_command(msg.content).split(" ", 1)[1].title()
        questions = bot_data['quiz_data'][msg.server.id][1][cat]
    except (KeyError, IndexError):
        em = Embed(title="Available Categories", colour=0xff7830)
        desc = 'We could not find the specified category in this server. Please choose one of the available options listed below.\n'
        if len(bot_data['quiz_data'][msg.server.id][1]) > 0:
            for k,v in bot_data['quiz_data'][msg.server.id][1].items():
                desc+='\n'+k
        else:
            desc += '\nNone'
        em.description = desc
        qmsg = await msgutils.send_embed(Bot, msg, em)
        def check(s):
            return s.content.title() in bot_data['quiz_data'][msg.server.id][1] or s.content.lower() == 'cancel'
        newm = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
        if not newm or newm.content.lower() == 'cancel':
            em = Embed(title="Question Wizard", description='*Operation Cancelled*', colour=0xff7830)
            await msgutils.edit_embed(Bot, qmsg, em)
            await Bot.delete_message(newm)
            return
        cat = newm.content.title()
        questions = bot_data['quiz_data'][msg.server.id][1][cat]
        await Bot.delete_messages([qmsg, newm])

    def formatDesc(cat="Unknown", ql="Unknown", score=100):
        return "Category: "+cat+"\nQuestions Left: "+str(ql)+"\nPercent Correct: "+'{0:.2f}'.format(score)+"%"

    em = Embed(title="Quiz", description=formatDesc(cat=cat)+"\n\nHow many questions do you want in your quiz? There "+("is" if len(questions) == 1 else "are")+" "+str(len(questions))+" question"+("s" if len(questions) == 1 else "")+" in total to choose from.\nType a number, or type `all` to get all questions in the category.", colour=0xff7830)
    qmsg = await msgutils.send_embed(Bot, msg, em)
    def check(s):
        return (objutils.integer(s.content) and 0<int(s.content)<=len(questions)) or s.content == 'all'
    nm = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
    if not nm:
        return
    if nm.content != 'all':
        shuffle(questions)
        questions = questions[0:int(nm.content)]
    await Bot.delete_message(nm)
    em.add_field(name="Question", value="NULL")

    totalscore = 0

    em.description=formatDesc(cat=cat, ql=len(questions), score=100.0)
    for a in range(len(questions)):
        questions[a].optshuf()
        em.set_field_at(0, name="Question "+str(a+1), value=questions[a].getstr()+"\n\nTo select your answer, type in the option letter (from A to "+chr(len(questions[a].options)+64)+").\nIf you don't know the answer, you can always guess!")
        qmsg = await msgutils.edit_embed(Bot, qmsg, em)
        def check(s):
            return len(s.content)==1 and 1<=ord(s.content.upper())-64<=len(questions[a].options)
        def yesnocheck(s):
            return s.content in ['y', 'n', 'yes', 'no']
        def confirmcheck(s):
            return check(s) or s.content in ['n', 'next']
        select = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
        select.content = str(ord(select.content.upper())-64)
        await Bot.delete_message(select)
        while True:
            em.set_field_at(0, name="Question "+str(a+1), value=questions[a].getstr(selected=int(select.content)-1)+"\n\nTo select another answer, type in the option letter (from A to "+chr(len(questions[a].options)+64)+").\nWhen you are ready to move on, type `next (n)`.\nIf you don't know the answer, you can always guess!")
            qmsg = await msgutils.edit_embed(Bot, qmsg, em)
            newselect = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=confirmcheck)
            await Bot.delete_message(newselect)
            if newselect.content in ['n', 'next']:
                if questions[a].isCorrect(int(select.content)):
                    totalscore += 1
                em.set_field_at(0, name="Question "+str(a+1), value=questions[a].getstr(selected=int(select.content)-1, showCorrect=True)+'\n\nWhen you are done viewing answers, type `next (n)` to move on.')
                em.description = formatDesc(cat=cat, ql=len(questions)-a-1, score=100*totalscore/(a+1))
                await msgutils.edit_embed(Bot, qmsg, em)
                def moveoncheck(s):
                    return s.content in ['n', 'next']
                moveon = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=moveoncheck)
                await Bot.delete_message(moveon)
                break
            else:
                newselect.content = str(ord(newselect.content.upper())-64)
                select = newselect

    em.remove_field(0)
    moneyrecieved = randint(round(totalscore/2)*100, round(totalscore*2)*100)
    em.title = 'Quiz Completed!'
    em.description = 'Congratulations! You completed a quiz in the '+cat+' category with '+str(len(questions))+' questions.\nYou recieved a score of '+'{0:.2f}'.format(100*totalscore/len(questions))+'%, or '+str(totalscore)+' out of '+str(len(questions))+'!\nAs you answered '+str(totalscore)+' questions correctly, you have recieved $'+str(moneyrecieved/100)+'!'
    await msgutils.edit_embed(Bot, qmsg, em)
    give(moneyrecieved, msg.author.id)


async def add(Bot, msg):
    if (bot_data['quiz_data'][msg.server.id][0] and bot_data['quiz_data'][msg.server.id][0] not in msg.author.roles) and not msg.channel.permissions_for(msg.author).manage_messages:
        em = Embed(title="Insufficient Permissions", description=strutils.format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await msgutils.send_embed(Bot, msg, em)
        return
    question = strutils.strip_command(msg.content).split(" ", 1)[1]
    em = Embed(title="Add Quiz Question", description="Question:\n"+question, colour=0xff7830)
    desc = ''
    if len(bot_data['quiz_data'][msg.server.id][1]) > 0:
        for k,v in bot_data['quiz_data'][msg.server.id][1].items():
            desc+='\n'+k
    else:
        desc = '\nNone'
    em.add_field(name="Question Category", value="Available Categories:"+desc+"\n\nIf your desired category is not listed, you may add one below.\n\nIf you want to cancel, type `cancel`.", inline=False)
    qmsg = await msgutils.send_embed(Bot, msg, em)

    cat = await getquestioncategory(Bot, msg, qmsg, em, add=True)
    if not cat:
        return
    em.set_field_at(0, name="Question Category", value=cat, inline=False)
    quest = await editquestion(Bot, msg, qmsg, em, cat, question)
    bot_data['quiz_data'][msg.server.id][1][cat].append(quest)

async def editquestion(Bot, msg, qmsg, em, cat, question):
    responsesvalue = "Type `add (a)`, `remove (r)`, and `edit (e)` to add, remove, and edit responses.\nType `back` to go back and edit your category, `cancel` to leave the Question Wizard, or `done` to finish and publish your question."
    optionresponses = "```css\n"
    em.add_field(name="Responses", value=responsesvalue)
    await msgutils.edit_embed(Bot, qmsg, em)
    options = OrderedDict()

    def oformat(s, v, c):
        if c:
            return "\n."+chr(int(s)+64)+": ("+v.center(50)+")"
        else:
            return "\n."+chr(int(s)+64)+": ["+v.center(50)+"]"

    while True:
        def check(s):
            return s.content.lower() in ['done', 'add', 'remove', 'edit', 'back', 'a', 'r', 'e', 'cancel']
        out = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
        if not out or out.content == 'cancel':
            em = Embed(title="Question Wizard", description="*Operation Cancelled*", colour=0xff7830)
            await msgutils.edit_embed(Bot, qmsg, em)
            await Bot.delete_message(out)
            return
        elif out.content == 'back':
            await Bot.delete_message(out)
            em.set_field_at(0, name="Question Category", value="Available Categories:"+desc+"\n\nIf your desired category is not listed, you may add one below.\n\nIf you want to cancel, type `cancel`.", inline=False)
            em.remove_field(1)
            qmsg = await msgutils.edit_embed(Bot, qmsg, em)
            cat = await getquestioncategory(Bot, msg, qmsg, em, add=True)
            if not cat:
                return
            em.set_field_at(0, name="Question Category", value=cat, inline=False)
            em.add_field(name="Responses", value=optionresponses+'```\n\n'+responsesvalue)
            await msgutils.edit_embed(Bot, qmsg, em)
        elif out.content in ('add', 'a'):
            mm = await Bot.send_message(msg.channel, "What is the response you would like to add? Type `cancel` to cancel.")
            while True:
                option = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel)
                if not option:
                    return
                if option.content in options:
                    _m = await Bot.send_message(msg.channel, "That option already exists!\nPlease input a different option.")
                    await asyncio.sleep(0.5)
                    await Bot.delete_messages([option,_m])
                else:
                    break
            if option.content.lower() != 'cancel':
                def corrcheck(s):
                    return s.content.lower() in ["correct", "c", "incorrect", "i", "right", "wrong"]
                mmm = await Bot.send_message(msg.channel, "Would you like this option to be correct or incorrect? Type `correct (c)` or `incorrect (i)`.")
                corr = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=corrcheck)
                if not corr:
                    return
                if corr.content.lower() in ["correct", "c", "right"]:
                    options[option.content] = True
                else:
                    options[option.content] = False
                optionresponses+= oformat(str(len(options)), option.content, options[option.content])
                em.set_field_at(1, name="Responses", value=optionresponses+"```\n\n"+responsesvalue)
                await msgutils.edit_embed(Bot, qmsg, em)
                await Bot.delete_messages([out, option, mm, mmm, corr])
            else:
                mmm = await Bot.send_message(msg.channel, "*Operation Cancelled*")
                await asyncio.sleep(0.25)
                await Bot.delete_messages([out, option, mm, mmm])
        elif out.content in ('remove', 'r'):
            if len(options) == 0:
                mm = await Bot.msgutils.send_embed(msg.channel, "You have no options to remove!")
                await asyncio.sleep(0.25)
                await Bot.delete_messages([mm, out])
            else:
                mm = await Bot.send_message(msg.channel, "What is the response you would like to remove? Type in its letter.\nType `cancel` to cancel.")
                def check(s):
                    return s.content.lower() == 'cancel' or len(s.content) == 1 and 1 <= ord(s.content.upper())-64 <= len(options)
                option = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                if not option:
                    return
                if option.content != 'cancel':
                    option.content = str(ord(option.content.upper())-64)
                    mmm = await Bot.send_message(msg.channel, "Are you sure? This cannot be undone.\nRespond with `yes (y)` or `no (n)`")
                    def yesnocheck(s):
                        return s.content.lower() in ['yes', 'no', 'y', 'n']
                    yesorno = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=yesnocheck)
                    if not yesorno:
                        return
                    if yesorno.content.lower() in ['yes', 'y']:
                        del options[list(options.keys())[int(option.content)-1]]
                        optionresponses = "```css\n"
                        if len(options) > 0:
                            for k, v in options.items():
                                optionresponses+= oformat(str(list(options.keys()).index(k)+1), k, v)
                            em.set_field_at(1, name="Responses", value=optionresponses+"```\n\n"+responsesvalue)
                        else:
                            em.set_field_at(1, name="Responses", value=responsesvalue)
                        await msgutils.edit_embed(Bot, qmsg, em)
                        await Bot.delete_messages([out, mm, mmm, option, yesorno])
                    else:
                        mmmm = await Bot.send_message(msg.channel, "*Operation Cancelled*")
                        await Bot.delete_messages([out, mm, mmm, option, yesorno, mmmm])
                else:
                    mmm = await Bot.send_message(msg.channel, "*Operation Cancelled*")
                    await asyncio.sleep(0.25)
                    await Bot.delete_messages([out, option, mm, mmm])
        elif out.content in ('edit', 'e'):
            if len(options) == 0:
                mm = await Bot.msgutils.send_embed(msg.channel, "You have no options to edit!")
                await asyncio.sleep(0.25)
                await Bot.delete_messages([mm, out])
            else:
                mm = await Bot.send_message(msg.channel, "What is the response you would like to edit? Type in its letter.\nType `cancel` to cancel.")
                def check(s):
                    return s.content.lower() == 'cancel' or len(s.content) == 1 and 1 <= ord(s.content.upper())-64 <= len(options)
                option = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                if not option:
                    return
                if option.content != 'cancel':
                    option.content = str(ord(option.content.upper())-64)
                    mmm = await Bot.send_message(msg.channel, "What would you like to replace it with?")
                    while True:
                        newoption = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel)
                        if not newoption:
                            return
                        def corrcheck(s):
                            return s.content.lower() in ["correct", "c", "incorrect", "i", "right", "wrong"]
                        mmmmmmmm = await Bot.send_message(msg.channel, "Would you like this option to be correct or incorrect? Type `correct (c)` or `incorrect (i)`.")
                        iscorrm = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=corrcheck)
                        if not iscorrm:
                            return
                        iscorr = iscorrm.content in ["correct", "c", "right"]
                        if newoption.content not in options or options[newoption.content] != iscorr:
                            break
                        else:
                            _m = await Bot.send_message(msg.channel, "That option already exists!\nPlease input a different option.")
                            await asyncio.sleep(0.5)
                            await Bot.delete_messages([out, option, newoption, _m, iscorrm, mmmmmmmm])
                    mmmm = await Bot.send_message(msg.channel, "Are you sure? This cannot be undone.\nRespond with `yes (y)` or `no (n)`")
                    def yesnocheck(s):
                        return s.content.lower() in ['yes', 'no', 'y', 'n']
                    yesorno = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=yesnocheck)
                    if not yesorno:
                        return
                    if yesorno.content.lower() in ['yes', 'y']:
                        oldoption = list(options.keys())[int(option.content)-1]
                        options = OrderedDict(list((newoption.content, iscorr) if k == oldoption else (k, v) for k, v in options.items()))
                        optionresponses = '```css\n'
                        for k, v in options.items():
                            optionresponses+= oformat(str(list(options.keys()).index(k)+1), k, v)
                        em.set_field_at(1, name="Responses", value=optionresponses+"```\n\n"+responsesvalue)
                        await msgutils.edit_embed(Bot, qmsg, em)
                    await Bot.delete_messages([out, option, newoption, mm, mmm, mmmm, yesorno, iscorrm, mmmmmmmm])
                else:
                    mmm = await Bot.send_message(msg.channel, "*Operation Cancelled*")
                    await asyncio.sleep(0.25)
                    await Bot.delete_messages([out, option, mm, mmm])
        elif out.content == 'done':
            if len(options) > 1:
                mooooooooocow = await Bot.send_message(msg.channel, "Should this question have shuffled responses?")
                def yesnocheck(s):
                    return s.content.lower() in ['yes', 'no', 'y', 'n']
                yesorno = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=yesnocheck)
                if not yesorno:
                    return
                if yesorno.content.lower() in ['yes', 'y']:
                    shuffled = True
                else:
                    shuffled = False
                em.set_field_at(1, name="Responses", value=optionresponses+'```')
                await msgutils.edit_embed(Bot, qmsg, em)
                await Bot.delete_messages([out, yesorno, mooooooooocow])
                return Question(question, options, shuffled)
            else:
                momomo = await Bot.send_message(msg.channel, "You must have at least 2 options!")
                await asyncio.sleep(0.5)
                await Bot.delete_messages([out, momomo])


async def getquestioncategory(Bot, msg, qmsg, em, add=False):
    while True:
        out = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel)
        if not out or out.content.lower() == 'cancel':
            em = Embed(title="Question Wizard", description="*Operation Cancelled*", colour=0xff7830)
            await msgutils.edit_embed(Bot, qmsg, em)
            await Bot.delete_message(out)
            return None
        elif out.content.title() not in bot_data['quiz_data'][msg.server.id][1]:
            if add:
                m = await Bot.send_message(msg.channel, out.content.title()+" is not currently a category. Would you like to make a new category? Type` yes (y)` or `no (n)`.")
                def check(s):
                    return s.content.lower() in ["y", "n", "yes", "no"]
                yesno = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                if not yesno:
                    return
                await Bot.delete_messages([yesno, m, out])
                if yesno.content.lower() in ["y", "yes"]:
                    bot_data['quiz_data'][msg.server.id][1][out.content.title()] = []
                    return out.content.title()
            else:
                m = await Bot.send_message(msg.channel, out.content.title()+" is not currently a category.")
                await asyncio.sleep(0.25)
                await Bot.delete_messages([m, out])
                return None
        else:
            await Bot.delete_message(out)
            return out.content.title()

quiz_handlers["take"] = take
quiz_handlers["add"] = add
quiz_handlers["setmod"] = setmod
quiz_handlers["modrole"] = setmod

add_message_handler(quiz, "quiz")
print("\tQuiz Command Initialized")
