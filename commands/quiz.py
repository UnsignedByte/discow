import asyncio
from discord import Embed
from discow.handlers import add_message_handler, quiz_data
from discow.utils import *
from collections import OrderedDict
from commands.utilities import save
from commands.economy import give
from random import shuffle, randint

print("\tInitializing Quiz Command")
quiz_handlers = {}
quiz_users = []

@asyncio.coroutine
def quiz(Discow, msg):
    if not msg.server.id in quiz_data:
        quiz_data[msg.server.id] = [None, {}]
    else:
        for k in quiz_data[msg.server.id][1].keys():
            if not quiz_data[msg.server.id][1][k]:
                del quiz_data[msg.server.id][1][k]
    newmsg = strip_command(msg.content).split(" ")
    try:
        if not msg.author.id in quiz_users:
            quiz_users.append(msg.author.id)
            try:
                yield from quiz_handlers[newmsg[0]](Discow, msg)
            except Exception:
                raise
            finally:
                quiz_users.remove(msg.author.id)
        else:
            yield from Discow.send_message(msg.channel, "You already have a quiz running!\nPlease cancel that command first.")
    except KeyError:
        em = Embed(title="ERROR", description="Unknown subcommand **%s**." % newmsg[0], colour=0xd32323)
        yield from Discow.send_message(msg.channel, embed=em)

@asyncio.coroutine
def setmod(Discow, msg):
    if (quiz_data[msg.server.id][0] and quiz_data[msg.server.id][0] not in msg.author.roles) and not msg.channel.permissions_for(msg.author).manage_messages:
        em = Embed(title="Insufficient Permissions", description=format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        yield from send_embed(Discow, msg, em)
        return
    try:
        quiz_data[msg.server.id][0] = msg.role_mentions[0]
        yield from Discow.send_message(msg.channel, "Quiz moderator role has succesfully been set to "+msg.role_mentions[0].mention+".")
    except IndexError:
        yield from Discow.send_message(msg.channel, "Please mention a role.")

@asyncio.coroutine
def take(Discow, msg):
    try:
        cat = strip_command(msg.content).split(" ", 1)[1].title()
        questions = quiz_data[msg.server.id][1][cat]
    except (KeyError, IndexError):
        em = Embed(title="Available Categories", colour=0xff7830)
        desc = 'We could not find the specified category in this server. Please choose one of the available options listed below.\n'
        if len(quiz_data[msg.server.id][1]) > 0:
            for k,v in quiz_data[msg.server.id][1].items():
                desc+='\n'+k
        else:
            desc += '\nNone'
        em.description = desc
        qmsg = yield from send_embed(Discow, msg, em)
        def check(s):
            return s.content.title() in quiz_data[msg.server.id][1] or s.content.lower() == 'cancel'
        newm = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
        if not newm or newm.content == 'cancel':
            em = Embed(title="Question Wizard", description='*Operation Cancelled*', colour=0xff7830)
            yield from edit_embed(Discow, qmsg, em)
            yield from Discow.delete_message(newm)
            return
        cat = newm.content
        questions = quiz_data[msg.server.id][1][cat]
        yield from Discow.delete_messages([qmsg, newm])

    def formatDesc(cat="Unknown", ql="Unknown", score=100):
        return "Category: "+cat+"\nQuestions Left: "+str(ql)+"\nPercent Correct: "+'{0:.2f}'.format(score)+"%"

    em = Embed(title="Quiz", description=formatDesc(cat=cat)+"\n\nHow many questions do you want in your quiz? There "+("is" if len(questions) == 1 else "are")+" "+str(len(questions))+" question"+("s" if len(questions) == 1 else "")+" in total to choose from.\nType a number, or type `all` to get all questions in the category.", colour=0xff7830)
    qmsg = yield from send_embed(Discow, msg, em)
    def check(s):
        return (isInteger(s.content) and 0<int(s.content)<=len(questions)) or s.content == 'all'
    nm = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
    if not nm:
        return
    if nm.content != 'all':
        shuffle(questions)
        questions = questions[0:int(nm.content)]
    yield from Discow.delete_message(nm)
    em.add_field(name="Question", value="NULL")

    totalscore = 0

    em.description=formatDesc(cat=cat, ql=len(questions), score=100.0)
    for a in range(len(questions)):
        em.set_field_at(0, name="Question "+str(a+1), value=questions[a].getstr()+"\n\nTo select your answer, type in the option letter (from A to "+chr(len(questions[a].options)+64)+").\nIf you don't know the answer, you can always guess!")
        qmsg = yield from edit_embed(Discow, qmsg, em)
        def check(s):
            return len(s.content)==1 and 1<=ord(s.content.upper())-64<=len(questions[a].options)
        def yesnocheck(s):
            return s.content in ['y', 'n', 'yes', 'no']
        def confirmcheck(s):
            return check(s) or s.content in ['n', 'next']
        select = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
        select.content = str(ord(select.content.upper())-64)
        yield from Discow.delete_message(select)
        questions[a].optshuf()
        while True:
            em.set_field_at(0, name="Question "+str(a+1), value=questions[a].getstr(selected=int(select.content)-1)+"\n\nTo select another answer, type in the option letter (from A to "+chr(len(questions[a].options)+64)+").\nWhen you are ready to move on, type `next (n)`.\nIf you don't know the answer, you can always guess!")
            qmsg = yield from edit_embed(Discow, qmsg, em)
            newselect = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=confirmcheck)
            yield from Discow.delete_message(newselect)
            if newselect.content in ['n', 'next']:
                if questions[a].isCorrect(int(select.content)):
                    totalscore += 1
                em.set_field_at(0, name="Question "+str(a+1), value=questions[a].getstr(selected=int(select.content)-1, showCorrect=True)+'\n\nWhen you are done viewing answers, type `next (n)` to move on.')
                em.description = formatDesc(cat=cat, ql=len(questions)-a-1, score=100*totalscore/(a+1))
                yield from edit_embed(Discow, qmsg, em)
                def moveoncheck(s):
                    return s.content in ['n', 'next']
                moveon = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=moveoncheck)
                yield from Discow.delete_message(moveon)
                break
            else:
                newselect.content = str(ord(newselect.content.upper())-64)
                select = newselect

    em.remove_field(0)
    moneyrecieved = randint(round(totalscore/2)*100, round(totalscore*2)*100)
    em.title = 'Quiz Completed!'
    em.description = 'Congratulations! You completed a quiz in the '+cat+' category with '+str(len(questions))+' questions.\nYou recieved a score of '+'{0:.2f}'.format(100*totalscore/len(questions))+'%, or '+str(totalscore)+' out of '+str(len(questions))+'!\nAs you answered '+str(totalscore)+' questions correctly, you have recieved $'+str(moneyrecieved/100)+'!'
    yield from edit_embed(Discow, qmsg, em)
    give(moneyrecieved, msg.author.id)


@asyncio.coroutine
def add(Discow, msg):
    if (quiz_data[msg.server.id][0] and quiz_data[msg.server.id][0] not in msg.author.roles) and not msg.channel.permissions_for(msg.author).manage_messages:
        em = Embed(title="Insufficient Permissions", description=format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        yield from send_embed(Discow, msg, em)
        return
    question = strip_command(msg.content).split(" ", 1)[1]
    em = Embed(title="Add Quiz Question", description="Question:\n"+question, colour=0xff7830)
    desc = ''
    if len(quiz_data[msg.server.id][1]) > 0:
        for k,v in quiz_data[msg.server.id][1].items():
            desc+='\n'+k
    else:
        desc = '\nNone'
    em.add_field(name="Question Category", value="Available Categories:"+desc+"\n\nIf your desired category is not listed, you may add one below.\n\nIf you want to cancel, type `cancel`.", inline=False)
    qmsg = yield from send_embed(Discow, msg, em)

    cat = yield from getquestioncategory(Discow, msg, qmsg, em, add=True)
    if not cat:
        return
    em.set_field_at(0, name="Question Category", value=cat, inline=False)
    responsesvalue = "Type `add (a)`, `remove (r)`, and `edit (e)` to add, remove, and edit responses.\nType `back` to go back and edit your category, `cancel` to leave the Question Wizard, or `done` to finish and publish your question."
    optionresponses = "```css\n"
    em.add_field(name="Responses", value=responsesvalue)
    yield from edit_embed(Discow, qmsg, em)
    options = OrderedDict()

    def oformat(s, v, c):
        if c:
            return "\n."+chr(int(s)+64)+": ("+v.center(50)+")"
        else:
            return "\n."+chr(int(s)+64)+": ["+v.center(50)+"]"

    while True:
        def check(s):
            return s.content.lower() in ['done', 'add', 'remove', 'edit', 'back', 'a', 'r', 'e', 'cancel']
        out = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
        if not out or out.content == 'cancel':
            em = Embed(title="Question Wizard", description="*Operation Cancelled*", colour=0xff7830)
            yield from edit_embed(Discow, qmsg, em)
            yield from Discow.delete_message(out)
            return
        elif out.content == 'back':
            yield from Discow.delete_message(out)
            em.set_field_at(0, name="Question Category", value="Available Categories:"+desc+"\n\nIf your desired category is not listed, you may add one below.\n\nIf you want to cancel, type `cancel`.", inline=False)
            em.remove_field(1)
            qmsg = yield from edit_embed(Discow, qmsg, em)
            cat = yield from getquestioncategory(Discow, msg, qmsg, em, add=True)
            if not cat:
                return
            em.set_field_at(0, name="Question Category", value=cat, inline=False)
            em.add_field(name="Responses", value=optionresponses+'```\n\n'+responsesvalue)
            yield from edit_embed(Discow, qmsg, em)
        elif out.content in ('add', 'a'):
            mm = yield from Discow.send_message(msg.channel, "What is the response you would like to add? Type `cancel` to cancel.")
            while True:
                option = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel)
                if not option:
                    return
                if option.content in options:
                    _m = yield from Discow.send_message(msg.channel, "That option already exists!\nPlease input a different option.")
                    yield from asyncio.sleep(0.5)
                    yield from Discow.delete_messages([option,_m])
                else:
                    break
            if option.content.lower() != 'cancel':
                def corrcheck(s):
                    return s.co

                    ntent.lower() in ["correct", "c", "incorrect", "i", "right", "wrong"]
                mmm = yield from Discow.send_message(msg.channel, "Would you like this option to be correct or incorrect? Type `correct (c)` or `incorrect (i)`.")
                corr = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=corrcheck)
                if not corr:
                    return
                if corr.content.lower() in ["correct", "c", "right"]:
                    options[option.content] = True
                else:
                    options[option.content] = False
                optionresponses+= oformat(str(len(options)), option.content, options[option.content])
                em.set_field_at(1, name="Responses", value=optionresponses+"```\n\n"+responsesvalue)
                yield from edit_embed(Discow, qmsg, em)
                yield from Discow.delete_messages([out, option, mm, mmm, corr])
            else:
                mmm = yield from Discow.send_message(msg.channel, "*Operation Cancelled*")
                yield from asyncio.sleep(0.25)
                yield from Discow.delete_messages([out, option, mm, mmm])
        elif out.content in ('remove', 'r'):
            if len(options) == 0:
                mm = yield from Discow.send_embed(msg.channel, "You have no options to remove!")
                yield from asyncio.sleep(0.25)
                yield from Discow.delete_messages([mm, out])
            else:
                mm = yield from Discow.send_message(msg.channel, "What is the response you would like to remove? Type in its letter.\nType `cancel` to cancel.")
                def check(s):
                    return s.content.lower() == 'cancel' or len(s.content) == 1 and 1 <= ord(s.content.upper())-64 <= len(options)
                option = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                if not option:
                    return
                if option.content != 'cancel':
                    option.content = str(ord(option.content.upper())-64)
                    mmm = yield from Discow.send_message(msg.channel, "Are you sure? This cannot be undone.\nRespond with `yes (y)` or `no (n)`")
                    def yesnocheck(s):
                        return s.content.lower() in ['yes', 'no', 'y', 'n']
                    yesorno = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=yesnocheck)
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
                        yield from edit_embed(Discow, qmsg, em)
                        yield from Discow.delete_messages([out, mm, mmm, option, yesorno])
                    else:
                        mmmm = yield from Discow.send_message(msg.channel, "*Operation Cancelled*")
                        yield from Discow.delete_messages([out, mm, mmm, option, yesorno, mmmm])
                else:
                    mmm = yield from Discow.send_message(msg.channel, "*Operation Cancelled*")
                    yield from asyncio.sleep(0.25)
                    yield from Discow.delete_messages([out, option, mm, mmm])
        elif out.content in ('edit', 'e'):
            if len(options) == 0:
                mm = yield from Discow.send_embed(msg.channel, "You have no options to edit!")
                yield from asyncio.sleep(0.25)
                yield from Discow.delete_messages([mm, out])
            else:
                mm = yield from Discow.send_message(msg.channel, "What is the response you would like to edit? Type in its letter.\nType `cancel` to cancel.")
                def check(s):
                    return s.content.lower() == 'cancel' or len(s.content) == 1 and 1 <= ord(s.content.upper())-64 <= len(options)
                option = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                if not option:
                    return
                if option.content != 'cancel':
                    option.content = str(ord(option.content.upper())-64)
                    mmm = yield from Discow.send_message(msg.channel, "What would you like to replace it with?")
                    while True:
                        newoption = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel)
                        if not newoption:
                            return
                        def corrcheck(s):
                            return s.content.lower() in ["correct", "c", "incorrect", "i", "right", "wrong"]
                        mmmmmmmm = yield from Discow.send_message(msg.channel, "Would you like this option to be correct or incorrect? Type `correct (c)` or `incorrect (i)`.")
                        iscorrm = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=corrcheck)
                        if not iscorrm:
                            return
                        iscorr = iscorrm.content in ["correct", "c", "right"]
                        if newoption.content not in options or options[newoption.content] != iscorr:
                            break
                        else:
                            _m = yield from Discow.send_message(msg.channel, "That option already exists!\nPlease input a different option.")
                            yield from asyncio.sleep(0.5)
                            yield from Discow.delete_messages([out, option, newoption, _m, iscorrm, mmmmmmmm])
                    mmmm = yield from Discow.send_message(msg.channel, "Are you sure? This cannot be undone.\nRespond with `yes (y)` or `no (n)`")
                    def yesnocheck(s):
                        return s.content.lower() in ['yes', 'no', 'y', 'n']
                    yesorno = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=yesnocheck)
                    if not yesorno:
                        return
                    if yesorno.content.lower() in ['yes', 'y']:
                        oldoption = list(options.keys())[int(option.content)-1]
                        options = OrderedDict(list((newoption.content, iscorr) if k == oldoption else (k, v) for k, v in options.items()))
                        optionresponses = '```css\n'
                        for k, v in options.items():
                            optionresponses+= oformat(str(list(options.keys()).index(k)+1), k, v)
                        em.set_field_at(1, name="Responses", value=optionresponses+"```\n\n"+responsesvalue)
                        yield from edit_embed(Discow, qmsg, em)
                    yield from Discow.delete_messages([out, option, newoption, mm, mmm, mmmm, yesorno, iscorrm, mmmmmmmm])
                else:
                    mmm = yield from Discow.send_message(msg.channel, "*Operation Cancelled*")
                    yield from asyncio.sleep(0.25)
                    yield from Discow.delete_messages([out, option, mm, mmm])
        elif out.content == 'done':
            if len(options) > 1:
                yield from Discow.send_message("Should this question have shuffled responses?")
                def yesnocheck(s):
                    return s.content.lower() in ['yes', 'no', 'y', 'n']
                yesorno = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=yesnocheck)
                if not yesorno:
                    return
                if yesorno.content.lower() in ['yes', 'y']:
                    shuffled = True
                else:
                    shuffled = False
                em.set_field_at(1, name="Responses", value=optionresponses+'```')
                yield from edit_embed(Discow, qmsg, em, yesorno)
                yield from Discow.delete_message(out)
                quiz_data[msg.server.id][1][cat].append(Question(question, options, shuffled))
                yield from save(Discow, msg, overrideperms=True)
                return
            else:
                momomo = yield from Discow.send_message(msg.channel, "You must have at least 2 options!")
                yield from asyncio.sleep(0.5)
                yield from Discow.delete_messages([out, momomo])


