import pprint
from abc import ABC

from praw.models import WikiPage

from exception.exceptions import DuplicateCodeException
from handler.handlers import AbstractHandler
from referral import Referral


class AbstractWikiHandler(AbstractHandler, ABC):
    """
    Abstract Wiki Handler

    Abstract class for Wiki handlers to inherit common functionality

    Raises:
        DuplicateCodeException: code already exists in the list
    """
    def _get_raw_text(self, source: str) -> str:
        page: WikiPage = self._reddit.subreddit(self._config.home_subreddit).wiki[source]
        return page.mod.wikipage.content_md

    def _save(self, referral: Referral, source: str) -> bool:
        referral.check_format()
        referral.validate()

        if self._is_duplicate(referral, source):
            raise DuplicateCodeException()

        page = self._reddit.subreddit(self._config.home_subreddit).wiki[source]

        if not page.may_revise:
            raise PermissionError("Bot user {bot_user} does not have write access to wiki page {source}".format(
                                        bot_user=self._config.botname,
                                        source=source))

        referrals_string = page.mod.wikipage.content_md
        # add the entry with two leading newlines for readability
        updated_list = referrals_string + "\n\n{new_user}:{code}".format(
                                                                new_user=referral.get_user,
                                                                code=referral.get_code)
        page.edit(updated_list)

        return True

    def _replace(self, raw_text: str, source: str):
        page: WikiPage = self._reddit.subreddit(self._config.home_subreddit).wiki[source]

        if not page.may_revise:
            raise PermissionError("Bot user {bot_user} does not have write access to wiki page {source}".format(
                                        bot_user=self._config.botname,
                                        source=source))

        page.edit(raw_text)


class WikiReferralHandler(AbstractWikiHandler):
    """
    Wiki handler for referrals
    """

    def _get_list_name(self) -> str:
        return self._config.referral_list_name


class WikiRenewalHandler(AbstractWikiHandler):
    """
    Wiki handler for renewals
    """

    def _get_list_name(self) -> str:
        return self._config.renewal_list_name
