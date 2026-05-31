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
##  Copyright : Saturno Software - 2026                                       ##
##                                                                            ##
##  Description :                                                             ##
##                                                                            ##
##----------------------------------------------------------------------------##

import os
import sys

##----------------------------------------------------------------------------##
## Constants                                                                  ##
##----------------------------------------------------------------------------##
_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT         = os.path.normpath(os.path.join(_DIR, ".."))
PACKAGE_JSON_PATH = os.path.join(REPO_ROOT, "package.json")

def _load_package_json():
    try:
        import json
        with open(PACKAGE_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}

_PKG = _load_package_json()

PROGRAM_NAME      = _PKG.get("name", "gosh")
PROGRAM_VERSION   = _PKG.get("version", "5.0.0")
PROGRAM_BUILD     = int(_PKG.get("build", 0))
PROGRAM_COPYRIGHT = "2026"
PROGRAM_AUTHOR    = "Saturno Software"
PROGRAM_EMAIL     = "hello@saturno.software"
PROGRAM_WEBSITE   = "https://saturno.software"
PROGRAM_LICENSE   = _PKG.get("license", "GPLv3")

BOOKMARK_SEPARATOR = ";"
SATURNO_PLATFORM_ROOT = os.path.join(os.path.expanduser("~"), ".saturnosoftware")
SATURNO_HOME_DIR      = os.path.join(SATURNO_PLATFORM_ROOT, "gosh")
BOOKMARKS_BIN_DIR     = os.path.join(SATURNO_HOME_DIR, "bin")
BOOKMARKS_CONFIG_DIR  = os.path.join(SATURNO_HOME_DIR, "config")
BOOKMARKS_DATA_DIR    = os.path.join(SATURNO_HOME_DIR, "data")
BOOKMARKS_FILE_PATH   = os.path.join(BOOKMARKS_DATA_DIR, "gosh-paths.txt")

SEQUENCE_MATCHER_MIN_RATIO = 0.6


##----------------------------------------------------------------------------##
## Fuzzy Matching                                                             ##
##----------------------------------------------------------------------------##
def fuzzy_score(name, query):
    if name == query:
        return 100000

    name_lower = name.lower()
    query_lower = query.lower()
    name_len = len(name)

    ## Case-insensitive exact
    if name_lower == query_lower:
        return 50000

    ## Prefix match (case-sensitive) - shorter name = better
    if name.startswith(query):
        return 45000 - name_len

    ## Substring match (case-sensitive)
    if query in name:
        return 40000 - name_len

    ## Case-insensitive prefix
    if name_lower.startswith(query_lower):
        return 35000 - name_len

    ## Case-insensitive substring
    if query_lower in name_lower:
        return 30000 - name_len

    ## Ordered character subsequence match
    qi = 0
    query_len = len(query_lower)
    for c in name_lower:
        if qi < query_len and c == query_lower[qi]:
            qi += 1
    if qi == query_len:
        return 10000 - name_len

    return 0

## -----------------------------------------------------------------------------
def find_best_fast_match(bookmarks, query):
    best_score = 0
    best_name = None

    for name in bookmarks:
        score = fuzzy_score(name, query)
        if score > best_score:
            best_score = score
            best_name = name
            if score >= 100000:
                break

    return best_name, best_score

## -----------------------------------------------------------------------------
def _split_name_parts(name):
    import re
    return [p for p in re.split(r"[.\-_/\\\s,;:]+", name) if p]

## -----------------------------------------------------------------------------
def find_best_sequencematcher_match(bookmarks, query):
    from difflib import SequenceMatcher

    best_ratio = 0
    best_name = None

    for name in bookmarks:
        ratio = SequenceMatcher(None, name, query).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_name = name

        parts = _split_name_parts(name)
        if len(parts) > 1:
            for part in parts:
                ratio = SequenceMatcher(None, part, query).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_name = name

        if best_ratio >= 1:
            break

    if best_ratio < SEQUENCE_MATCHER_MIN_RATIO:
        return None

    return best_name

## -----------------------------------------------------------------------------
def find_best_match(bookmarks, query):
    best_name, best_score = find_best_fast_match(bookmarks, query)

    if best_score > 0:
        return best_name

    return find_best_sequencematcher_match(bookmarks, query)




