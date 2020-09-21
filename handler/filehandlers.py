from abc import ABC

from exception.exceptions import DuplicateCodeException
from handler.handlers import AbstractHandler
from referral import Referral


class AbstractFileHandler(AbstractHandler, ABC):
    """
    Abstract File Handler

    Abstract class for File handlers to inherit common functionality
    """
    def _get_raw_text(self, source: str) -> str:
        with open(source) as file:
            content: str = file.read()

        return content

    def _save(self, referral: Referral, source: str) -> bool:
        referral.check_format()
        referral.validate()

        if self._is_duplicate(referral, source):
            raise DuplicateCodeException()

        with open(source, 'at') as file:
            # add the entry with two leading newlines for readability
            file.write("\n\n{new_user}:{code}".format(new_user=referral.get_user,
                                                      code=referral.get_code))

        return True

    def _replace(self, raw_text: str, source: str):
        # w = overwrite the file
        with open(source, 'wt') as file:
            file.write(raw_text)


class FileReferralHandler(AbstractFileHandler):
    """
    File handler for referrals
    """

    def _get_list_name(self) -> str:
        return self._config.referral_list_name


class FileRenewalHandler(AbstractFileHandler):
    """
    File handler for renewals
    """

    def _get_list_name(self) -> str:
        return self._config.renewal_list_name
