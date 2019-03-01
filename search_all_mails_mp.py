#!/usr/bin/env python
from multiprocessing.pool import Pool
from multiprocessing import JoinableQueue as Queue
from multiprocessing import Lock, Process
import re
import os
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

WORKERS = 8
MAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+&-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
KILLPILL = "|"


def output(lock, msg):
    with lock:
        sys.stdout.write(msg)


def handle_found(lock, gmails, mail, path, line):
    output(lock, "{}|{}|{}".format(mail, path, line))
    gmail = gmails.get(mail, False)
    if gmail:
        # print it twice: for @gmail and @googlemail.
        output(lock, "{}|{}|{}".format(gmail, path, line))


def handle_file(lock, mails, gmails, path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            mail = MAIL_REGEX.search(line[:1024])  # even for sql statements, reading 1024 bytes should be enough
            if mail and mail.group() in mails:
                handle_found(lock, gmails, mail.group(), path, line)


def explore_path(lock, mails, gmails, path):
    directories = []
    # print("Working on {}".format(path))
    for filename in os.listdir(path):
        fullname = os.path.join(path, filename)
        if os.path.isdir(fullname):
            directories.append(fullname)
        else:
            handle_file(lock, mails, gmails, fullname)
    return directories


# https://stackoverflow.com/questions/11920490/how-do-i-run-os-walk-in-parallel-in-python
def parallel_worker(lock, unsearched, mails, gmails):
    # print("Started worker :)")
    while True:
        path = unsearched.get()
        if path == KILLPILL:
            # End.
            unsearched.task_done()
            return

        try:
            # print("getting it from {}".format(unsearched))
            # print("it's {}".format(path))
            dirs = explore_path(lock, mails, gmails, path)
            for newdir in dirs:
                unsearched.put(newdir)
            unsearched.task_done()
        except Exception as ex:
            sys.stderr.write("{}\n".format(ex))
            unsearched.task_done()


def read_mails(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        mails = set()
        gmails = {}
        for line in f:
            mail = line.strip().lower()
            # Treat gmail and googlemail as equal but only use the original form
            parts = mail.split("@")

            if not len(parts) > 1:
                # Invalid mail.
                continue

            mails.add(mail)
            if parts[1] == "gmail.com":
                gmails[mail] = "{}@{}".format(parts[0], "googlemail.com")
            if parts[1] == "googlemail.com":
                gmails[mail] = "{}@{}".format(parts[0], "gmail.com")
        return mails, gmails


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python search_all_mails_mp.py [mail.txt] [path1] ([pathN])")
        print(
            "Each line in the mail text file needs to be a mail addr only. "
            "(Non-mail lines are ignored, unless they contain an @ symbol)")
        raise Exception("Needs more paths as arguments")

    # print("main")
    unsearched = Queue()  # paths to do

    # https://emailregex.com/
    lock = Lock()

    mail_list = sys.argv[1]

    mails, gmails = read_mails(mail_list)

    for path in sys.argv[2:]:
        # Search all paths passed in as params
        unsearched.put(path)

    processess = []
    for i in range(WORKERS):
        p = Process(target=parallel_worker, args=(lock, unsearched, mails, gmails))
        p.start()
        processess.append(p)

    unsearched.join()

    for i in range(WORKERS):
        unsearched.put(KILLPILL)
    for p in processess:
        p.join()
    sys.stderr.write('Done')
