# Performing the necessary imports 
import re
import requests
from flask import Flask, request
import telegram
from newsbot.news_credentials import bot_token, bot_user_name,URL 
from time import sleep

global bot
global TOKEN #from BotFather
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

# start the flask app
app = Flask(__name__)

#Function to access API 
def get_content():
    url = ('http://newsapi.org/v2/top-headlines?'
           'country=us&'
           'apiKey=bc06c2ceab2148698006caef89a4e111')
    response = requests.get(url).json()
    articles = response['article']

def format_content():
    articles = get_content()
    return_list=[]
    for a in articles:
        source=a['source']['name']
        author=a['author']
        title=a['title']
        url=a['url']
        return_list.append('\n\nAgency: '+str(source)+'\nAuthor :'+str(author)+'\nTitle: '+title+'\n\nread here: '+str(url))

    if len(return_list)>5:
        return return_list[:5]


#Bind function to route - telling flask what to do when a URL is called
#This is the URL Tele will call to get responses 
@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
   # retrieve the message in JSON and then transform it to Telegram object
   update = telegram.Update.de_json(request.get_json(force=True), bot)

   chat_id = update.message.chat.id
   msg_id = update.message.message_id

   # Telegram understands UTF-8, so encode text for unicode compatibility
   text = update.message.text.encode('utf-8').decode()
   # for debugging purposes only
   print("got text message :", text)
   # the first time you chat with the bot AKA the welcoming message
   if text == "/start":
       # print the welcoming message
       bot_welcome = """
       Welcome to NewsBot. Send a message saying 'news' to this bot and get the trending news headline.
       """
       #show 'typing' under bot name
       bot.sendChatAction(chat_id=chat_id, action="typing")
       sleep(1.5)
       # send the welcoming message
       bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

   elif text=="news":
       try:
           # create the api link for the avatar based on
           news = format_content()
           #show 'sending photo' under bot name 
           bot.sendChatAction(chat_id=chat_id, action="typing")
           sleep(4)
           # reply with the top 5 news articles
           bot.sendMessage(chat_id=chat_id, text = " ".join(news), reply_to_message_id=msg_id)
       except Exception:
           # if things went wrong
           bot.sendMessage(chat_id=chat_id, text="There was a problem, please try again.", reply_to_message_id=msg_id)
    
   else:
       text = "Invalid input. Send a message saying 'news' to receive latest headlines."
       bot.sendChatAction(chat_id=chat_id, action="typing")
       sleep(1.5)
       bot.sendMessage(chat_id=chat_id, text =text, reply_to_message_id=msg_id)

   return 'ok'

#Webhooks help alter the behaviour of webpages using custom callbacks. So the server is called by webhook only when the bot receoves a message.
@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    # we use the bot object to link the bot to our app which live
    # in the link provided by URL
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    # something to let us know things work
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'
if __name__ == '__main__':
    # note the threaded arg which allow
    # your app to have more than one thread
    app.run(threaded=True)

