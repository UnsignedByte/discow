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
|close|`cow close`|Shut down the bot and save all data.|`close`, `shutdown`|
|save|`cow save`|Save all data.|`save`|
|settings|`cow settings {args}`|Look at Settings Subcommands.|`settings`|
|purge|`cow purge {n}`|Clears the last `n` messages.|`clear`, `purge`|
|quote|`cow quote {id} (channel)`|Quotes a message given an id and an optional channel.|`quote`|

### Settings Subcommands

| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|disable|`cow settings disable {cmd} {channel(s)}`|Disables a command in the specified channels.|`disable`|
|enable|`cow settings enable {cmd} {channel(s)}`|Enables a command in the specified channels.|`enable`|

### Fun
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|rps|`cow rps {item}`|Plays rock paper scissors!|`rps`|
|easteregg|`cow easteregg`|Sends a random message!|`easteregg`|

### Gambling/Economy
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|daily|`cow daily`|Gives you your daily money!|`daily`|
|money|`cow money (mention)`|Displays your money or someone else's money.|`money`|
|slots|`cow slots {amount}`|Gamble for money!|`slots`, `gamble`|

### Calendar Parser
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|schedule|`cow schedule {day}`|Tells you the schedule for a given day.|`schedule`|
|weekschedule|`cow weekschedule {week}`|Tells you the schedule for a given week.|`weekschedule`, `week-schedule`, `week_schedule`|
