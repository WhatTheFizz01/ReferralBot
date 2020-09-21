# Referral Bot
Responds to inbox messages of people looking for Referral codes.  It is planned for expansion to different carriers on respective subreddits.

Code is licensed under GNU GPLv3.  Original code is licensed under MIT.

There are two types of messages handled:
1) Subject is "PM Referral"
    - Send a message back providing the referral code and username of the owner of the code.
    - Also notifies the owner of the referral code.
2) Subject is "Opt-in"
    - Appends sender's username to wiki "referrals" list.
3) Subject is "Renewal"
    - Appends sender's username to wiki "referrals-nextmonth" list.

##Misc Features Included:
1) Subject is "Replace Month" and "referrals" wiki when wiki only has "Update Approved" 
    - Replaces wiki "referrals" with contents of "referrals-nextmonth" and resets list.
    - Sends notification of this occurrence to all participating users 
2) Subject is "Announcement" and matches username
    - Sends out contents of the message body as a message to all participating users
    - Please Note: misuse at your own risk.


##Configuration:
Configuration is done through the referralbot.ini.

The referral system can be run from wiki pages or from local files. The referralOutputMethod value specifies "wiki" or "file", with the wiki page names or filenames defined in their associated sections.


