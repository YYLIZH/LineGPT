# LineGPT

[中文](README_zh_TW.md) | English

A linebot with assistance of ChatGPT.

## Usage

The functions of LineGPT are defined by several commands. You can use help to list available commands. <br>

```
@LineGPT help
```
![help](doc/en/help_en.jpg)
## ChatGPT

Let ChatGPT help you.

```
@LineGPT gpt help
```
![gpt help](doc/en/gpt_help_en.jpg)
## Weather (Currently only support weather in Taiwan)

Check the weather in your place.

```
@LineGPT weather help
```
![weather help](doc/en/weather_help_en.jpg)
![weather use](doc/en/weather_use_en.jpg)
## Settle

Need to know how much you should pay? Let LineGPT settle a groups' expense!

```
@LineGPT settle help
```
![settle help](doc/en/settle_help_en.jpg)

## Developer's guide

### Environment variable

Settings are listed in a .env file. Here offering a template '.env.template' for user to setup your personal setting for this bot.<br>
| Item                      | Necessity | Default value | Note                                                                                                                                                                                                |
| ------------------------- | :-------: | :-----------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LANGUAGE                  |    NO     |     zh_TW     | Default is Traditional Chinese.                                                                                                                                                                     |
| LINE_CHANNEL_SECRET       |    YES    |      ""       | Channel secret of LINE. You can check [this link](https://developers.line.biz/en/services/messaging-api/) for more information                                                                      |
| LINE_CHANNEL_ACCESS_TOKEN |    YES    |      ""       | Channel access token of LINE. You can check [this link](https://developers.line.biz/en/services/messaging-api/) for more information                                                                |
| SESSION_EXPIRE            |    NO     |      600      | To save the memory, you can not talk to ChatGPT after <SESSION_EXPIRE> time since last update.                                                                                                      |
| WEATHER_TOKEN             |    NO     |      ""       | You can set your own token or simply use mine. If you want to use your own token. Please refer the [official website](https://opendata.cwb.gov.tw/devManual/insrtuction) to see how to get a token. |

Note: After you fill in these variable, please rename the .env.template to .env.

### Testing

1. Start the server

```
uvicorn api.index:app --reload --loop asyncio
```

api page will be
http://127.0.0.1:8000/docs

2. Open ngrok

```
ngrok http 8000
```

![ngrok](doc/ngrok.png)

3. Copy the https url to line bot webhook url. The result will be <your url>/webhook
   ![webhook](doc/webhook.png)

4. Check verify button to see if the url works.
5. You can send message to your bot.

### Deploy

1. Vercel
   Fork this project to your github to use vercel. You can import the .env file in Settings > Environment Variables.

2. Container
   You can also deploy your bot by docker. Note that Linebot only take https url, so you may need to verify your domain first.

### Issues, questions and PRs

Bug reports, issues, and PRs are always welcome. If you face any questions, welcome to [discuss page](https://github.com/YYLIZH/LineGPT/discussions) to discuss.
