#!/usr/bin/env python3
##----------------------------------------------------------------------------##
##                               *       +                                    ##
##                         '                  |                               ##
##                     ()    .-.,="``"=.    - o -                             ##
##                           '=/_       \     |                               ##
##                        *   |  '=._    |                                    ##
##                             \     `=./`,        '                          ##
##                          .   '=.__.=' `='      *                           ##
##                 +                         +                                ##
##                      O      *        '       .                             ##
##                                                                            ##
##  File      : gosh2.py                                                      ##
##  Project   : gosh                                                          ##
##  Date      : Sep 28, 2015 - gosh-core.py                                   ##
##              Feb 25, 2022 - gosh2.py                                       ##
##  License   : See project's COPYING.TXT for full info.                      ##
##  Author    : mateus.digital <hello@mateus.digital>                         ##
##  Copyright : mateus.digital - 2015 - 2025                                  ##
##                                                                            ##
##  Description :                                                             ##
##                                                                            ##
##----------------------------------------------------------------------------##

##----------------------------------------------------------------------------##
## Imports                                                                    ##
##----------------------------------------------------------------------------##
import argparse
import os;
import os.path;
import sys;
import getopt;
import pdb;
import subprocess;
from difflib import SequenceMatcher as SM;


##----------------------------------------------------------------------------##
## Constants / Globals                                                        ##
##----------------------------------------------------------------------------##
##------------------------------------------------------------------------------
PROGRAM_NAME      = "gosh";
PROGRAM_VERSION   = "5.0.0";
PROGRAM_COPYRIGHT = "2015 - 2025";
##------------------------------------------------------------------------------
## Location of the paths file.
BOOKMARKS_FILE_DIR  = os.path.expanduser("~/.mateusdigital/config/gosh");
BOOKMARKS_FILE_PATH = os.path.join(BOOKMARKS_FILE_DIR, "gosh-paths.txt");
##------------------------------------------------------------------------------
## Some chars that are important to gosh.
## This char is used to pass the values back to gosh shell script.
OUTPUT_META_CHAR   = "#";
BOOKMARK_SEPARATOR = ";";

##----------------------------------------------------------------------------##
## Helper Functions                                                           ##
##----------------------------------------------------------------------------##
##------------------------------------------------------------------------------
def name_for_fuzzy_name(fuzzy_name):
    best_score = 0;
    best_name  = None;

    for k in bookmarks.keys():
        score = SM(None, k, fuzzy_name).ratio();
        if(score > best_score):
            best_name  = k;
            best_score = score;
        if(best_score == 1):
            return k;

    return best_name;

##------------------------------------------------------------------------------
def canonize_path(path):
    path = path.lstrip().rstrip();
    path = os.path.normpath(os.path.normcase(os.path.abspath(os.path.expanduser(path))));
    return path.replace("\\", "/");


##----------------------------------------------------------------------------##
## Print Functions                                                            ##
##----------------------------------------------------------------------------##
##------------------------------------------------------------------------------
def print_fatal(msg):
    print("{0} {1}".format("[FATAL]", msg));
    exit(1);

##------------------------------------------------------------------------------
def print_help():
    print("""Usage:
  gosh                   (Same as gosh -l)
  gosh <name>            (To change the directory)
  gosh -h | -v           (Show help | version)
  gosh -l | -L           (Show list of bookmarks)
  gosh -p <name>         (Show path for bookmark)
  gosh -e <path>         (Show bookmark for path)
  gosh -a <name> <path>  (Add bookmark)
  gosh -u <name> <path>  (Update bookmark path)
  gosh -d <name>         (Delete the bookmark)

Options:
  *-h --help     : Show this screen.
  *-v --version  : Show app version and copyright.

  *-e --exists <path>  : Print the Bookmark for path.
  *-p --print  <name>  : Print the path of Bookmark.

  *-l --list       : Show all Bookmarks (no Paths).
  *-L --list-long  : Show all Bookmarks and Paths.

  *-a --add    <name> <path>  : Add a Bookmark with specified path.
  *-u --update <name> <path>  : Update the path for a Bookmark.
  *-d --delete <name>         : Delete a Bookmark.

  *-E --edit                  : Open default editor to edit the bookmarks file.

Notes:
  If <path> is blank the current directory is assumed.

  Options marked with * are exclusive, i.e. the gosh will run that
  and exit after the operation.
""");

