#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import praw
import time
import traceback
import logging

from praw.exceptions import RedditAPIException

from exception.exceptions import ReferralBotFatalException
from responder import Responder
from referralbotconfig import ReferralBotConfig

# Start logger
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s %(message)s')

# Log into Reddit API
try:
    reddit = praw.Reddit(client_id=os.environ["CLIENT_ID"],
                         client_secret=os.environ["CLIENT_SECRET"],
                         password=os.environ["REDDIT_PASSWORD"],
                         user_agent='script:PMAutomaticReplyBot:v1',
                         username=os.environ["REDDIT_USERNAME"])
except KeyError:
    reddit = praw.Reddit('bot1')


def handle():
    config: ReferralBotConfig = ReferralBotConfig('referralbot.ini')
    print("Starting...")
    logging.info("[Info] Starting bot in {type} mode...".format(type=config.referral_source_type))

    while True:
        print("Checking inbox...")

        try:
            for message in reddit.inbox.unread(limit=None):
                responder = Responder(reddit, config, message)
                responder.run()
                message.mark_read()
            time.sleep(30)

        except ReferralBotFatalException:
            print("FATAL error occurred. Here's the traceback: \n {} \n\n Exiting!".format(traceback.format_exc()))
            logging.fatal("[FATAL] {msg}".format(msg=format(traceback.format_exc())))
            logging.fatal("[FATAL] Bot is terminating")
            exit(1)
        except RedditAPIException:
            # probably rate limited. Sleep for a minute
            print("Error occurred. Here's the traceback: \n {} \n\n Sleeping...".format(traceback.format_exc()))
            logging.warning("[Warning] Error occurred.  Stacktrace follows: \n {}".format(traceback.format_exc()))
            time.sleep(60)
        except Exception:
            print("Error occurred. Here's the traceback: \n {} \n\n Sleeping...".format(traceback.format_exc()))
            logging.warning("[Warning] Error checking inbox.  Stacktrace follows: \n {}".format(traceback.format_exc()))
            time.sleep(30)


if __name__ == "__main__":
    handle()
