import requests
from base64 import b64decode
from enum import Enum
from discow.handlers import add_message_handler
import asyncio

def getCategories():
    categories = {}
    for a in requests.get('https://opentdb.com/api_category.php').json()['trivia_categories']:
        categories[a['name'].lower()] = a['id']

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
    def __init__(self):
        self.token_id = requests.get('https://opentdb.com/api_token.php', params={'command':'request'}).json()['token']
    def getquestion(self, category=None, difficulty=None, type=None, amount=1):
        obj = {k: v for k, v in locals().items() if v is not None}
        obj.update({'token':self.token_id, 'encode':'base64'})
        del obj['self']
        response = requests.get('https://opentdb.com/api.php', params=obj).json()
        if response['response_code'] == 0:
            return list({k: (list(b64decode(n).decode('utf-8') for n in v) if isinstance(v, list) else b64decode(v).decode('utf-8')) for k, v in x.items()} for x in response["results"])
        elif response['response_code'] == 1:
            return 'No results'
        elif response['response_code'] == 2:
            return 'Invalid Parameter'
        elif response['response_code'] == 3:
            self.token_id = requests.get('https://opentdb.com/api_token.php', params={'command':'request'}).json()['token']
            return self.getquestion(category=category, difficulty=difficulty, type=type, amount=amount)
        elif response['response_code'] == 4:
            self.token_id = requests.get('https://opentdb.com/api_token.php', params={'command':'reset', 'token':self.token_id}).json()['token']
            return self.getquestion(category=category, difficulty=difficulty, type=type, amount=amount)

triviaAPI = Trivia()

@asyncio.coroutine
def trivia(Discow, msg):
    cont = strip_command(msg.content).rsplit(' ', 1)
    diff = None
    cat = None
    if cont[0].lower() not in Data.difficulties:
        cont = ' '.join(cont)
    else:
        diff = Data.difficulties[cont.pop(0).lower()]
    if cont[0].lower() in categories:
        cat = categories(cont[0].lower())
    question = triviaAPI.getquestion()
    yield from Discow.send_message(msg.channel, question)

add_message_handler(trivia, 'trivia')
