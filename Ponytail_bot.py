#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from uuid import uuid4
from telegram import InlineQueryResultArticle,InlineQueryResultMpeg4Gif, InlineQueryResultGif, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown
from pyfiglet import Figlet
import fortune
from pprint import pprint
import giphy_client
from giphy_client.rest import ApiException
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

F = Figlet(font='slant')

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def inlinequery(update, context):
    """Handle the inline query."""
 
    query = update.inline_query.query
 
    ##This is the other shit that can do
    f=open('log.txt','a+')
    f.write(str(update.inline_query) + '\n #### Query \t ' + query + ' #######\n')
    f.close()
    
    if query:
        q = query.split(' ')

        # create an instance of the API class
        api_instance = giphy_client.DefaultApi()
        api_key = 'your-giphy-token' # str | Giphy API Key.
        limit = 50 # int | The maximum number of records to return. (optional) (default to 25)
         # int | An optional results offset. Defaults to 0. (optional) (default to 0)
        rating = 'g' # str | Filters results by specified rating. (optional)
        lang = 'en' # str | Specify default country for regional content; use a 2-letter ISO 639-1 country code. See list of supported languages <a href = \"../language-support\">here</a>. (optional)
        fmt = 'json' # str | Used to indicate the expected response format. Default is Json. (optional) (default to json)
        
        gif_urls = []
        
        try: 
            # Search Endpoint
            offset=0
            api_response = api_instance.gifs_search_get(api_key, query, limit=limit, offset=offset, rating=rating, lang=lang, fmt=fmt)
            for gif in api_response.data:
                url = re.findall('(https://[^?]+)',gif.images.original.url)[0]
                gif_urls.append(url)
        except ApiException as e:
            print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
        
        
    else:
        gif_urls = []
        
        f=open('urls.txt','r')
        urls = f.read()
        urls = urls.split('\n')
        for url in urls:
            gif_urls.append(url)
        
    results = []
    for gif_url in gif_urls:
        results.append(InlineQueryResultGif(type='gif',id=uuid4(), gif_url=gif_url, thumb_url=gif_url))

    update.inline_query.answer(results)


def inlinequery_text(update, context):


    query = update.inline_query.query

    query = re.findall('_(.*)',query)[0]
    q = query.split(' ')
    fq = ''
    for i in q:
        if len(i) > 5:
            for r in range(0,len(i)):
                
                if r%5 == 0:
                    fq = fq + F.renderText(i[r:r+5])
                    continue
        else:
            fq = fq + F.renderText(i)
        
    results = [
         InlineQueryResultArticle(
            id=uuid4(),
            title='quotes',
            input_message_content=InputTextMessageContent(
                    fortune.get_random_fortune('fortunes'),
                    parse_mode=ParseMode.MARKDOWN
                    )),
        InlineQueryResultArticle(
            id=uuid4(),
            title='wasted',
            input_message_content=InputTextMessageContent(
                    f"{query}\n"*250,
                    parse_mode=ParseMode.MARKDOWN
                    )),
        InlineQueryResultArticle(
            id=uuid4(),
            title="figlet",
            input_message_content=InputTextMessageContent(
                "``` {} ```".format(fq),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="bold",
            input_message_content=InputTextMessageContent(
                "*{}*".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="code",
            input_message_content=InputTextMessageContent(
                "```\n {} \n```".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="cross",
            input_message_content=InputTextMessageContent(
                f"~~{query}~~",
                parse_mode=ParseMode.MARKDOWN))]
        
    
    update.inline_query.answer(results)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater('your-telegram-token(my.telegram.org)', use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery, pattern='^[^_]*$'))
    dp.add_handler(InlineQueryHandler(inlinequery_text,pattern='^_.*$'))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()