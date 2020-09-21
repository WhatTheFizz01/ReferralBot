import ssl
import urllib.request
import re

from exception.exceptions import InvalidCodeFormatException, InvalidCodeException
from referralbotconfig import ReferralBotConfig
from praw.models import Redditor


class Referral(object):
    """
    Referral object

    Attributes:
        _config (referralbotconfig.ReferralBotConfig): Global configuration
        _referrer (praw.models.Redditor): the Redditor corresponding to the referral code
        _code (str): the referral code
    """

    def __init__(self, config: ReferralBotConfig, referrer: Redditor, code: str):
        self._referrer: Redditor = referrer
        self._code: str = code.strip().upper()
        self._config: ReferralBotConfig = config

    def validate(self) -> bool:
        """Check the URL if the format is good

        Returns:
            bool: True = format is good
                   False = format is incorrect
        """
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(self._createlink()) as response:
            html = response.read().decode('utf-8')
            # look for the checkbox icon on the page
            if re.search(self._config.html_match_success, html) is None:
                raise InvalidCodeException()

        return True

    def check_format(self) -> bool:
        matcher = re.compile(self._config.code_regex, re.IGNORECASE)
        if not matcher.match(self._code):
            raise InvalidCodeFormatException()

        return True

    def _createlink(self) -> str:
        return self._config.referral_base_url + self._code

    @property
    def get_user(self) -> Redditor:
        return self._referrer

    @property
    def get_code(self) -> str:
        return self._code
