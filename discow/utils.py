whitespace = [' ', '\t', '\n']
discow_prefix = "cow "

def format_response(string, **kwargs):
    if "_msg" in kwargs:
        message = kwargs["_msg"]
        kwargs["_msgcontent"] = message.content
        kwargs["_author"] = message.author
    if "_author" in kwargs:
        author = kwargs["_author"]
        kwargs["_name"] = author.display_name
        kwargs["_username"] = author.name
        kwargs["_mention"] = author.mention

    return string.format(**kwargs)

def parse_command(msg, num=-1):
    cont = msg[len(discow_prefix):].split(" ")
    if num is not -1:
        if len(cont)<num+1:
            raise IndexError("Not enough inputs")
        else:
            return cont[:num]+[' '.join(cont[num:])]
    else:
        return cont

def strip_command(msg):
    return parse_command(msg, 1)[1]
