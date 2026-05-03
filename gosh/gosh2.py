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
import json
import os;
import os.path;
import shutil;
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
PROGRAM_BUILD     = 0;
PROGRAM_COPYRIGHT = "2015 - 2025";
PROGRAM_AUTHOR    = "mateus.digital";
PROGRAM_EMAIL     = "hello@mateus.digital";
PROGRAM_WEBSITE   = "http://mateus.digital";
PROGRAM_LICENSE   = "GPLv3";
##------------------------------------------------------------------------------
## Location of the paths file.
REPO_ROOT                 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."));
PACKAGE_JSON_PATH         = os.path.join(REPO_ROOT, "package.json");
SATURNO_PLATFORM_ROOT     = os.path.expanduser("~/.saturnosoftware");
SATURNO_HOME_DIR          = os.path.join(SATURNO_PLATFORM_ROOT, "gosh");
BOOKMARKS_BIN_DIR         = os.path.join(SATURNO_HOME_DIR, "bin");
BOOKMARKS_CONFIG_DIR      = os.path.join(SATURNO_HOME_DIR, "config");
BOOKMARKS_DATA_DIR        = os.path.join(SATURNO_HOME_DIR, "data");
BOOKMARKS_FILE_PATH       = os.path.join(BOOKMARKS_DATA_DIR, "gosh-paths.txt");
LEGACY_BOOKMARKS_FILE_DIR = os.path.expanduser("~/.mateusdigital/config/gosh");
LEGACY_BOOKMARKS_FILE_PATH = os.path.join(LEGACY_BOOKMARKS_FILE_DIR, "gosh-paths.txt");
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

##------------------------------------------------------------------------------
def ensure_bookmarks_storage():
    os.makedirs(BOOKMARKS_CONFIG_DIR, exist_ok=True);
    os.makedirs(BOOKMARKS_DATA_DIR, exist_ok=True);

    if(os.path.isfile(BOOKMARKS_FILE_PATH)):
        return;

    if(os.path.isfile(LEGACY_BOOKMARKS_FILE_PATH)):
        shutil.move(LEGACY_BOOKMARKS_FILE_PATH, BOOKMARKS_FILE_PATH);
        return;

    open(BOOKMARKS_FILE_PATH, "w").close(); ## @leak: don't care...


##------------------------------------------------------------------------------
def cli_path(path):
    return canonize_path(path);


##------------------------------------------------------------------------------
def load_cli_info():
    cli_info = {
        "Name"    : PROGRAM_NAME,
        "Version" : PROGRAM_VERSION,
        "Build"   : PROGRAM_BUILD,
        "Author"  : PROGRAM_AUTHOR,
        "Email"   : PROGRAM_EMAIL,
        "Website" : PROGRAM_WEBSITE,
        "License" : PROGRAM_LICENSE,
    };

    if os.path.isfile(PACKAGE_JSON_PATH):
        with open(PACKAGE_JSON_PATH, "r", encoding="utf-8") as package_file:
            package = json.load(package_file);

        if package.get("name"):
            cli_info["Name"] = str(package["name"]);
        if package.get("version"):
            cli_info["Version"] = str(package["version"]);
        if package.get("build") is not None:
            cli_info["Build"] = int(package["build"]);
        if package.get("license"):
            cli_info["License"] = str(package["license"]);

    return cli_info;


##------------------------------------------------------------------------------
def get_usage_text():
    cli_info = load_cli_info();

    return """Usage:
  {name}                   (Same as {name} -l)
  {name} <name>            (To change the directory)
  {name} -h | -v | -Json   (Show help | version | JSON metadata)
  {name} -l | -L           (Show list of bookmarks)
  {name} -p <name>         (Show path for bookmark)
  {name} -e <path>         (Show bookmark for path)
  {name} -a <name> <path>  (Add bookmark)
  {name} -u <name> <path>  (Update bookmark path)
  {name} -d <name>         (Delete the bookmark)

Options:
  *-h --help       : Show this screen.
  *-v --version    : Show app version and copyright.
  *-Json --json    : Print structured CLI metadata for help/version consumers.

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

  Options marked with * are exclusive, i.e. the {name} will run that
  and exit after the operation.
""".format(name=cli_info["Name"]);


##------------------------------------------------------------------------------
def get_version_text():
    cli_info = load_cli_info();

    return "\n".join([
        "{program_name} - {program_version}-{program_build} - {author} <{email}>",
        "Copyright (c) {program_copyright} - mateus.digital",
        "This is a free software ({license_name}) - Share/Hack it",
        "Check {website} for more :)"
    ]).format(
        program_name=cli_info["Name"],
        program_version=cli_info["Version"],
        program_build=cli_info["Build"],
        author=cli_info["Author"],
        email=cli_info["Email"],
        program_copyright=PROGRAM_COPYRIGHT,
        license_name=cli_info["License"],
        website=cli_info["Website"]
    );


