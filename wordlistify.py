#!/usr/bin/env python3
import os
import sys
from collections import defaultdict

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

pwds = defaultdict(int)
min_len = 6


def print_wordlist(lines):
    for line in lines:
        try:
            pwd = line.split(":", 1)[1].strip()
            if len(pwd) >= min_len:
                pwds[pwd] += 1
        except:
            sys.stderr.write("Error in {}".format(line))

    pwds_sorted = sorted(pwds.items(), key=lambda x: -x[1])

    for pwd, count in pwds_sorted:
        sys.stdout.write("{}:{}\n".format(count, pwd))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        pwd_filename = sys.argv[1]
        with open(pwd_filename, "r", encoding="utf-8", errors="ignore") as f:
            print_wordlist(f)
    else:
        sys.stderr.write("Usage: wordlistify.py [file from dedupe]\n"
                         "(Creates a wordlist from deduped username:password list)\n")
