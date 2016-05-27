#!/usr/local/bin/python
import sys, json, requests, subprocess, errno, re
from colorama import Fore, Back, Style
from subprocess import Popen, PIPE
#from giturlparse import parse


#----------------------------------------------------------------------------------------------------------------------
SHACOLW=7
EVENTCOLW=15
BRANCHCOLW=20
MSGCOLW=60
DFLTCOLW=10

HANDLEDEVENTS=["CreateEvent","DeleteEvent","PushEvent","CommitCommentEvent"]
#SKIPEVENTS=["ForkEvent","IssuesEvent","WatchEvent","IssueCommentEvent","PullRequestEvent","PullRequestReviewCommentEvent"]

#Function to print the output
def printIt( p, sha, type, repo, branch, login, message, filler):

	#clean up comments that have \n in them
	message = message.replace("\n"," ")

	#print Fore.RED+sha[:SHACOLW].ljust(SHACOLW," ")+Fore.RESET,type[:EVENTCOLW].ljust(EVENTCOLW,filler),repo[:DFLTCOLW].ljust(DFLTCOLW,filler),branch[:BRANCHCOLW].ljust(BRANCHCOLW,filler),Fore.BLUE+login.ljust(DFLTCOLW," ")+Fore.RESET,message.ljust(MSGCOLW," ")
	line = Fore.RED+sha[:SHACOLW].ljust(SHACOLW," ")+Fore.RESET
	line += " " + type[:EVENTCOLW].ljust(EVENTCOLW,filler)
	line += " " + repo[:DFLTCOLW].ljust(DFLTCOLW,filler)
	line += " " + branch[:BRANCHCOLW].ljust(BRANCHCOLW,filler)
	line += " " + Fore.BLUE+login.ljust(DFLTCOLW," ")+Fore.RESET
	line += " " + message.ljust(MSGCOLW," ")
	line += "\n"

	try:
		p.stdin.write(line)
	except:
		# Stop loop on "Invalid pipe" or "Invalid argument".
		# No sense in continuing with broken pipe.
		exit(1)

	return


#----------------------------------------------------------------------------------------------------------------------

#process arguments
gitRemote=subprocess.check_output(["git", "config", "--local", "remote.origin.url"])
urlAttributes = re.match('((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?', gitRemote)

#this code will handle parsing all git url formats, but we dont need that right now
#urlAttributes = parse(gitRemote)
#print(json.dumps(urlAttributes, indent=4))

if urlAttributes.groups()[0] == "git@github.com" :
	gitUser=urlAttributes.groups()[6].split('/')[0]
	gitRepo=urlAttributes.groups()[6].split('/')[1]
else:
	if urlAttributes.groups()[6].split('/')[0] == "github.com":
		gitUser=urlAttributes.groups()[6].split('/')[1]
		gitRepo=urlAttributes.groups()[6].split('/')[2]
	else:
		print urlAttributes.groups()
		print 'ERROR: Not a GITHUB repo, other remote repos not currently supported'
		exit(1)

if len(sys.argv) >=2:
	gitUser=sys.argv[1]
if len(sys.argv) == 3:
	gitRepo=sys.argv[2]
url="https://api.github.com/repos/" + gitUser + "/" + gitRepo + "/events?per_page=100"
response = requests.get(url, stream=True)

#open a pipe
p = Popen('less', stdin=PIPE)

#get the total # of pages from the header
try:
	numPages = int( response.headers["link"].split(",")[1].split("?")[1].split("&")[1].split("=")[1].split(">")[0])
except:
	numPages = 1

for i in range(1,numPages+1):
	printIt(p, "sha", "type", "repo", "branch", "login", "message", " ")

	if i > 1: 
		response = requests.get(url+'&page='+str(i), stream=True) 
		
	rows=json.loads(response.text)
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
				printIt(p, sha, type, repo, branch, login, message, " ")
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
				else:
					branch = ""
				printIt(p, sha, type, repo, branch, login, message," ")

				commits = payload.get("commits")
				if commits:
					for c in commits:
						if c:
							shaCommit = c["sha"][:SHACOLW]
							message = c["message"][:MSGCOLW]
							printIt(p, shaCommit,"", "", "", login,message,".")
				else:
					commits = ""
		else:
			sha = ""
			branch = ""
			printIt(p, sha, type, repo, branch, login, message," ")

#clean up the pipe
p.stdin.close()
p.wait()

exit(0)

