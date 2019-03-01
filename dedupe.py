# /usr/bin/env python3
import codecs
import sys
import re
from collections import defaultdict

MAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+&-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
IP_REGEX = re.compile(r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
KILLPILL = "|"

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

mails = defaultdict(set)

# These things we want ot handle, at least if they include passwords.
Parseables = r"""
email@secondtld:password (also exists with 3 tlds)
username@empo.ru@mail.ru:alibaba1

email:password
user@gmail.com:somepass12

email[space]:password
user@domain.de :morepass12

email;password
user@gmail.com;somepass12

email\tpassword
username@freenet.de	03423

password:hash[space]:mail (exists without space, too)
univers11:$H$9gPJoPSDbwAisCTj5M0cEIcwpOSvC2.:mail@usertld.nl

username:password:mail
User:p4ssw9rd:username@gmail.com

username;password;mail
User;p4ssw9rd;username@gmail.com

email:hash:password/salt(?)
user@googlemail.com:fff1d2284429f8401e24a3bf1b29cca4:y9aezigr

email:hash
usermail@googlemail.com:4096$12$4$9nAH70G38jHRGne%$c349476f68e3f99c999e89e9e7c1bdb08f6d81aa879613746eb0247517e14f8c

username:email:passwort/hash?
username:username@web.de:7e4c4c6275cc8a9c

name:email:ip:password
username:user@gmail.com:82.82.1.11:somepwd007

email;hash;password
user@googlemail.com;fff1d2284429f8401e24a3bf1b29cca4;something

email;hash;password(?)
username@hotmail.de;bd16321b360c27c1dbd26ff451b1832c;iAn9i_MFK3NLanpL\"VN+jX15(G2lZ{

email
user@googlemail.com

name/pass?:email:bitcoinfoo:bitcoinfoo:bitcoinfoo
username:username@googlemail.com:0.00000000:0.00000000:0.00000000

email:hash:morehash?
username@tin.it:c4890ac7a2202a9709a20478ad2902f9:IulV7zAFyaQ1YCvbVMEaUsbcH9WmSICw

email:[empty]
username@googlemail.com:

name,email,pass
Username,username@hotmail.com,eversomething

name:hash:salt:email:ip
Username:5e0fd6fb9a6770f56a3a52a16778c624:qyXwADGf:username@hotmail.com:10.10.10.10

username?/questonmarks:[space]mail:password
?????? ??? ?????: username@web.de:w1nn0r!!

username:hash:salt:mail:ip' (note the apostrophe)
username:63e5b6f3259fe38e83431b26790f1846:Tr7RbhmZ:username@hotmail.com:94.1.1.1'

|id|username|hash|mail|clearname||||something
|172840|username|5192701e7724617149990de2a40b2467|username@gmail.com|Username||||NULL
"""

# We don't handle SQLs at the moment. Most only contain hashes.
SQLs = r"""
SQL (?)  @F:\Collection#2-5\Collection #2_New combo cloud_UPDATES_November 4th 2018_Update Dumps\BitcoinTalk.org_Forum_sha256crypt_&_SMF_2015-05 (514k+ Users) - PRIVATE.txt
(37417,	2,	'',	0,	'username',	'dbdf6d92aba8be1838c0ac48c4959622',	'2011-01-01',	'username@googlemail.com',	0,	'',	'',	'',	'',	'',	2,	0,	'Newbies',	0,	1236708439,	0,	1320836978,	1320836982,	1267264882,	4,	10,	5,	'-1',	2,	0,	0,	0,	11557975,	'01-01-1901',	'1901-01-01',	-1,	-1,	'83.149.73.77',	0,	1,	'',	0,	0,	2,	14,	12,	'u.40D4$IEG7)lcwjxVRj$CgWy1KD6\"',	'',	0,	1581513,	0,	0,	0,	0,	'',	0,	0,	200,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	100,	1,	'',	1333000863,	0,	0,	0,	1,	1,	'',	'',	0,	'',	'vb',	'',	0,	1,	0,	0,	0,	0,	'0',	0,	0,	0,	'',	'',	0,	NULL),

F:\Collection#1\Collection  #1_NEW combo semi private_Update Dumps\BitcoinTalk.org_Forum_sha256crypt_&_SMF_2015-05 (514k+ Users) - PRIVATE.txt
INSERT INTO `smf_members` VALUES (44783,'username',1319652971,21,0,'',1431816460,'username',14,0,'','','','','$5$rounds=7500$+5pt+/0iuRvENmeV$zJPgw1lT2Wt1DNmbj7A7xJXfZtD/mKtGxDB7bUivX34','username@googlemail.com','',0,'0001-01-01','','','','','','','',1,1,'','',0,'',1,0,0,'',1,1,0,2,'95.211.1.1','95.211.1.1','my home town','2d5d182c2122c17f4f6748d2163ffd34',0,1,'',11394692,'','',12,118530,'1fc6',0,'',0,2,21,0,0,NULL);

SQL (hashed, salted) @F:\Collection#2-5\Collection #3_Dump checkyou\checkyou\forums.malwarebytes.org\MalwareBytes_ipb_members_11_15_2014.sql
INSERT INTO `ibf_members` (`member_id`, `name`, `member_group_id`, `email`, `joined`, `ip_address`, `posts`, `title`, `allow_admin_mails`, `time_offset`, `skin`, `warn_level`, `warn_lastwarn`, `language`, `last_post`, `restrict_post`, `view_sigs`, `view_img`, `bday_day`, `bday_month`, `bday_year`, `msg_count_new`, `msg_count_total`, `msg_count_reset`, `msg_show_notification`, `misc`, `last_visit`, `last_activity`, `dst_in_use`, `coppa_user`, `mod_posts`, `auto_track`, `temp_ban`, `login_anonymous`, `ignored_users`, `mgroup_others`, `org_perm_id`, `member_login_key`, `member_login_key_expire`, `has_blog`, `members_auto_dst`, `members_display_name`, `members_seo_name`, `members_created_remote`, `members_cache`, `members_disable_pm`, `members_profile_views`, `members_l_display_name`, `members_l_username`, `failed_logins`, `failed_login_count`, `has_gallery`, `members_pass_hash`, `members_pass_salt`, `member_banned`, `member_uploader`, `members_bitoptions`, `fb_uid`, `fb_emailhash`, `fb_lastsync`, `members_day_posts`, `live_id`, `twitter_id`, `twitter_token`, `twitter_secret`, `notification_cnt`, `tc_lastsync`, `fb_session`, `fb_token`, `ips_mobile_token`, `unacknowledged_warnings`, `blogs_recache`, `ipsconnect_id`, `ipsconnect_revalidate_url`) VALUES ('2893', 'username', '19', 'username@gmx.de', '1216225492', '93.134.230.107', '0', '', '1', '0', '0', '', '0', '1', '', '0', '1', '1', '', '', '', '0', '0', '0', '0', '', '1216225531', '1216225531', '0', '0', '0', '0', '0', '0&1', '', '', '', 'd1410edf0a9a2280a155a62440ebb7bd', '1216830403', '0', '1', 'username', 'username', '0', '', '0', '399', 'username', 'username', '', '0', '0', 'ec8a40382f887f335eb83f4ed216f741', 'fRz#<', '0', 'default', '0', '0', '', '0', '0,0', '', '', '', '', '0', '0', '', '', '', '', '', '0', '');

SQL (hashed, salted) F:\Collection#2-5\Collection #3_Dump checkyou\checkyou\hackforums.net2\hackforums.txt
,(635330, 'username', '63e5b6f3259fe38e83431b26790f1846', 'Tr7RbhmZ', 'tP7ULC938r3W5grIEkBkxXtrAq1m9qaWApvDNMW78gC6eZtMMK', 'username@hotmail.com', 0, 0, 0.00, NULL, NULL, NULL, 2, NULL, 0, NULL, 1294772026, 1295911088, 1295559707, 0, NULL, 0, NULL, NULL, NULL, '30-4-1986', 'all', NULL, NULL, 1, 0, 2, 0, 1, 2, 0, 'linear', 1, 1, 1, 1, 0, 0, 0, NULL, NULL, 1, 0, 2, NULL, NULL, 0, 0, 0, 0, NULL, NULL, NULL, 0, 0, 0, '94.252.94.42', '94.252.94.42', 1593597482, 1593597482, NULL, 1033, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, NULL)

F:\Collection#1\Collection  #1_NEW combo semi private_Update Dumps\Avast_2014_400k.txt
(11195454,'username','',NULL,'','username','username@googlemail.com',NULL,'a9c9bf38985cde3dd06e03f13b891416e8740f77','','',0,'avast.com'),

SQL (Hashed) F:\Collection#2-5\Collection #3_Dump checkyou\checkyou\h4cky0u.org\h4cky0u_db.sql
(1420, 0, 2, '', 0, '84.63.14.5', 1232005456, 'Username', 'username', '$H$9CA50tCxqan/X1RnmhvoHAUOBzWzPo/', 1232005456, 0, 'username@gmx.de', 197685577614, '', 1232005502, 1232005456, 0, 'viewtopic.php?f=9&t=694&hilit=adultbouncer', '', 1232005496, 0, 0, 0, 0, 0, 0, 'en', 1.00, 0, 'D M d, Y g:i a', 3, 0, '', 0, 0, 0, 0, -3, 0, 0, 't', 'd', 0, 't', 'a', 0, 1, 0, 1, 1, 1, 1, 895, '', 0, 0, 0, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '88c0653bcd42597d'),

SQL (NO PASS) F:\Collection#2-5\Collection #3_Dump checkyou\checkyou\forumcore.com\forumcore.sql
(12918, 'username', 3, 'username@googlemail.com', 1329602197, '91.51.1.1', 17, NULL, 1, '1', NULL, NULL, 0, 1, 1329999622, '0', 1, 1, 0, 0, 0, 0, 0, 0, 1, NULL, 1346205210, 1348839268, 0, 0, '0', '', '0', '0&1', 'a:0:{}', '', '', '7acec25dc7272b81527fe37d18072092', 1349444068, NULL, 0, 0, 'username', 'username', 0, NULL, 0, 'username', 'username', '', 0, 180, 'a05de14d9c0d08e4442eab8b40ea2cd4', '|bSFL', 0, 'flash', 0, 0, '', 0, '1,1329999622', NULL, '', '', '', 0, 0, '', NULL, NULL, 0, NULL, NULL, '', '', 0, 0, 0, 0),

SQL (Hash) F:\Collection#2-5\Collection #3_OLD LEAK\1337-crew_members.txt
(112,'username',3,'username@msn.com',1180039025,'84.162.103.98',5,'',1,'0','1',1,NULL,NULL,0,0,NULL,NULL,'0',1,1,1,1,1,1,1,0,0,0,0,'db30',1245510023,0,0,'-1&-1',0,'0','0','0',0,'0&0',NULL,'','','6d2f4adc6fd8a0cb33fb5e42cf32fb32',1251371121,0,0,0,'std',1,'username','username',0,NULL,0,'username','username',NULL,0,0,'','',NULL,0,'default',0,0,'',0,0,'0,0','095c5eb538cc872d7619f8f08d8d4d12033c1370','1:1:1',0,3),

SQL (Hash) F:\Collection#2-5\Collection #3_Dump checkyou\checkyou\blackhatworld.com\blackhatworld.txt
(507447,	2,	'',	0,	'S-T-H',	'dbdf6d92aba8be1838c0ac48c4959622',	'2012-01-01',	'username@t-online.de',	0,	'',	'',	'',	'',	'',	2,	0,	'Newbies',	0,	1352464643,	0,	1352464643,	1352465100,	0,	0,	10,	5,	'0',	2,	0,	0,	0,	45112519,	'09-05-1985',	'1985-09-05',	-1,	-1,	'176.198.176.1',	0,	1,	'',	0,	0,	2,	2,	2,	'RmyIXrcDe??yIG\\36Op0Dr1Uhe`9+l',	'',	0,	0,	0,	0,	0,	0,	'',	0,	0,	11,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	0,	100,	1,	'',	0,	0,	0,	0,	1,	1,	'',	'',	0,	'',	'vb',	'',	0,	1,	0,	0,	0,	0,	NULL,	0,	0,	0,	'',	'',	0,	NULL),
"""


class ExtractException(Exception):
    def __init__(self, extract_failure, line):
        Exception.__init__(self, "{}: <<{}>>".format(extract_failure, line))
        self.line = line
        self.extract_failure = extract_failure


def cleaned(line):
    """
    This is the `beef`: It'll try to parse a line and figure out the password to it.
    To get the mail, use the MAIL_REGEX above like:
        try:
            email = MAIL_REGEX.search(line).group()
        except: 
            print("oops, no mail in {}".format(line)
    :param line: The line
    :return: the password in the line, hopefully. 
    :raise If we can't figure out the format, we'll raise an ExtractException. This can generally be ignored.
    """
    def nonempty(password):
        password = password.strip()
        if len(password) < 1:
            raise ExtractException("Password is empty", line)
        return password

    line = line.strip()  # Let's hope no password ends with a space...
    line1k = line[:1024]
    try:
        email = MAIL_REGEX.search(line1k).group()
    except:
        raise ExtractException("No email found in line", line)

    # handle special case where mail is the last element
    if line.endswith(email):
        try:
            splitter = line.rsplit(email, 1)[0][-1]
        except:
            raise ExtractException("Invalid splitter", line)
        if splitter not in [":", ";"]:
            raise ExtractException("Unknown splitter for right mail", line)
        # password:hash[space]:mail (exists without space, too)
        # univers11:$H$9gPJoPSDbwAisCTj5M0cEIcwpOSvC2.:mail@usertld.nl
        # or
        # username:password:mail
        doublesplit = line.rsplit(splitter, 1)[0].split(splitter, 1)
        if len(doublesplit) < 2:
            raise ExtractException("Empty entry", line)
        if doublesplit[1].startswith("$H$") or len(doublesplit[1]) == 32:  # it's a hash
            return nonempty(doublesplit[0])
        else:
            # assume first part to be username, second password
            return nonempty(doublesplit[1])

    # normal case. Email is somewhere in the middle or at the start.
    try:
        # get the char right behind the mail, assume it's the splitter.
        # strip because we assume spaces can exist after email before the splitter
        # same for \, @ and _
        splitter = line1k.split(email)[1].replace("_", "").replace("\\", "").replace("@", "").strip()[0]
    except:
        raise ExtractException("Invalid line (no content behind mail)", line)

    if splitter not in [";", ":", ",", "\t"]:
        raise ExtractException("Not a supported splitter. New format, SQL or sth else", line)

    split1 = line.split(splitter, 1)
    splittercount = line.count(splitter)

    def mail_hash_or_nohash():
        # email:hash[len32]:password
        if splittercount > 1:
            split2 = line.split(splitter, 2)
            if len(split2[1]) == 32:
                return nonempty(split2[2])

        return nonempty(split1[1])

    if splitter == ":":
        if email in split1[0]:
            return mail_hash_or_nohash()

        if email in split1[1]:
            split3 = line.split(":", 3)
            try:
                # check for name:email:ip:password
                if IP_REGEX.search(split3[2]):
                    return nonempty(split3[3])
            except:
                pass

            try:
                # don't return username:username@googlemail.com:0.00000000:0.00000000:0.00000000
                account_standings = split3[3].split(":")
                # float(x.xxx) + float(x.xxx) should be a float, else throw an exception
                if isinstance((float(account_standings[0]) + float(account_standings[1])), float):
                    raise ExtractException("we don't care for the blockchain.", line)
            except ExtractException:
                raise
            except:
                pass
            # assume username:email:passwort/hash?
            return nonempty(split1[1].split(":", 1)[1])

        if split1[0] == "?????? ??? ?????" and splittercount > 1:
            # ?????? ??? ?????: username@web.de:w1nn0r!!
            return line.split(":", 2)[2]

    if splitter == ";" or splitter == "\t":
        return mail_hash_or_nohash()

    if splitter == ",":
        if split1[1].startswith(email):
            # name,email,pass
            try:
                return nonempty(split1[1].split(",", 1)[1])
            except:
                raise ExtractException("Unknown format for comma line (name,email,pass)", line)

        raise ExtractException("Expected comma line to start with mail (name,email,pass)", line)

    assert 0, "I SHOULDN'T REACH THIS WITH {} (splitter {})".format(line, splitter)


def parse_lines(lines, out, err):
    for line in lines:
        elements = line.split(KILLPILL, 2)  # our format is generally mail|location|line
        if len(elements) < 3:
            sys.stderr.write("Broken line: {}\n".format(line))
        else:
            try:
                mail = elements[0]
                password = cleaned(elements[2])
            except ExtractException as ex:
                err.write("{}\n".format(ex))
                continue
            if not password:
                raise ExtractException("No password recieved. This is likely an internal bug.", line)
            mails[mail].add(password)

    for mail, passwords in sorted(mails.items(), key=lambda x: str(x[0])):
        for password in sorted(list(passwords)):
            # yield "{}:{}".format(mail, password)
            out.write(mail)
            out.write(":")
            out.write(password)
            out.write("\n")


# line = r"mail@mail.de||username:mail@mail.de:password"
# parse_lines([line])
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("This tool will parse and deduplicate the results from ./search_all_mails_mp.py")
        print("Usage: ./dedupe.py [search_all_mails_mp.outfile] > deduped.txt")
        exit(1)
    with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as f:
        # with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as f:
        parse_lines(f, sys.stdout, sys.stderr)
