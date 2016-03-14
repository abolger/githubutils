#!/bin/bash
#curl https://api.github.com/repos/capitalone/hygieia/events\?per_page\=100 2>/dev/null|python -c '
curl https://api.github.com/repos/jimzucker/hygieia/events\?per_page\=100 2>/dev/null|python -c '
import sys, json;
from colorama import Fore, Back, Style

SHACOLW=7
EVENTCOLW=15
BRANCHCOLW=20
MSGCOLW=60
DFLTCOLW=10

SKIPEVENTS=["ForkEvent","IssuesEvent","WatchEvent","IssueCommentEvent","PullRequestEvent","PullRequestReviewCommentEvent"]

def printIt( sha, type, repo, branch, login, message, filler):
	message = message.replace("\n"," ")
	print Fore.RED+sha[:SHACOLW].ljust(SHACOLW," ")+Fore.RESET,type[:EVENTCOLW].ljust(EVENTCOLW,filler),repo[:DFLTCOLW].ljust(DFLTCOLW,filler),branch[:BRANCHCOLW].ljust(BRANCHCOLW,filler),Fore.BLUE+login.ljust(DFLTCOLW," ")+Fore.RESET,message.ljust(MSGCOLW," ")
	return;

printIt("sha","type","repo","branch","login","message"," ")
rows=json.load(sys.stdin);
for r in rows: 
	type = r.get("type","")
	if type in SKIPEVENTS: 
		continue
	repo = r.get("repo","").get("name","").split("/")[1][:DFLTCOLW]
	login = r["actor"]["login"][:DFLTCOLW]
	message = r.get("created_at")
	payload = r.get("payload")
	if type == "CommitCommentEvent":
		comment = payload.get("comment")
		sha = comment.get("commit_id")
		branch = ""
		printIt(sha, type, repo, branch, login, message, " ")
	else:
		if payload :
			sha = payload.get("head","")[:SHACOLW]
			branch = payload.get("ref")
			if branch:
				refsplit = branch.split("/")
				if len(refsplit) == 3:
					branch = refsplit[2]
		else:
			sha = ""
			branch = ""
		printIt(sha, type, repo, branch, login, message," ")

		if payload:
			commits = payload.get("commits")
			if commits:
				for c in commits:
					if c:
						shaCommit = c["sha"][:SHACOLW]
						message = c["message"][:MSGCOLW]
						printIt(shaCommit,"", "", "", login,message,".")
'