##----------------------------------------------------------------------------##
## Helpers                                                                    ##
##----------------------------------------------------------------------------##
def canonize_path(path):
    path = path.strip()
    path = os.path.normpath(os.path.normcase(os.path.abspath(os.path.expanduser(path))))
    return path.replace("\\", "/")


## -----------------------------------------------------------------------------
def ensure_bookmarks_storage():
    os.makedirs(BOOKMARKS_CONFIG_DIR, exist_ok=True)
    os.makedirs(BOOKMARKS_DATA_DIR, exist_ok=True)

    if os.path.isfile(BOOKMARKS_FILE_PATH):
        return

    open(BOOKMARKS_FILE_PATH, "w").close()


## -----------------------------------------------------------------------------
def load_bookmarks():
    bookmarks = {}
    with open(BOOKMARKS_FILE_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(BOOKMARK_SEPARATOR)
            if len(parts) < 2:
                continue
            name = parts[0].strip()
            path = parts[1].strip()
            count = 0
            if len(parts) >= 3:
                try:
                    count = int(parts[2])
                except:
                    pass
            bookmarks[name] = {"path": path, "count": count}
    return bookmarks

## -----------------------------------------------------------------------------
def save_bookmarks(bookmarks):
    lines = []
    for key in sorted(bookmarks):
        entry = bookmarks[key]
        lines.append("{0}{1}{2}{1}{3}\n".format(
            key, BOOKMARK_SEPARATOR, entry["path"], entry["count"]
        ))
    with open(BOOKMARKS_FILE_PATH, "w") as f:
        f.writelines(lines)

## -----------------------------------------------------------------------------
def cli_path(path):
    return canonize_path(path)

## -----------------------------------------------------------------------------
def load_cli_info():
    return {
        "Name"    : PROGRAM_NAME,
        "Version" : PROGRAM_VERSION,
        "Build"   : PROGRAM_BUILD,
        "Author"  : PROGRAM_AUTHOR,
        "Email"   : PROGRAM_EMAIL,
        "Website" : PROGRAM_WEBSITE,
        "License" : PROGRAM_LICENSE,
    }


## -----------------------------------------------------------------------------
def get_usage_text():
    cli_info = load_cli_info()
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
""".format(name=cli_info["Name"])


def get_version_text():
    cli_info = load_cli_info()
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
    )

## -----------------------------------------------------------------------------
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
    ]

## -----------------------------------------------------------------------------
def get_cli_metadata():
    cli_info = load_cli_info()
    usage_text = get_usage_text()
    version_text = get_version_text()

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
    }

## -----------------------------------------------------------------------------
def print_json_metadata():
    import json
    print(json.dumps(get_cli_metadata(), indent=2))


## -----------------------------------------------------------------------------
def print_json_error(code, message, command=None):
    import json
    payload = {
        "Schema"  : "saturno-cli-error/v1",
        "Tool"    : load_cli_info()["Name"],
        "Command" : command,
        "Code"    : code,
        "Message" : message,
    }
    print(json.dumps(payload), file=sys.stderr)
    exit(1)


## -----------------------------------------------------------------------------
def print_fatal(msg):
    print("[FATAL] " + msg)
    exit(1)


##----------------------------------------------------------------------------##
## Main                                                                       ##
##----------------------------------------------------------------------------##
def main():
    argv = sys.argv[1:]

    ## No args = help
    if not argv:
        print(get_usage_text())
        return

    ## Manual arg parsing - much faster than argparse
    cmd = argv[0]
    rest = argv[1:]

    ## Help / Version / Json / Edit — no bookmarks needed
    if cmd in ("-h", "--help"):
        print(get_usage_text())
        return
    if cmd in ("-v", "--version"):
        print(get_version_text())
        return
    if cmd in ("-Json", "--json"):
        ## --json with a runtime action is not supported
        if rest:
            print_json_error(
                "cli.json-metadata-only",
                "--json is currently only supported for root help/version metadata."
            )
        print_json_metadata()
        return
    if cmd in ("-E", "--edit"):
        print(BOOKMARKS_FILE_PATH)
        return

    ## Everything below needs bookmarks
    ensure_bookmarks_storage()
    bookmarks = load_bookmarks()

    ## List
    if cmd in ("-l", "--list"):
        if not bookmarks:
            print("No bookmarks yet... :/")
        else:
            for key in sorted(bookmarks):
                print(key)
        return

    ## List long
    if cmd in ("-L", "--list-long"):
        if not bookmarks:
            print("No bookmarks yet... :/")
        else:
            max_len = max(len(k) for k in bookmarks)
            for key in sorted(bookmarks):
                spaces = " " * (max_len - len(key))
                print("{0}{1} : {2}".format(key, spaces, bookmarks[key]["path"]))
        return

    ## Exists
    if cmd in ("-e", "--exists"):
        path = rest[0] if rest else "."
        clean_path = canonize_path(path)
        bookmark_name = None
        for name, entry in bookmarks.items():
            if entry["path"] == clean_path:
                bookmark_name = name
                break
        if bookmark_name is None:
            print("No bookmark")
        else:
            print("Bookmark: ({0})".format(bookmark_name))
        return

    ## Print
    if cmd in ("-p", "--print"):
        if not rest:
            print_fatal("Missing bookmark name for -p")
        name = rest[0]
        clean_name = find_best_match(bookmarks, name)
        if clean_name is None or clean_name not in bookmarks:
            print("Bookmark ({0}) doesn't exists.".format(name))
            exit(1)
        path = bookmarks[clean_name]["path"]
        clean_path = canonize_path(path)
        if not os.path.isdir(clean_path):
            print("Bookmark ({0}) exists but it's path is invalid ({1})".format(clean_name, clean_path))
        else:
            print(clean_path)
        bookmarks[clean_name]["count"] += 1
        save_bookmarks(bookmarks)
        return

    ## Add
    if cmd in ("-a", "--add"):
        name = rest[0] if len(rest) >= 1 else "."
        path = rest[1] if len(rest) >= 2 else "."
        clean_path = canonize_path(path)
        clean_name = name
        if name == "." and path == ".":
            clean_name = os.path.basename(clean_path)
        if clean_name in bookmarks:
            print_fatal("Bookmark ({0}) already exists.".format(clean_name))
        if not os.path.isdir(clean_path):
            print_fatal("Path ({0}) is not a valid directory.".format(clean_path))
        bookmarks[clean_name] = {"path": clean_path, "count": 0}
        save_bookmarks(bookmarks)
        print("Bookmark added:\n  ({0}) - ({1})".format(clean_name, clean_path))
        return

    ## Delete
    if cmd in ("-d", "--delete"):
        if not rest:
            print_fatal("Missing bookmark name for -d")
        name = rest[0]
        clean_name = find_best_match(bookmarks, name)
        if clean_name is None or clean_name not in bookmarks:
            print_fatal("Bookmark ({0}) doesn't exists.".format(name))
        del bookmarks[clean_name]
        save_bookmarks(bookmarks)
        print("Bookmark deleted:\n  ({0})".format(name))
        return

    ## Update
    if cmd in ("-u", "--update"):
        if len(rest) < 2:
            print_fatal("Usage: gosh -u <name> <path>")
        name = rest[0]
        path = rest[1]
        clean_name = find_best_match(bookmarks, name)
        clean_path = canonize_path(path)
        if clean_name is None or clean_name not in bookmarks:
            print_fatal("Bookmark ({0}) doesn't exists.".format(name))
        if not os.path.isdir(clean_path):
            print_fatal("Path ({0}) is not a valid directory.".format(clean_path))
        bookmarks[clean_name]["path"] = clean_path
        save_bookmarks(bookmarks)
        print("Bookmark updated:\n  ({0}) - ({1})".format(clean_name, clean_path))
        return

    ## Positional value = jump to bookmark
    query = cmd
    clean_name = find_best_match(bookmarks, query)
    if clean_name is None or clean_name not in bookmarks:
        print("Bookmark ({0}) doesn't exists.".format(query))
        exit(1)

    path = bookmarks[clean_name]["path"]
    clean_path = canonize_path(path)
    if not os.path.isdir(clean_path):
        print("Bookmark ({0}) exists but it's path is invalid ({1})".format(clean_name, clean_path))
    else:
        print(clean_path)

    bookmarks[clean_name]["count"] += 1
    save_bookmarks(bookmarks)


##
## Entry point ...
##

## -----------------------------------------------------------------------------
main()