##------------------------------------------------------------------------------
def print_version():
    msg = "\n".join([
        "{program_name} - {program_version} - mateus.digital <hello@mateus.digital>",
        "Copyright (c) {program_copyright} - mateus.digital",
        "This is a free software (GPLv3) - Share/Hack it",
        "Check http://mateus.digital for more :)"]);

    msg = msg.format(
        program_name=PROGRAM_NAME,
        program_version=PROGRAM_VERSION,
        program_copyright=PROGRAM_COPYRIGHT
    );

    print(msg);



##----------------------------------------------------------------------------##
## Script                                                                     ##
##----------------------------------------------------------------------------##
##
## Parse the Command Line
parser = argparse.ArgumentParser(add_help=False);

parser.add_argument("-h", "--help"   ,       dest=None       ,            action="store_true");
parser.add_argument("-v", "--version",       dest=None       ,            action="store_true");
parser.add_argument("-e", "--exists" ,       dest="exists"   , nargs="*", action="store");
parser.add_argument("-p", "--print"  ,       dest="print"    , nargs=1  , action="store");
parser.add_argument("-l", "--list"   ,       dest=None       ,            action="store_true");
parser.add_argument("-L", "--list-long",     dest=None       ,            action="store_true");
parser.add_argument("-a", "--add"    ,       dest="add"      , nargs="*", action="store");
parser.add_argument("-d", "--delete" ,       dest="delete"   , nargs=1  , action="store");
parser.add_argument("-u", "--update" ,       dest="update"   , nargs=2  , action="store");
parser.add_argument("-E", "--edit"   ,       dest="edit_paths",           action="store_true");

parser.add_argument("values", nargs="*"); ## Positional Values
args = parser.parse_args();

##
## Help and Version doesn't need anything...
if(args.help):
    print_help();
    exit(0);
elif(args.version):
    print_version();
    exit(0);
elif(args.edit_paths):
    print(BOOKMARKS_FILE_PATH);
    exit(0);

##
##
bookmarks             = {} ## Name : Path dictionary
bookmarks_file        = None;
something_was_changed = False;


##
## This will ensure that the bookmarks file exists.
if(not os.path.isdir(BOOKMARKS_FILE_DIR)):
    os.makedirs(BOOKMARKS_FILE_DIR);
if(not os.path.isfile(BOOKMARKS_FILE_PATH)):
    open(BOOKMARKS_FILE_PATH, "w").close(); ## @leak: don't care...


##
## Open the filename and read all bookmarks that are in format of:
##    BookmarkName : BookmarkSeparator (Note that the ':' is the separator)
bookmark_lines = open(BOOKMARKS_FILE_PATH, "r").readlines(); ## @leak: don't care...
for line in bookmark_lines:
    clean_line = line.replace("\n", "").strip()
    if not clean_line:
        continue

    split = clean_line.split(BOOKMARK_SEPARATOR)

    if len(split) < 2:
        continue

    name = split[0].strip()
    path = split[1].strip()

    count = 0
    if len(split) >= 3:
        try:
            count = int(split[2])
        except:
            count = 0

    bookmarks[name] = {
        "path": path,
        "count": count
    }

##
## Exists
if(args.exists is not None):
    path       = args.exists[0] if len(args.exists) >= 1 else ".";
    clean_path = canonize_path(path);

    bookmark_name = None;
    for name in bookmarks.keys():
        bookmark_path = bookmarks[name]["path"];
        if(bookmark_path == clean_path):
            bookmark_name = name;
            break;

    if(bookmark_name is None):
        print("No bookmark");
    else:
        print("Bookmark: ({0})".format(bookmark_name));