##------------------------------------------------------------------------------
def get_cli_commands():
    return [
        { "Name": "jump", "Description": "Change the shell directory to the selected bookmark", "SupportsJsonOutput": False },
        { "Name": "list", "Description": "List bookmark names", "SupportsJsonOutput": False },
        { "Name": "list-long", "Description": "List bookmark names and paths", "SupportsJsonOutput": False },
        { "Name": "print", "Description": "Print the resolved path for one bookmark", "SupportsJsonOutput": False },
        { "Name": "exists", "Description": "Print the bookmark that matches one path", "SupportsJsonOutput": False },
        { "Name": "add", "Description": "Add a bookmark", "SupportsJsonOutput": False },
        { "Name": "update", "Description": "Update one bookmark path", "SupportsJsonOutput": False },
        { "Name": "delete", "Description": "Delete one bookmark", "SupportsJsonOutput": False },
        { "Name": "edit", "Description": "Open the bookmarks file in the default editor", "SupportsJsonOutput": False },
    ];


##------------------------------------------------------------------------------
def get_cli_metadata():
    cli_info = load_cli_info();
    usage_text = get_usage_text();
    version_text = get_version_text();

    return {
        "Schema"      : "saturno-cli-metadata/v1",
        "Name"        : cli_info["Name"],
        "Summary"     : "Saturno directory bookmark CLI with Python core and shell wrappers.",
        "Version"     : cli_info["Version"],
        "Build"       : cli_info["Build"],
        "Author"      : cli_info["Author"],
        "Email"       : cli_info["Email"],
        "Website"     : cli_info["Website"],
        "License"     : cli_info["License"],
        "UsageText"   : usage_text,
        "VersionText" : version_text,
        "Texts"       : {
            "Usage"   : usage_text,
            "Version" : version_text,
        },
        "OutputModes" : ["text", "json"],
        "Commands"    : get_cli_commands(),
        "Paths"       : {
            "PlatformRoot" : cli_path(SATURNO_PLATFORM_ROOT),
            "InstallRoot"  : cli_path(SATURNO_HOME_DIR),
            "BinDir"       : cli_path(BOOKMARKS_BIN_DIR),
            "ConfigRoot"   : cli_path(BOOKMARKS_CONFIG_DIR),
            "DataRoot"     : cli_path(BOOKMARKS_DATA_DIR),
            "DataFile"     : cli_path(BOOKMARKS_FILE_PATH),
        },
        "Supports"    : {
            "JsonMetadata" : True,
            "JsonCommands" : [],
            "JsonErrors"   : True,
            "ChangesDirectory" : True,
        }
    };


##------------------------------------------------------------------------------
def print_json_metadata():
    print(json.dumps(get_cli_metadata(), indent=2));


##------------------------------------------------------------------------------
def print_json_error(code, message, command=None):
    payload = {
        "Schema"  : "saturno-cli-error/v1",
        "Tool"    : load_cli_info()["Name"],
        "Command" : command,
        "Code"    : code,
        "Message" : message,
    };

    print(json.dumps(payload), file=sys.stderr);
    exit(1);


##------------------------------------------------------------------------------
def has_runtime_action(parsed_args):
    return (
        parsed_args.exists is not None
        or parsed_args.print is not None
        or parsed_args.list
        or parsed_args.list_long
        or parsed_args.add is not None
        or parsed_args.delete is not None
        or parsed_args.update is not None
        or parsed_args.edit_paths
        or len(parsed_args.values) != 0
    );


##----------------------------------------------------------------------------##
## Print Functions                                                            ##
##----------------------------------------------------------------------------##
##------------------------------------------------------------------------------
def print_fatal(msg):
    print("{0} {1}".format("[FATAL]", msg));
    exit(1);

##------------------------------------------------------------------------------
def print_help():
    print(get_usage_text());

##------------------------------------------------------------------------------
def print_version():
    print(get_version_text());



##----------------------------------------------------------------------------##
## Script                                                                     ##
##----------------------------------------------------------------------------##
##
## Parse the Command Line
parser = argparse.ArgumentParser(add_help=False);

parser.add_argument("-h", "--help"   ,       dest=None       ,            action="store_true");
parser.add_argument("-v", "--version",       dest=None       ,            action="store_true");
parser.add_argument("-Json", "--json",       dest="json"     ,            action="store_true");
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
if(args.json):
    if(args.help or args.version or not has_runtime_action(args)):
        print_json_metadata();
        exit(0);

    print_json_error("cli.json-metadata-only", "--json is currently only supported for root help/version metadata.");
elif(args.help):
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
ensure_bookmarks_storage();


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
