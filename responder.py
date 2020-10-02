#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import praw
from praw.models import Message
from praw.exceptions import APIException, PRAWException, ClientException
import time
import logging

from prawcore import NotFound, Forbidden, BadRequest

from exception.exceptions import InvalidCodeFormatException, InvalidCodeException, DuplicateCodeException, \
    NoReferralsFoundException, ReferralBotFatalException
from handler.filehandlers import FileReferralHandler, FileRenewalHandler
from handler.handlers import AbstractHandler
from referralbotconfig import ReferralBotConfig
from handler.wikihandlers import WikiReferralHandler, WikiRenewalHandler
from referral import Referral
from renewalprocessor import ReferralProcessor


class Responder(object):
    """
    Class for responding to a Message for Referrals.

    Attributes:
        message (praw.models.Message): Object of Message from user
        _user (str): Author of message
        _replyMessage (str): Message body to send back
        _referrer (str); Username of person who will refer the user
    """

    def __init__(self, reddit: praw.Reddit, config: ReferralBotConfig, message: Message):
        self._message: Message = message
        self._user = message.author
        self._config: ReferralBotConfig = config
        self._reddit: praw.Reddit = reddit
        self._replyMessage: str = "Hello {user}! \n\n ".format(user=self._user)

        self._referral_list_name: str = ''
        self._renewal_list_name: str = ''

        if config.referral_source_type == 'wiki':
            self._referralHandler: AbstractHandler = WikiReferralHandler(config, reddit)
            self._renewalHandler: AbstractHandler = WikiRenewalHandler(config, reddit)
        else:
            self._referralHandler: AbstractHandler = FileReferralHandler(config, reddit)
            self._renewalHandler: AbstractHandler = FileRenewalHandler(config, reddit)

    def run(self):
        """Handles the actions for Responder"""
        print("Responding to {}".format(self._user))
        logging.info("[Info] Responding to {}".format(self._user))
        if self._user == "[deleted]":
            logging.warning("[Warning] {} is a invalid user.  Not responding..".format(self._user))
        elif self._user == "reddit":
            logging.warning("[Warning] {} is an automatic Reddit message.  Not responding..".format(self._user))
        elif self._verify_account_age():
            print("User age verified")
            logging.info("[Info] {} age verified".format(self._user))
            if self._message.subject.lower() in ['Renewal'.lower(), 'Opt-in'.lower()]:
                if self._verifykarma():
                    print("User karma verified")
                    logging.info("[Info] {} karma verified".format(self._user))
                    self._build_message()
                    self._reply()
                else:
                    print("User karma verification failed")
                    logging.info("[Info] Failed karma verification, replying with karma requirement information.")
                    self._replyMessage += self._config.karma_failed_message
                    self._reply()
            else:
                print("Skipping user karma verification, not required")
                logging.info("[Info] Skipped karma verification, not required.")
                self._build_message()
                self._reply()
        else:
            print("User age verification failed")
            logging.info("[Info] Failed age verification, replying with age requirement information.")
            self._replyMessage += self._config.age_failed_message
            self._reply()

    def _verify_account_age(self) -> bool:
        """
        Verifies the user's account is older than X day(s). All time objects use UTC.

        Returns:
            bool: True if self._user's account age is older than a day
        """
        current_time = datetime.utcnow()

        user_created = self._user.created_utc

        age_requirement = timedelta(days=self._config.age_requirement)

        return current_time - datetime.fromtimestamp(user_created) > age_requirement

    def _verifykarma(self) -> bool:
        # Verifies user for at least X combined karma.  Returns true or false dependent on result.

        combined_karma = self._user.link_karma + self._user.comment_karma
        min_karma = self._config.karma_requirement
        return combined_karma > min_karma

    def _get_referral(self) -> Referral:
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
        referral: Referral = self._referralHandler.get_random()
        self._referrer = referral.get_user
        logging.info("[Info] Selected {} as referrer".format(referral.get_user))

        return referral

    def _build_message(self):
        """Build the response to the user."""

        if self._message.subject.startswith("re: "):
            # They are responding to our message. What to do?
            logging.info("[Info] Responding to a reply")
            print("User {} replied to our message. This is the message: \n"
                  "Subject: {} \n Message Body: {}".format(self._user, self._message.subject, self._message.body))
            # Respond to the message directing them to the reddit
            self._replyMessage += self._config.noreply_message
        elif self._config.request_subject.lower() in self._message.subject.lower():
            self._build_message_get_referral()
        elif "Opt-in".lower() in self._message.subject.lower():
            self._build_message_optin()
        elif "Renewal".lower() in self._message.subject.lower():
            self._build_message_renewal()
        elif "Replace Month".lower() in self._message.subject.lower():
            self._build_message_process_renewals()
        elif "Announcement".lower() in self._message.subject.lower():
            self._build_message_announcement()
        else:
            # Tell them more about PM Mobile
            logging.info("[Info] Responding with general response")
            self._replyMessage += self._config.bot_about_message

    def _build_message_get_referral(self):
        # Give them a referral
        logging.info("[Info] Responding to referrer request")

        try:
            referral: Referral = self._get_referral()
        except NoReferralsFoundException:
            self._replyMessage += self._config.no_referrals_found_message
            logging.info("[Info] Sent No Referral Found Notification Message to " + self._config.contact_name)
        else:
            self._reddit.redditor(referral.get_user.name).message(
                self._config.referrer_subject,
                self._config.referrer_message.format(notify_user=referral.get_user, code=referral.get_code))
            logging.info("[Info] Sent Referral Notification Message to " + referral.get_user.name)
            self._replyMessage += self._config.referral_message.format(
                code=referral.get_code,
                referrer=referral.get_user)

    def _build_message_optin(self):
        r = Referral(self._config, self._user, self._message.body)

        try:
            self._referralHandler.save(r)
        except(InvalidCodeFormatException, InvalidCodeException):
            self._replyMessage += self._config.optin_invalid_code_message.format(code=r.get_code)
            logging.info("[Info] Responding with Opt-In invalid code refusal")
        except DuplicateCodeException:
            self._replyMessage += self._config.optin_duplicate_message.format(code=r.get_code)
            logging.info("[Info] Responding with Opt-In duplicate refusal")
        except (PermissionError, FileNotFoundError, NotFound, Forbidden, BadRequest) as e:
            error = "{exception_type} writing Opt-In to {type}:{target}".format(
                exception_type=e.__class__.__name__,
                type=self._config.referral_source_type,
                target=self._config.referral_list_name)
            logging.fatal("[FATAL] " + error)
            raise ReferralBotFatalException(error)
        else:
            self._replyMessage += self._config.optin_message.format(code=r.get_code)
            logging.info("[Info] Responding with Opt-In completion confirmation")

    def _build_message_renewal(self):
        r = Referral(self._config, self._user, self._message.body)

        try:
            self._renewalHandler.save(r)
        except(InvalidCodeFormatException, InvalidCodeException):
            self._replyMessage += self._config.renewal_invalid_code_message.format(code=r.get_code)
            logging.info("[Info] Responding with renewal invalid code refusal")
        except DuplicateCodeException:
            self._replyMessage += self._config.renewal_duplicate_message.format(code=r.get_code)
            logging.info("[Info] Responding with renewal duplicate refusal")
        except (PermissionError, FileNotFoundError, NotFound, Forbidden, BadRequest) as e:
            error = "{exception_type} writing renewal to {type}:{target}".format(
                exception_type=e.__class__.__name__,
                type=self._config.referral_source_type,
                target=self._config.renewal_list_name)
            logging.fatal("[FATAL] " + error)
            raise ReferralBotFatalException(error)
        else:
            self._replyMessage += self._config.renewal_message.format(code=r.get_code)
            logging.info("[Info] Responding with renewal completion confirmation")

    def _build_message_process_renewals(self):
        rp = ReferralProcessor(self._config, self._reddit)

        try:
            is_renewal_approved = rp.is_renewal_approved()
        except (PermissionError, FileNotFoundError, NotFound, Forbidden) as e:
            error = "{exception_type} error checking renewal approval from: {type}:{target}".format(
                exception_type=e.__class__.__name__,
                type=self._config.referral_source_type,
                target=self._config.referral_list_name)
            logging.fatal("[FATAL] " + error)
            raise ReferralBotFatalException(error)
        if is_renewal_approved:
            logging.info("[Info] Processing list updates...")
            try:
                rp.process()
            except (PermissionError, FileNotFoundError, NotFound, Forbidden) as e:
                error = "{exception_type} error processing renewals from:" \
                            " {type}:{source} to: {type}:{target}".format(
                                                        exception_type=e.__class__.__name__,
                                                        type=self._config.referral_source_type,
                                                        source=self._config.renewal_list_name,
                                                        target=self._config.referral_list_name)
                logging.fatal("[FATAL] " + error)
                raise ReferralBotFatalException(error)
            message_body = self._config.renewal_complete
            users = self._referralHandler.get_usernames()
            for user in users:
                self._reddit.redditor(user).message(self._config.renewal_complete_subject, message_body)
            self._replyMessage += self._config.renewal_process_success
        else:
            logging.info("[Info] Responding with general response.  Refusing list update request.")
            self._replyMessage += self._config.renewal_failed_message

    def _build_message_announcement(self):
        # Note: If this is used to message users without consent, consequences may arise
        if str(self._user).lower() == self._config.contact_name.lower():
            logging.info("[Info] Sending mass message...")
            users = self._referralHandler.get_usernames()
            message_body = self._message.body
            for user in users:
                self._reddit.redditor(user).message(self._config.announcement_subject, message_body)
            self._replyMessage += self._config.announcement_success_message
        else:
            logging.info("[Info] Responding with general response.  Refusing announcement request.")
            self._replyMessage += self._config.bot_error_message

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
