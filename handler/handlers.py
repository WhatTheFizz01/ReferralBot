from abc import ABC, abstractmethod
import random
from typing import List
import re

from exception.exceptions import NoReferralsFoundException
from referralbotconfig import ReferralBotConfig
from referral import Referral
import praw


class AbstractHandler(ABC):

    def __init__(self, config: ReferralBotConfig, reddit: praw.Reddit):
        self._config: ReferralBotConfig = config
        self._reddit: praw.Reddit = reddit

    @abstractmethod
    def _get_list_name(self) -> str:
        pass

    @abstractmethod
    def _get_raw_text(self, source: str) -> str:
        pass

    @abstractmethod
    def _replace(self, text: str, source: str) -> None:
        pass

    @abstractmethod
    def _save(self, referral: Referral, source: str) -> bool:
        pass

    def get_all(self) -> List[Referral]:
        return self._get_all(self._get_list_name())

    def get_random(self) -> Referral:
        return self._get_random(self._get_list_name())

    def get_usernames(self) -> List[str]:
        return self._get_usernames(self._get_list_name())

    def get_raw_text(self) -> str:
        return self._get_raw_text(self._get_list_name())

    def is_duplicate(self, referral: Referral) -> bool:
        return self._is_duplicate(referral, self._get_list_name())

    def replace(self, raw_text: str):
        self._replace(raw_text, self._get_list_name())

    def save(self, referral: Referral) -> bool:
        return self._save(referral, self._get_list_name())

    def _get_all(self, source: str) -> List[Referral]:
        referrals = self._get_referrals_str(source)

        referrals_list: List[Referral] = []

        for referral in referrals:
            items = referral.split(':')
            if len(items) == 2:
                redditor = self._reddit.redditor(items[0])
                referrals_list.append(Referral(self._config, redditor, items[1]))

        return referrals_list

    def _get_codes(self, source: str) -> List[str]:
        referrals = self._get_referrals_str(source)

        codes_list: List[str] = []

        for referral in referrals:
            items = referral.split(':')
            if len(items) == 2:
                codes_list.append(items[1].upper())

        return codes_list

    def _get_random(self, source: str) -> Referral:
        # avoids the extra blank lines
        referrals = self._get_referrals_str(source)

        referral = random.sample(referrals, 1)[0]
        referral = referral.strip()

        items = referral.split(':')
        if len(items) == 2:
            redditor = self._reddit.redditor(items[0])
            return Referral(self._config, redditor, items[1].upper())
        else:
            raise NoReferralsFoundException()

    def _get_referrals_str(self, source: str) -> List[str]:
        referrals_string: str = self._get_raw_text(source)

        # get all the raw referrals text and split on newline
        # remove all empty entries and return a list
        referrals: List[str] = list(filter(None, re.split(r'[\n]+', referrals_string)))

        return referrals

    def _get_usernames(self, source: str) -> List[str]:
        referrals: List[str] = self._get_referrals_str(source)

        users_list: List[str] = []

        for referral in referrals:
            items = referral.split(':')
            if len(items) == 2:
                users_list.append(items[0])

        return users_list

    def _is_duplicate(self, referral: Referral, source: str) -> bool:
        return referral.get_code.upper() in self._get_codes(source)
