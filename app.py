#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import os
import praw
from praw.models import Message
from praw.exceptions import APIException, PRAWException, ClientException
import random
import re
import time
import traceback
import logging

# Start logger
logging.basicConfig(filename='log.txt',level=logging.INFO,format='%(asctime)s %(message)s')

# Log into Reddit API
try:
    reddit = praw.Reddit(client_id=os.environ["CLIENT_ID"],
                         client_secret=os.environ["CLIENT_SECRET"],
                         password=os.environ["REDDIT_PASSWORD"],
                         user_agent='script:PMAutomaticReplyBot:v1',
                         username=os.environ["REDDIT_USERNAME"])
except KeyError:
    reddit = praw.Reddit('bot1')

# Used in response messages
PM_MOBILE_LINK = "https://productioncommunity.publicmobile.ca/t5/Rewards/Refer-a-Friend-Reward/m-p/411#M4"

USER_MESSAGE_LINK = "https://www.reddit.com/message/compose/?to={username}" \
                    "&subject=PM%20Mobile%20Referral&message=" \
                    "Hello%20{username}!%20The%20PM%20Referral%20Bot%20directed%20me%20to%20you.%20Thanks%20" \
                    "for%20the%20referral%20number!"

BOT_MESSAGE_LINK = "https://www.reddit.com/message/compose?to=/u/PMReferralBot&subject=" \
                   "PM%20Referral&message=Referral%20Please"

ACTIVATION = "https://activate.publicmobile.ca/"

REFERRAL_LIST = "https://www.reddit.com/r/PublicMobile/wiki/referrals"

FUTURE_REFERRAL_LIST = "https://www.reddit.com/r/PublicMobile/wiki/referrals-nextmonth"


