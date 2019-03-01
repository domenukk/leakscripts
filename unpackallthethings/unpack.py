#!/usr/bin/env python3
import csv
import os
import shutil
import string

from sqlite2csv import dump_database_to_spreadsheets
from xls2csv import xls2csv


def heuristic_csv_copy(infile, outfile, remove):
    """"
    If it fails to parse as xls, it might be a broken csv. Let's try.
    """
    if os.path.exists(outfile):
        raise FileExistsError("File already exists: {}".format(outfile))
    try:
        with open(infile, newline='', encoding="utf-8") as csvfile:
            # https://stackoverflow.com/questions/2984888/check-if-file-has-a-csv-format-with-python
            start = csvfile.read(4096)

            # isprintable does not allow newlines, printable does not allow umlauts...
            if not all([c in string.printable or c.isprintable() for c in start]):
                return False
            dialect = csv.Sniffer().sniff(start)
    except csv.Error:
        # Could not get a csv dialect -> probably not a csv.
        return False

    if remove:
        shutil.move(infile, outfile)
    else:
        shutil.copyfile(infile, outfile)
    return True


def recurse(path, remove=False):
    count = count_xls = count_csv = count_sql = existed = failed_xls = failed_sql = 0
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            count += 1
            in_file = os.path.join(root, name)
            lname = name.lower()
            if lname.endswith(".xls") or lname.endswith(".xlsx"):
                print("Working on {}".format(in_file))
                out_file = in_file + ".csv"
                try:
                    # going to work
                    xls2csv(in_file, out_file)
                    count_xls += 1
                    if remove:
                        os.remove(in_file)
                except FileExistsError as e:
                    print("Skipping existing file {}".format(out_file))
                    existed += 1
                except Exception as e:
                    try:
                        if heuristic_csv_copy(in_file, out_file, remove):
                            print("Copied possible csv: {}".format(in_file))
                            count_csv += 1
                            continue
                    except Exception as e2:
                        print("Error processing {}: {} (heuristic: {})".format(in_file, e, e2))
                        failed_xls += 1
            if lname.endswith(".db") or lname.endswith(".db3") or lname.endswith(".sqlite") or lname.endswith(
                    ".sqlite3"):
                print("Working on {}".format(in_file))
                try:
                    dump_database_to_spreadsheets(in_file)
                    count_sql += 1
                    if remove:
                        os.remove(in_file)
                except Exception as ex:
                    print("Failed to convert {}: {}".format(in_file, ex))
                    try:
                        folder, _ = os.path.splitext(in_file)
                        os.rmdir(folder)
                    except:
                        pass
                    failed_sql += 1

    print("Unpacked {} sql, {}[{}] xls files, {} existed, {} sql, {} xls failed. Total: {} files.".format(count_sql,
                                                                                                          count_xls,
                                                                                                          count_csv,
                                                                                                          existed,
                                                                                                          failed_sql,
                                                                                                          failed_xls,
                                                                                                          count))


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        print("Give me a path to massage. Add --remove if you want to remove all working specimen after successful unpacking.")
    else:
        remove = False
        if "--remove" in sys.argv:
            remove = True
            sys.argv.remove("--remove")
        recurse(sys.argv[1], remove)