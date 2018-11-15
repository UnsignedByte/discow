# Discow
A Python3 bot for Discord using discord.py.  
Created by [UnsignedByte](https://github.com/UnsignedByte) and licensed under [The MIT License](https://en.wikipedia.org/wiki/MIT_License).  
Add this bot to your server [here](https://discordapp.com/api/oauth2/authorize?client_id=427609586032443392&permissions=8&scope=bot)!

**Features:**
* Lots of commands! Including, but not limited to:
  * Quiz creating and taking!
  * Stock trading!
  * Moderation!
  * Gambling!
  * And more!
  * Ping logging!

## Commands
Prefix: `cow`

Necessary arguments: `{var}`  
Optional arguments: `(var)`  
Remember to delete `{}` and `()`.


### Utilities

| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|help|`cow help (page)`|Displays help information. If no valid page number is given, the first page will be displayed.|`help`|
|info|`cow info`|Displays general information about the bot.|`info`, `hi`|
|close|`cow close`|Shut down the bot and save all data.|`close`, `shutdown`|
|save|`cow save`|Save all data.|`save`|
|settings|`cow settings {args}`|Look at Settings Subcommands.|`settings`|
|purge|`cow purge {n}`|Clears the last `n` messages.|`clear`, `purge`|
|quote|`cow quote {id} (channel)`|Quotes a message given an id and an optional channel.|`quote`|
|define|`cow define {word}`|Retrieves the definition of a word from Merriam-Webster.|`define`, `dictionary`|
|wolframalpha|`cow wolframalpha {query}`|Queries wolframalpha and returns an image containing the result|`wolframalpha`, `wolfram`, `wa`|

#### Settings Subcommands

| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|settings|`cow settings {subcommand} (args)`|Settings for the bot. Requires the `manage server` permission. | `settings`|
|disable|`cow settings disable {cmd} {channel(s)}`|Disables a command in the specified channels.|`disable`|
|enable|`cow settings enable {cmd} {channel(s)}`|Enables a command in the specified channels.|`enable`|

### Fun
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|invite|`cow invite`|Creates an invite link for the server!|`invite`|
|thesaurus|`cow thesaurus`|Thesaurus-ifies a sentence.|`thesaurus`|
|rps|`cow rps {item}`|Plays rock paper scissors!|`rps`|
|quiz|`cow quiz {subcommand}`|Create quizzes and take them for money! For more information take a look at Quiz Subcommands.|`quiz`|
|trivia|`cow trivia (difficulty) (category)`|Answer trivia questions for money!|`trivia`|

#### Quiz Subcommands

| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|setmod|`cow quiz setmod {role mention}`|Choose a role for moderating quiz questions, categories, etc.|`setmod`, `modrole`|
|add|`cow quiz add {question}`|Adds a quiz question to your server! Follow the Question Wizard's instructions.|`add`|
|take|`cow quiz take (category)`|Take a quiz! Follow the Quiz Wizard's instructions.|`take`|

### Gambling/Economy
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|daily|`cow daily`|Gives you your daily money!|`daily`|
|money|`cow money (mention)`|Displays your money or someone else's money.|`money`|
|bank|`cow bank`|Displays your bank account information.|`bank`|
|deposit|`cow deposit {amount}`|Deposits Mooney into your bank account.|`deposit`, `dep`|
|withdraw|`cow withdraw {amount}`|Withdraws Mooney from your bank account.|`withdraw`, `with`|
|convert|`cow convert {amount} {currency}`|Converts from Mooney to another currency. Will not work if other bot is not online. Do `cow convert` to see currency types.|`convert`|
|stock|`cow stock {subcommand} {name}`|View, buy, and sell stocks using realtime stock information from the nasdaq website. For more info look at Stock Subcommands.|`stock`, `stocks`|
|slots|`cow slots {amount}`|Gamble for money!|`slots`, `gamble`|

#### Stock Subcommands
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|buy|`cow stock buy {name}`|Buy virtual stocks|`buy`, `invest`|
|sell|`cow stock sell {name}`|Sell virtual stocks.|`sell`|
|get|`cow stock get {name}`|View realtime stock information from the nasdaq website.|`get`, `info`|

#### Ping Logging
| **Name** | **Usage** | **Description** | **Aliases** |
|:-:|:-:|:-:|:-:|
|who ping|`who ping`|Check pings|None|
|clear ping|`clear ping`|Clear saved pings|None|
