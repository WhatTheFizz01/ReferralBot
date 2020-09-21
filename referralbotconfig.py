from configparser import ConfigParser, ExtendedInterpolation
import urllib.parse


class ReferralBotConfig(object):
    """
    Global configuration handler

    There's probably a better Python pattern
    """

    def __init__(self, filename):
        config: ConfigParser = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(filename)

        self._bot_message_link: str = ''.join((config.get('Bot Message', 'baseUrl'),
                                               '&subject=',
                                               urllib.parse.quote(config.get('Bot Message', 'subject')),
                                               '&message=',
                                               urllib.parse.quote(config.get('Bot Message', 'message'))
                                               ))

        self._user_message_link: str = ''.join((config.get('User Message', 'baseUrl'),
                                                '&subject=',
                                                urllib.parse.quote(config.get('User Message', 'subject')),
                                                '&message=',
                                                urllib.parse.quote(config.get('User Message', 'message'), "{,}")
                                                ))

        self._activation: str = config.get('Links', 'activation')
        self._age_requirement: int = int(config.get('validation', 'ageRequirement'))
        self._age_verification_failed_message: str = config.get('Messages', 'ageVerificationFailed')
        self._announcement_subject: str = config.get('Announcements', 'subject')
        self._announcement_success_message: str = config.get('Announcements', 'success')
        self._botname: str = config.get('referralbot', 'botName')
        self._bot_about_message: str = config.get('Bot Message', 'aboutMessage')
        self._bot_error_message: str = config.get('Bot Message', 'errorMessage')
        self._code_regex: str = config.get('validation', 'codeRegex')
        self._contact_name: str = config.get('referralbot', 'contactName')
        self._home_subreddit: str = config.get('referralbot', 'subreddit')
        self._html_match_success: str = config.get('validation', 'htmlMatchSuccess')
        self._karma_failed_message: str = config.get('Messages', 'karmaFailed')
        self._karma_requirement: int = int(config.get('validation', 'karmaRequirement'))
        self._no_referrals_found_message: str = config.get('Referral Request Messages', 'noReferralsFound')
        self._noreply_message: str = config.get('Messages', 'noreply')
        self._optin_message: str = config.get('Opt-In Messages', 'success')
        self._optin_duplicate_message: str = config.get('Opt-In Messages', 'duplicate')
        self._optin_invalid_code_message: str = config.get('Opt-In Messages', 'invalidCode')
        self._referral_base_url: str = config.get('Links', 'referralBaseUrl')
        self._referral_source_type: str = config.get('referralbot', 'referralOutputMethod')

        if self._referral_source_type == 'wiki':
            self._referral_list_name: str = config.get('wiki', 'referralList')
            self._renewal_list_name: str = config.get('wiki', 'renewalList')
        else:
            self._referral_list_name: str = config.get('file', 'referralList')
            self._renewal_list_name: str = config.get('file', 'renewalList')

        self._referral_message: str = config.get('Referral Request Messages', 'referralMessage')
        self._referrer_message: str = config.get('Referral Request Messages', 'referrerMessage')
        self._referrer_subject: str = config.get('Referral Request Messages', 'referrerSubject')
        self._renewal_complete: str = config.get('Process Renewal Messages', 'complete')
        self._renewal_complete_subject: str = config.get('Process Renewal Messages', 'completeSubject')
        self._renewal_duplicate_message: str = config.get('Renewal Request Messages', 'duplicate')
        self._renewal_failed_message: str = config.get('Process Renewal Messages', 'failed')
        self._renewal_invalid_code_message: str = config.get('Renewal Request Messages', 'invalidCode')
        self._renewal_process_success: str = config.get('Process Renewal Messages', 'success')
        self._renewal_message: str = config.get('Renewal Request Messages', 'success')
        self._request_subject: str = config.get('Referral Request Messages', 'requestSubject')
        self._service_link: str = config.get('Links', 'serviceLink')
        self._service_name: str = config.get('referralbot', 'serviceName')
        self._update_approved_text: str = config.get('referralbot', 'updateApprovedText')

    @property
    def activation(self) -> str:
        return self._activation

    @property
    def age_failed_message(self) -> str:
        return self._age_verification_failed_message

    @property
    def age_requirement(self) -> int:
        return self._age_requirement

    @property
    def announcement_subject(self) -> str:
        return self._announcement_subject

    @property
    def announcement_success_message(self) -> str:
        return self._announcement_success_message

    @property
    def botname(self) -> str:
        return self._botname

    @property
    def bot_about_message(self) -> str:
        return self._bot_about_message

    @property
    def bot_error_message(self) -> str:
        return self._bot_error_message

    @property
    def bot_message_link(self) -> str:
        return self._bot_message_link

    @property
    def code_regex(self) -> str:
        return self._code_regex

    @property
    def contact_name(self) -> str:
        return self._contact_name

    @property
    def home_subreddit(self) -> str:
        return self._home_subreddit

    @property
    def html_match_success(self) -> str:
        return self._html_match_success

    @property
    def karma_failed_message(self) -> str:
        return self._karma_failed_message

    @property
    def karma_requirement(self) -> int:
        return self._karma_requirement

    @property
    def no_referrals_found_message(self) -> str:
        return self._no_referrals_found_message

    @property
    def noreply_message(self) -> str:
        return self._noreply_message

    @property
    def optin_message(self) -> str:
        return self._optin_message

    @property
    def optin_duplicate_message(self) -> str:
        return self._optin_duplicate_message

    @property
    def optin_invalid_code_message(self) -> str:
        return self._optin_invalid_code_message

    @property
    def referral_base_url(self) -> str:
        return self._referral_base_url

    @property
    def referral_list_name(self) -> str:
        return self._referral_list_name

    @property
    def referral_message(self) -> str:
        return self._referral_message

    @property
    def referral_source_type(self) -> str:
        return self._referral_source_type

    @property
    def referrer_message(self) -> str:
        return self._referrer_message

    @property
    def referrer_subject(self) -> str:
        return self._referrer_subject

    @property
    def renewal_complete(self) -> str:
        return self._renewal_complete

    @property
    def renewal_complete_subject(self) -> str:
        return self._renewal_complete_subject

    @property
    def renewal_duplicate_message(self) -> str:
        return self._renewal_duplicate_message

    @property
    def renewal_failed_message(self) -> str:
        return self._renewal_failed_message

    @property
    def renewal_invalid_code_message(self) -> str:
        return self._renewal_invalid_code_message

    @property
    def renewal_list_name(self) -> str:
        return self._renewal_list_name

    @property
    def renewal_message(self) -> str:
        return self._renewal_message

    @property
    def renewal_process_success(self) -> str:
        return self._renewal_process_success

    @property
    def request_subject(self) -> str:
        return self._request_subject

    @property
    def service_link(self) -> str:
        return self._service_link

    @property
    def service_name(self) -> str:
        return self._service_name

    @property
    def update_approved_text(self) -> str:
        return self._update_approved_text

    @property
    def user_message_link(self) -> str:
        return self._user_message_link