@asyncio.coroutine
def getquestioncategory(Discow, msg, qmsg, em, add=False):
    while True:
        out = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel)
        if not out or out.content.lower() == 'cancel':
            em = Embed(title="Question Wizard", description="*Operation Cancelled*", colour=0xff7830)
            yield from edit_embed(Discow, qmsg, em)
            yield from Discow.delete_message(out)
            return None
        elif out.content.title() not in quiz_data[msg.server.id][1]:
            if add:
                m = yield from Discow.send_message(msg.channel, out.content.title()+" is not currently a category. Would you like to make a new category? Type` yes (y)` or `no (n)`.")
                def check(s):
                    return s.content.lower() in ["y", "n", "yes", "no"]
                yesno = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                if not yesno:
                    return
                yield from Discow.delete_messages([yesno, m, out])
                if yesno.content.lower() in ["y", "yes"]:
                    quiz_data[msg.server.id][1][out.content.title()] = []
                    return out.content.title()
            else:
                m = yield from Discow.send_message(msg.channel, out.content.title()+" is not currently a category.")
                yield from asyncio.sleep(0.25)
                yield from Discow.delete_messages([m, out])
                return None
        else:
            yield from Discow.delete_message(out)
            return out.content.title()


quiz_handlers["take"] = take
quiz_handlers["add"] = add
quiz_handlers["setmod"] = setmod
quiz_handlers["modrole"] = setmod

add_message_handler(quiz, "quiz")
print("\tQuiz Command Initialized")
