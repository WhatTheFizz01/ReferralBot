from praw import Reddit

from handler.filehandlers import FileReferralHandler, FileRenewalHandler
from handler.handlers import AbstractHandler
from handler.wikihandlers import WikiReferralHandler, WikiRenewalHandler
from referralbotconfig import ReferralBotConfig


class ReferralProcessor(object):
    """
    Class for processing Referrals.

    Attributes:
        _config (referralbotconfig.ReferralBotConfig): Global configuration
    """

    def __init__(self, config: ReferralBotConfig, reddit: Reddit):

        self._config: ReferralBotConfig = config

        if config.referral_source_type == 'wiki':
            self._referralHandler: AbstractHandler = WikiReferralHandler(config, reddit)
            self._renewalHandler: AbstractHandler = WikiRenewalHandler(config, reddit)
        else:
            self._referralHandler: AbstractHandler = FileReferralHandler(config, reddit)
            self._renewalHandler: AbstractHandler = FileRenewalHandler(config, reddit)

    def process(self):
        self._referralHandler.replace(self._renewalHandler.get_raw_text())
        self._renewalHandler.replace('')

    def is_renewal_approved(self):
        return self._config.update_approved_text in self._referralHandler.get_raw_text()
