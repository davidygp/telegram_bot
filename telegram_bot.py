#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Scrape a Climbing Website: Onsight
# Connect to Telegram and send updates. IF there are changes.


# In[2]:


# # When running in jupyter notebook, sometimes need to do this #

# import os
# import sys

# # Need to add the anaconda environment to the PYTHONPATH
# env_paths = ['/home/davidyam/anaconda3/envs/tele_bot/lib/python36.zip', 
#              '/home/davidyam/anaconda3/envs/tele_bot/lib/python3.6', 
#              '/home/davidyam/anaconda3/envs/tele_bot/lib/python3.6/lib-dynload', 
#              '/home/davidyam/anaconda3/envs/tele_bot/lib/python3.6/site-packages']

# sys.path += env_paths

# # Need to add the following to path:
# # PATH=$PATH:/home/davidyam/Documents/2._Tutorials/telegram_bot/
# current_wd = os.getcwd()
# os.environ["PATH"] += ":"+current_wd

# # When running in jupyter notebook, sometimes need to do this #


# In[3]:


import json
import os
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from telegram import Bot
from telegram.ext import Updater, CommandHandler 
import time


# In[4]:


# Must download and install the latest gecko driver

# https://github.com/mozilla/geckodriver/releases


# In[5]:


# # Functions # #
def scrape_website(browser, search_field, verbose=False):
    """
        Scrapes the website and returns the list or None.
    """
    # Try to scrape the website
    try:
        abd_dates = browser.find_element_by_id(search_field)
        abd_dates_list = abd_dates.text.split("\n")
        return abd_dates_list
    except:
        return None
    
def read_cached_file(cached_filepath, verbose=False):
    """
        Read the cached file if it exist and return the cached list or None
    """
    # Read the cached file if it exists
    if os.path.exists(cached_filepath):
        if verbose: print("Cached file exists, reading it")
        # Reading the cached file
        with open(cached_filepath, 'r') as f:
            cached_abd_dates_list = f.readlines()

        cached_abd_dates_list = [x.replace("\n", "") for x in cached_abd_dates_list]
        if verbose: print(cached_abd_dates_list)
        return cached_abd_dates_list
    else:
        return None

def write_to_cache(abd_dates_list, cached_filepath, verbose=False):
    """
        Write a list to the cache file
    """
    # Writing the cached file
    with open(cached_filepath, 'w') as f:
        for item in abd_dates_list:
            f.write("%s\n" % item)
        
def run_all(bot, browser, chat_id, search_field, cached_filepath, verbose, reply):
    abd_dates_list = scrape_website(browser, search_field, verbose)
    if abd_dates_list is None:
        message_str = "David, error in scraping website & fetching content.\nPlease check."
        bot.send_message(chat_id=chat_id, text=message_str)
        
    cached_abd_dates_list = read_cached_file(cached_filepath, verbose)
    if cached_abd_dates_list != None:
        if abd_dates_list == cached_abd_dates_list:
            if verbose: print("Scrapped list and cached list are the same, no change from cache.")
            if reply: 
                t = time.time()
                message_str = "Time is:\n%s.\n\nNo Change from previous list!" %(time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(t)))
                bot.send_message(chat_id=chat_id, text=message_str)
        else:
            if verbose: print("Sending message to the group")
            changed_abd_dates_list = [x.strip() for x in abd_dates_list if x not in cached_abd_dates_list] 
            message_str = "Hi everyone!\n            This was changed on the Onsight ABD Verification Page \n%s" %("\n".join(changed_abd_dates_list))
            bot.send_message(chat_id=chat_id, text=message_str)
            
            if verbose: print("Writing into the cached file")
            write_to_cache(abd_dates_list, cached_filepath, verbose)
    else:
        if verbose: print("First time run, no cached file found.\n        writing to the cached filepath %s" %(cached_filepath))
        write_to_cache(abd_dates_list, cached_filepath, verbose)
        
        
# # Functions # #


# In[6]:


# # INFO for Onsight Website and ID to scrape # #
URL = "https://onsightventures.wufoo.com/forms/r9dr3hh00sr0r9/"

SEARCH_FIELD = "Field240" # Search ID, see Selenium, find_element_by_id()
# # Onsight Website and ID to scrape # #

# # INFO for the cached file # #
CACHED_FILEPATH = './cache.txt'
# # INFO for the cached file # #

# # INFO FOR THE TELEGRAM BOT # #
# 
TOKEN_ID_FILEPATH = "./token_id.json"
with open(TOKEN_ID_FILEPATH) as json_file:
    cfg = json.load(json_file)
# get TOKEN
# see: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API
TOKEN = cfg["TOKEN"]

# get GROUP_ID
# see: https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id

# Talk to your bot: $ /my_id @BoPangChanceYamBot
# Go to this: $ https://api.telegram.org/bot<TOKEN>/getUpdates
GROUP_ID = cfg["GROUP_ID"]
# # INFO FOR THE TELEGRAM BOT # #

# # Other Options # #
verbose = True # Whether to have verbose prints or not
# # Other Options # #


# In[7]:


# Functions for Selenium  (???)
opts = Options()
opts.headless = True
#assert opts.headless  # Operating in headless mode
browser = Firefox(options=opts)

# Parse the website
browser.get(URL)


# In[8]:


# # For the scheduled checking # #

bot = Bot(token=TOKEN)

run_all(bot, browser, chat_id=GROUP_ID, search_field=SEARCH_FIELD, cached_filepath=CACHED_FILEPATH, 
        verbose=False, reply=True) #False)

# # For the scheduled checking # #


# In[9]:


# # For the interactive bot # #

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def get_help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="I'm a BoPangChanceYamBot, ask me one of the folllowing:\n/check\n/print\n/time")
    
def check_website(update, context):
    run_all(context.bot, browser, update.effective_chat.id, search_field=SEARCH_FIELD, 
                                                   cached_filepath=CACHED_FILEPATH, 
                                                   verbose=False, reply=True)
def print_cache(update, context):
    cached_abd_dates_list = read_cached_file(CACHED_FILEPATH, verbose=False)
    if cached_abd_dates_list != None:
        message_str = "Cache is:\n\n%s" %("\n".join(cached_abd_dates_list))
        context.bot.send_message(chat_id=update.effective_chat.id, text=message_str)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No cache!")

def get_time(update, context):
    t = time.time()
    message_str = "Time is:\n%s" %(time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(t)))
    context.bot.send_message(chat_id=update.effective_chat.id, text=message_str)
       
dispatcher.add_handler(CommandHandler('help', get_help))
dispatcher.add_handler(CommandHandler('check', check_website))
dispatcher.add_handler(CommandHandler('print', print_cache))
dispatcher.add_handler(CommandHandler('time', get_time))

updater.start_polling()

# # For the interactive bot # #


# In[ ]:




