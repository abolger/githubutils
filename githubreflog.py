#!/usr/local/bin/python
import sys, json
from colorama import Fore, Back, Style

SHACOLW=7
EVENTCOLW=15
BRANCHCOLW=20
MSGCOLW=60
DFLTCOLW=10

HANDLEDEVENTS=["CreateEvent","DeleteEvent","PushEvent","CommitCommentEvent"]
#SKIPEVENTS=["ForkEvent","IssuesEvent","WatchEvent","IssueCommentEvent","PullRequestEvent","PullRequestReviewCommentEvent"]

#Function to print the output
def printIt( sha, type, repo, branch, login, message, filler):

	#clean up comments that have \n in them
	message = message.replace("\n"," ")

	print Fore.RED+sha[:SHACOLW].ljust(SHACOLW," ")+Fore.RESET,type[:EVENTCOLW].ljust(EVENTCOLW,filler),repo[:DFLTCOLW].ljust(DFLTCOLW,filler),branch[:BRANCHCOLW].ljust(BRANCHCOLW,filler),Fore.BLUE+login.ljust(DFLTCOLW," ")+Fore.RESET,message.ljust(MSGCOLW," ")
	return

printIt("sha","type","repo","branch","login","message"," ")

rows=json.load(sys.stdin)
for r in rows: 
	type = r.get("type","")
	if type not in HANDLEDEVENTS: 
		continue

	repo = r.get("repo","").get("name","").split("/")[1][:DFLTCOLW]
	login = r["actor"]["login"][:DFLTCOLW]

	#set message to Date/Time for event lines
	message = r.get("created_at")

	payload = r.get("payload")
	if payload :
		#CommitCommentEvent has a different payload
		if type == "CommitCommentEvent":
			comment = payload.get("comment")
			sha = comment.get("commit_id")
			branch = ""
			printIt(sha, type, repo, branch, login, message, " ")
		else:
			#Enhance message for a Create Event to show the source branch
			if type == "CreateEvent":
				message = message + " " + payload.get("ref_type","") + ":"  + payload.get("master_branch","")
			sha = payload.get("head","")[:SHACOLW]
			branch = payload.get("ref")
			if branch:
				refsplit = branch.split("/")
				if len(refsplit) == 3:
					branch = refsplit[2]
			printIt(sha, type, repo, branch, login, message," ")

			commits = payload.get("commits")
			if commits:
				for c in commits:
					if c:
						shaCommit = c["sha"][:SHACOLW]
						message = c["message"][:MSGCOLW]
						printIt(shaCommit,"", "", "", login,message,".")
	else:
		sha = ""
		branch = ""
		printIt(sha, type, repo, branch, login, message," ")

exit(0)

