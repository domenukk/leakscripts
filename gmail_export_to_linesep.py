#!/usr/bin/env python
import csv
import os
import sys
import json

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

mail_offset = 28  # Offset of mails in google's export CSV

if len(sys.argv) != 2:
    print("Please provide a input csv, exported from gmail.")
    exit(1)

with open(sys.argv[1]) as f:
    reader = csv.reader(f)

    for line in reader:
        for i in range(mail_offset, 36, 2):
            mail = line[i]
            if mail:
                mail = mail.strip().lower()
                sys.stdout.write(mail)
                sys.stdout.write("\n")