class Responder(object):
    """
    Class for responding to a Message for PM Referrals.

    Attributes:
        message (praw.models.Message): Object of Message from user
        _user (str): Author of message
        _replyMessage (str): Message body to send back
        _referer (str); Username of person who will refer the user
    """

    def __init__(self, message):
        self._message = message  # Message
        self._user = message.author
        self._replyMessage = "Hello {user}! \n\n ".format(user=self._user)

    def run(self):
        """Handles the actions for Responder"""
        print("Responding to {}".format(self._user))
        logging.info("[Info] Responding to {}".format(self._user))
        if self._user == "[deleted]":
            logging.warning("[Warning] {} is a invalid user.  Not responding..".format(self._user))
        elif self._user == "reddit":
            logging.warning("[Warning] {} is an automatic Reddit message.  Not responding..".format(self._user))
        elif self._verify():
            print("User age verified")
            logging.info("[Info] {} age verified".format(self._user))
            if "Renewal".lower() in self._message.subject.lower():
                if self._verifykarma():
                    print("User karma verified")
                    logging.info("[Info] {} karma verified".format(self._user))
                    self._build_message()
                    self._reply()
                else:
                    print("User karma verification failed")
                    logging.info("[Info] Failed karma verification, replying with karma requirement information.")
                    self._replyMessage += \
                        " You failed the account karma requirement and your request was not processed. \n\n" \
                        " We require the account to have at least 3 combined karma to reduce the amount of abuse received." \
                        " Please compose another request to renew after this requirement is satisfied. \n\n" \
                        " Please remember to compose a new message instead of replying to this message to complete your request.  Subject lines are case sensitive." \
                        " \n \nThanks for using the Public Mobile Referral Bot!" \
                        "\n \n" \
                        " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*"
                    self._reply()
            elif "Opt-in".lower() in self._message.subject.lower():
                if self._verifykarma():
                    print("User karma verified")
                    logging.info("[Info] {} karma verified".format(self._user))
                    self._build_message()
                    self._reply()
                else:
                    print("User karma verification failed")
                    logging.info("[Info] Failed karma verification, replying with karma requirement information.")
                    self._replyMessage += \
                        " You failed the account karma requirement and your request was not processed. \n\n" \
                        " We require the account to have at least 3 combined karma to reduce the amount of abuse received." \
                        " Please compose another request to opt into our list after this requirement is satisfied. \n\n" \
                        " Please remember to compose a new message instead of replying to this message to complete your request.  Subject lines are case sensitive." \
                        " \n \nThanks for using the Public Mobile Referral Bot!" \
                        "\n \n" \
                        " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*"
                    self._reply()
            else:
                print("Skipping user karma verification, not required")
                logging.info("[Info] Skipped karma verification, not required.")
                self._build_message()
                self._reply()
        else:
            print("User age verification failed")
            logging.info("[Info] Failed age verification, replying with age requirement information.")
            self._replyMessage += \
                " You failed the account age requirement and your request was not processed. \n\n" \
                " We require the account to be at least 24 hours old to reduce the amount of abuse received." \
                " Please compose another request after this requirement is satisfied. \n\n" \
                " Please remember to compose a new message instead of replying to this message to complete your request.  Subject lines are case sensitive." \
                " \n \nThanks for using the Public Mobile Referral Bot!" \
                "\n \n" \
                " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*"
            self._reply()

    def _verify(self) -> bool:
        """
        Verifies the user's account is older than a day. All time objects use UTC.

        Returns:
            bool: True if self._user's account age is older than a day
        """
        current_time = datetime.utcnow()

        user_created = self._user.created_utc

        one_day = timedelta(days=1)

        return current_time - datetime.fromtimestamp(user_created) > one_day
        
    def _verifykarma(self) -> bool:
        # Verifies user for at least 3 combined karma.  Returns true or false dependent on result.
        
        combined_karma = self._user.link_karma + self._user.comment_karma
        min_karma = int('3')
        return combined_karma > min_karma
    
    def _get_referral_user(self) -> None:
        """
        Gets _user as a randomly selected element from a list of user's who opted in to referring other customers.
        User list here: https://reddit.com/r/PublicMobile/wiki/referrals
        Regex expression taken from
            https://stackoverflow.com/questions/2596771/regex-to-split-on-successions-of-newline-characters
            Ex:
                a = "Foo\r\n\r\nDouble Windows\r\rDouble OS X\n\nDouble Unix\r\nWindows\rOS X\nUnix"
                b = re.split(r'[\r\n]+', a)
                ['Foo', 'Double Windows', 'Double OS X', 'Double Unix', 'Windows', 'OS X', 'Unix']
        """
        page = reddit.subreddit("PublicMobile").wiki['referrals']
        users_string = page.mod.wikipage.content_md
        users = re.split(r'[\r\n]+', users_string)

        self._referer = random.sample(users, 1)[0]
        self._referer = self._referer.strip()
        logging.info("[Info] Selected {} as referrer".format(self._referer))

    def _build_message(self):
        """Build the response to the user."""

        if "PM Referral".lower() in self._message.subject.lower():
            # Give them a referral
            logging.info("[Info] Responding to referrer request")
            self._get_referral_user()
            message_referer_link = USER_MESSAGE_LINK.format(username=self._referer)
            self._replyMessage += \
                " Thanks for showing interest in Public Mobile. When signing up," \
                " you can get a referral number from /u/{referer}. Click [here]({message_referer_link}) to " \
                "message /u/{referer}. \n\n Alternatively, click [here]({pm_referrals_link}) to get more information " \
                "on how referrals work." \
                "\n \n" \
                "**Please Note**: Numbers can **ONLY** be used during [Public Mobile activations]({activation}).  Other usage is strictly prohibited and will result in a ban." \
                "\n \n" \
                " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(
                    referer=self._referer,
                    message_referer_link=message_referer_link,
                    pm_referrals_link=PM_MOBILE_LINK,
                    activation=ACTIVATION)
            
            # Required for notification message to report abuse easily
            REPORT_LINK = "https://www.reddit.com/message/compose?to=/u/IEpicDestroyer&subject=Report%20User%20for%20Referral%20Bot%20Abuse%20-%20{REPORT_USER}&message=Reason%20for%20Report:%20".format(
                REPORT_USER=self._user)
            
            notify_message = \
                "Hello {notify_user}! \n\n" \
                "You have been recommended to refer {referred_user} to Public Mobile.  /u/{referred_user} has been notified to contact you.\n\n" \
                "If the user requests a referral from you, please respond quickly to obtain the referral.  Users do not wish to wait for a referral and will gladly skip to the next in order to secure a referral for an activation.\n\n" \
                "Please **do not reply** to this message as replies are not handled.  Please contact /u/{referred_user} directly to arrange the referral.\n\n" \
                "If you are suspicious of the user, you may wish to ignore the user or report the incident [here]({REPORT_LINK}).\n\n" \
                "*^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(
                    notify_user=self._referer,
                    referred_user=self._user,
                    REPORT_LINK=REPORT_LINK)
            reddit.redditor(self._referer).message('Public Mobile - Referral Notification', notify_message)
            logging.info("[Info] Sent Referral Notification Message to " + self._referer)

        elif "re:" in self._message.subject:
            # They are responding to our message. What to do?
            logging.info("[Info] Responding to a reply")
            print("User {} replied to our message. This is the message: \n"
                  "Subject: {} \n Message Body: {}".format(self._user, self._message.subject, self._message.body))
            # Respond to the message directing them to the reddit
            self._replyMessage += \
                " This bot does not accept any replies of messages. \n\n" \
                " If there is anything else that you need help with, you can compose a new message with your request or visit /r/PublicMobile for more assistance!" \
                " I am unable to help you with anything else unless you would like another referral by clicking [here]({bot_link}) or messaging /u/PMReferralBot." \
                "\n \n" \
                " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(bot_link=BOT_MESSAGE_LINK)
        elif "Opt-in".lower() in self._message.subject.lower():
            # Check if user already exist and update wiki list
            page = reddit.subreddit("PublicMobile").wiki['referrals']
            users_string = page.mod.wikipage.content_md
            users = re.split(r'[\r\n]+', users_string)
            users = [user.strip() for user in users]
            if self._user not in users:
                updated_list = users_string + "\n\n{new_user}".format(new_user=self._user)
                page.edit(updated_list)
                self._replyMessage += \
                     " Your opt in request has been successfully received!\n" \
                     " Your request has been automatically completed.  Please check the [referral list wiki]({wiki}) to confirm. \n\n" \
                    " Please remember to renew your enrollment before the 15th of every month to remain on the list.  Failure to complete renewal will drop your name from the list." \
                    " \n\n**Reminder**: Please be cautious of handing out your Public Mobile number to avoid abuse or scams!  " \
                    " \nThanks for using the Public Mobile Referral Bot!" \
                    "\n \n" \
                    " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(wiki=REFERRAL_LIST)
                logging.info("[Info] Responding with Opt-In completion confirmation")
            else:
                self._replyMessage += \
                    "Your username is already on the referral list.  Please check the [referral list wiki]({wiki}) to confirm.\n\n" \
                    "If this message was not expected, please send /u/IEpicDestroyer a message regarding this error." \
                    "\n \n" \
                    " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(wiki=REFERRAL_LIST)
                logging.info("[Info] Responding with Opt-In duplicate refusal")
        elif "Renewal".lower() in self._message.subject.lower():
            # Check if user already exist and update wiki list
            page = reddit.subreddit("PublicMobile").wiki['referrals-nextmonth']
            users_string = page.mod.wikipage.content_md
            users = re.split(r'[\r\n]+', users_string)
            users = [user.strip() for user in users]
            if self._user not in users:
                updated_list = users_string + "\n\n{new_user}".format(new_user=self._user)
                page.edit(updated_list)
                self._replyMessage += \
                    " Your enrollment renewal request has been successfully received!\n" \
                    " Your request will be automatically updated with the scheduled task on the 15th of every month.  You may choose to check the pending referrals for next month [here]({nextmonth}).  " \
                    " \n**Reminder**: Please be cautious of handing out your Public Mobile number to avoid abuse or scams!" \
                    " \n \nThanks for using the Public Mobile Referral Bot!" \
                    "\n \n" \
                    " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(nextmonth=FUTURE_REFERRAL_LIST)
                logging.info("[Info] Responding with renewal completion confirmation")
            else:
                self._replyMessage += \
                    "Your username is already on the future referral list.  Please check the [future referral list wiki]({nextmonth}) to confirm.\n\n" \
                    "If this message was not expected, please send /u/IEpicDestroyer a message regarding this error." \
                    "\n \n" \
                    " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(nextmonth=FUTURE_REFERRAL_LIST)
                logging.info("[Info] Responding with renewal duplicate refusal")

        elif "Replace Month".lower() in self._message.subject.lower():
            newpage = reddit.subreddit("PublicMobile").wiki['referrals']
            approval_check = newpage.mod.wikipage.content_md
            if "Update Approved".lower() in approval_check.lower():
                logging.info("[Info] Processing list updates...")
                page = reddit.subreddit("PublicMobile").wiki['referrals-nextmonth']
                users_string = page.mod.wikipage.content_md
                users = re.split(r'[\r\n]+', users_string)
                users = [user.strip() for user in users]
                users = list(filter(None, users))
                newpage.edit(users_string)
                message_body =\
                    " Hi everyone! \n\n" \
                    " Thank you again for your support for the Public Mobile Referral Bot!!!\n\n" \
                    " Thank you for renewing your enrollment to the Public Mobile referral list.  Your enrollment is confirmed until the 15^th of next month.  Please remember to renew before the 10^th of next month.\n  " \
                    " Failure to renew will result your name being dropped from the referral list.  You will be required to manually join back to continue to receive referrals.\n  " \
                    " Thank you again for your support for the Public Mobile Referral Bot! \n\n" \
                    " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*"
                for users in users:
                    reddit.redditor(users).message("Public Mobile Referral Bot - Successful Renewal", message_body)
                page.edit("IEpicDestroyer")
                self._replyMessage += \
                    " Successfully updated referral list and sent notification messages.  Please check logs to verify."
            else:
                logging.info("[Info] Responding with general response.  Refusing list update request.")
                self._replyMessage += \
                    " Unfortunately, we are unable to complete this request.  \n" \
                    " Please try your request again later. " \
                    "\n \n" \
                    " If you were looking for a specific request, I did not understand your request.  Please compose a new message and verify the correct subject is included.  Subject lines are case sensitive. \n\n" \
                    " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(bot_link=BOT_MESSAGE_LINK)
        elif "Announcement".lower() in self._message.subject.lower():
            # Note: If this is used to message users without consent, consequences may arise
            if str(self._user).lower() == "IEpicDestroyer".lower():
                logging.info("[Info] Sending mass message...")
                page = reddit.subreddit("PublicMobile").wiki['referrals-nextmonth']
                users_string = page.mod.wikipage.content_md
                users = re.split(r'[\r\n]+', users_string)
                users = [user.strip() for user in users]
                users = list(filter(None, users))
                message_body = self._message.body
                for users in users:
                    reddit.redditor(users).message("Public Mobile Referral Bot - Announcement", message_body)
                self._replyMessage += \
                    " Successfully sent announcement to all members.  Please check logs to verify."
            else:
                logging.info("[Info] Responding with general response.  Refusing announcement request.")
                self._replyMessage += \
                    " Unfortunately, we are unable to complete this request.  \n" \
                    " Please try your request again later. " \
                    "\n \n" \
                    " If you were looking for a specific request, I did not understand your request.  Please compose a new message and verify the correct subject is included.  Subject lines are case sensitive. \n\n" \
                    " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*"
        else:
            # Tell them more about PM Mobile
            logging.info("[Info] Responding with general response")
            self._replyMessage += \
                " I am a bot that can help you get a referral number for Public Mobile." \
                " We have a list of Public Mobile users who are happy to have their number used" \
                " for referrals. If you want to get a referral number, send /u/PMReferralBot a message with the subject \"PM Referral\"" \
                " as the subject or alternatively click [here]({bot_link})." \
                "\n \n" \
                " If you were looking for a specific request, I did not understand your request.  Please compose a new message and verify the correct subject is included.  Subject lines are case sensitive. \n\n" \
                " *^(This is an automatic bot response.  Please contact /u/IEpicDestroyer with any questions or concerns.)*".format(bot_link=BOT_MESSAGE_LINK)

    def _reply(self):
        """Send a reply to the user"""

        def send_message():
            self._message.reply(self._replyMessage)

        try:
            send_message()
            print("Message send successful to {}".format(self._user))
            logging.info("[Info] Successfully responded to {}".format(self._user))
        except (APIException, PRAWException, ClientException) as e:
            print(e)
            logging.warning("[Warning] Error sending message.  Stacktrace followed: \n" + e)

            # In case of RateLimitExceeded
            time.sleep(10)
            send_message()
            print("Message send successful")
            logging.info("[Info] Successfully responded to {} after ratelimit cooldown".format(self._user))
        except Exception as e:
            print("Didn't send message. This is why: \n {}".format(e))
            logging.warning("[Warning] Error sending message.  Stacktrace followed: \n" + e)

def handle():
    print("Starting...")
    logging.info("[Info] Starting bot...")
    while True:
        print("Checking inbox...")
        try:
            for item in reddit.inbox.unread(limit=100):
                if isinstance(item, Message):
                    pm = Responder(item)
                    pm.run()
                    item.mark_read()
            time.sleep(30)

        except Exception:
            print("Error occurred. Here's the traceback: \n {} \n\n Sleeping...".format(traceback.format_exc()))
            logging.warning("[Warning] Error checking inbox.  Stacktrace followed: \n {}".format(traceback.format_exc()))
            time.sleep(30)


if __name__ == "__main__":
    handle()
