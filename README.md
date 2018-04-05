# Discow
A Python3 bot for Discord using discord.py.  
Created by [UnsignedByte](https://github.com/UnsignedByte) and [anematode](https://github.com/anematode) and licensed under [The MIT License](https://en.wikipedia.org/wiki/MIT_License).

## Commands
Prefix: `cow`

Necessary arguments: `{var}`  
Optional arguments: `(var)`  
Remember to delete `{}` and `()`.

### Utilities

| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|help|`cow help`|Displays help information.|`help`|
|info|`cow info`|Displays general information about the bot.|`info`, `hi`|
|close|`cow close`|Shut down the bot and save all data.|`close`, `shutdown`|
|save|`cow save`|Save all data.|`save`|
|settings|`cow settings {args}`|Look at Settings Subcommands.|`settings`|
|purge|`cow purge {n}`|Clears the last `n` messages.|`clear`, `purge`|
|quote|`cow quote {id} (channel)`|Quotes a message given an id and an optional channel.|`quote`|
|define|`cow define {word}`|Retrieves the definition of a word from Merriam-Webster.|`define`, `dictionary`|
|schedule|`cow schedule {day}`|Tells you the Gunn Schedule for a given day.|`schedule`|

#### Settings Subcommands

| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|disable|`cow settings disable {cmd} {channel(s)}`|Disables a command in the specified channels.|`disable`|
|enable|`cow settings enable {cmd} {channel(s)}`|Enables a command in the specified channels.|`enable`|

### Fun
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|invite|`cow invite`|Creates an invite link for the server!|`invite`|
|thesaurus|`cow thesaurus`|Thesaurus-ifies a sentence.|`thesaurus`|
|rps|`cow rps {item}`|Plays rock paper scissors!|`rps`|
|reaction|`cow reaction {num}`|Adds random reactions to the last message.|`reaction`|
|easteregg|`cow easteregg`|Sends a random message!|`easteregg`|

### Gambling/Economy
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|daily|`cow daily`|Gives you your daily money!|`daily`|
|money|`cow money (mention)`|Displays your money or someone else's money.|`money`|
|stock|`cow stock {subcommand} {name}`|View, buy, and sell stocks using realtime stock information from the nasdaq website. For more info look at Stock Subcommands.|`stock`|
|slots|`cow slots {amount}`|Gamble for money!|`slots`, `gamble`|

#### Stock Subcommands
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|buy|`cow stock buy {name}`|Buy virtual stocks|`buy`, `invest`|
|sell|`cow stock sell {name}`|Sell virtual stocks.|`sell`|
|get|`cow stock get {name}`|View realtime stock information from the nasdaq website.|`get`, `info`|