##
## Print
elif(args.print is not None or len(args.values) != 0):
    name       = args.print[0] if(args.print is not None) else args.values[0];
    clean_name = name_for_fuzzy_name(name);

    if(clean_name not in bookmarks.keys()):
        print("Bookmark ({0}) doesn't exists.".format(clean_name));
        exit(1);

    ## Bookmark exists, check if path is valid.
    path       = bookmarks[clean_name]["path"];
    clean_path = canonize_path(path);

    if(not os.path.isdir(clean_path)):
        print("Bookmark ({0}) exists but it's path is invalid ({1})".format(
            clean_name, clean_path
        ));
    else:
        print(clean_path);

    bookmarks[clean_name]["count"] += 1;
    something_was_changed = True;

##
## List
elif(args.list or args.list_long):
    if(len(bookmarks) == 0):
        print("No bookmarks yet... :/");

    ## Get the greater bookmark's name length. It will
    ## be used to align all the bookmark's name.
    else:
        max_len = max(map(len, bookmarks.keys()));
        for key in sorted(bookmarks.keys()):
            spaces = " " * (max_len - len(key)); ## Put spaces to align the names.
            entry  = bookmarks[key];

            if(args.list_long):
                print("{0}{1} : {2}".format(key, spaces, entry["path"]))
            else:
                print(key);

##
## Delete
elif(args.delete is not None):
    name       = args.delete[0];
    clean_name = name_for_fuzzy_name(name);

    ## Check if we actually have a bookmark with this name.
    if(clean_name not in bookmarks.keys()):
        print_fatal("Bookmark ({0}) doesn't exists.".format(clean_name));

    ## Bookmark exists... Delete it and inform the user.
    del bookmarks[clean_name];
    something_was_changed = True;

    print("Bookmark deleted:\n  ({0})".format(name));

##
## Update
elif(args.update is not None):
    name       = args.update[0];
    path       = args.update[1];
    clean_name = name_for_fuzzy_name(name);
    clean_path = canonize_path(path);

    ## Check if we actually have a bookmark with this name.
    if(clean_name not in bookmarks.keys()):
        print_fatal("Bookmark ({0}) doesn't exists.".format(clean_name));

    ## Check if path is valid path.
    if(not os.path.isdir(clean_path)):
        print_fatal("Path ({0}) is not a valid directory.".format(clean_path));

    bookmarks[clean_name]["path"] = clean_path;
    something_was_changed = True;

    print("Bookmark updated:\n  ({0}) - ({1})".format(clean_name, clean_path));

##
## Add
##   args.add can be called without any argument, meaning that we want
##   to add the current path with the current base name as bookmark
##   so we need to compare it agaisnt None otherwise we can't capture
##   the case when we do gosh -a
elif(args.add is not None):
    name = ".";
    path = ".";
    if(len(args.add) >= 2):
        path = args.add[1];
    if(len(args.add) >= 1):
        name = args.add[0];

    ## Make the directory by the name if nothing was given.
    clean_path = canonize_path(path);
    clean_name = name;
    if(name == "." and path == "."):
        clean_name = os.path.basename(clean_path);

    ## Check if we have this bookmark, since we are adding we cannot have it.
    if(clean_name in bookmarks.keys()):
        print_fatal("Bookmark ({0}) already exists.".format(clean_name));

    ## Check if path is valid path.
    if(not os.path.isdir(clean_path)):
        print_fatal("Path ({0}) is not a valid directory.".format(clean_path));

    ## Name and Path are valid... Add it and inform the user.
    bookmarks[clean_name] = { "path": clean_path, "count": 0 };
    something_was_changed = True;

    print("Bookmark added:\n  ({0}) - ({1})".format(clean_name, clean_path));

##
## Save the bookmarks in disk. Sort them before just as convenience for
## who wants to mess with them in an editor.
bookmarks_str = "";
for key in sorted(bookmarks.keys()):
    entry = bookmarks[key]
    bookmarks_str += "{0}{1}{2}{1}{3}\n".format(
        key,
        BOOKMARK_SEPARATOR,
        entry["path"],
        entry["count"]
    )
bookmarks_file = open(BOOKMARKS_FILE_PATH, "w");
bookmarks_file.write(bookmarks_str);
bookmarks_file.close();
