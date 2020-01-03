# Public Mobile Referral Bot
Responds to inbox messages of people looking for Referral codes for Public Mobile.  It is planned for expansion to different carriers on respective subreddits.

There are two types of messages handled:
1) Subject is "PM Referral"
    - Send a message back providing the referral code and username of the owner of the code.
    - Also notifies the owner of the referral code.
2) Subject is "Opt-in"
    - Appends sender's username to wiki "referrals" list.
3) Subject is "Renewal"
    - Appends sender's username to wiki "referrals-nextmonth" list.

Misc Features Included:
1) Subject is "Replace Month" and "referrals" wiki only has "Update Approved" in wiki
    - Replaces wiki "referrals" with contents of "referrals-nextmonth" and resets list.
    - Sends notification of this occurrence to all participating users 
2) Subject is "Announcement" and matches username
    - Sends out contents of the message body as a message to all participating users
    - Please Note: misuse of this is at your own risk.
