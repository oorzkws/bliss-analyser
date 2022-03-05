#!/usr/bin/env python3

#
# LMS-BlissMixer
#
# Copyright (c) 2022 Craig Drummond <craig.p.drummond@gmail.com>
# MIT license.
#

import datetime, os, requests, sys, time

GITHUB_TOKEN_FILE = "%s/.config/github-token" % os.path.expanduser('~')
GITHUB_REPO = "CDrummond/bliss-analyser"
GITHUB_ARTIFACTS = ["bliss-analyser-linux", "bliss-analyser-mac", "bliss-analyser-windows"]

def info(s):
    print("INFO: %s" %s)


def error(s):
    print("ERROR: %s" % s)
    exit(-1)


def usage():
    print("Usage: %s <major>.<minor>.<patch>" % sys.argv[0])
    exit(-1)


def to_time(tstr):
    return time.mktime(datetime.datetime.strptime(tstr, "%Y-%m-%dT%H:%M:%SZ").timetuple())


def get_items(repo, artifacts):
    info("Getting artifact list")
    js = requests.get("https://api.github.com/repos/%s/actions/artifacts" % repo).json()
    if js is None or not "artifacts" in js:
        error("Failed to list artifacts")

    items={}
    for a in js["artifacts"]:
        if a["name"] in artifacts and (not a["name"] in items or to_time(a["created_at"])>items[a["name"]]["date"]):
            items[a["name"]]={"date":to_time(a["created_at"]), "url":a["archive_download_url"]}

    return items


def download_artifacts(version):
    items = get_items(GITHUB_REPO, GITHUB_ARTIFACTS)
    if len(items)!=len(GITHUB_ARTIFACTS):
        error("Failed to determine all artifacts")
    token = None
    with open(GITHUB_TOKEN_FILE, "r") as f:
        token = f.readlines()[0].strip()
    headers = {"Authorization": "token %s" % token};

    for item in items:
        dest = "%s-%s.zip" % (item, version)
        info("Downloading %s" % item)
        r = requests.get(items[item]['url'], headers=headers, stream=True)
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024): 
                if chunk:
                    f.write(chunk)
        if not os.path.exists(dest):
            info("Failed to download %s" % item)
            break


def checkVersion(version):
    try:
        parts=version.split('.')
        major=int(parts[0])
        minor=int(parts[1])
        patch=int(parts[2])
    except:
        error("Invalid version number")


if 1==len(sys.argv):
    usage()

version=sys.argv[1]
if version!="test":
    checkVersion(version)

download_artifacts(version)
