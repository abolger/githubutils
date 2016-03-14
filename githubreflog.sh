#!/bin/bash
GITUSER=${1:-capitalone}
GITREPO=${2:-hygieia}
URL="https://api.github.com/repos/${GITUSER}/$GITREPO/events?per_page=100"
NUMBER_PAGES=`curl -I "$URL" 2>/dev/null|egrep '^Link: '|awk -F'[,]' '{print $2}'|awk -F'[=&>]' '{print $4}'`

if [ "$NUMBER_PAGES" != "" ]
then
	for i in $(seq 1 $NUMBER_PAGES) 
	do 
		TMP_URL="${URL}&page=${i}"
		curl "$TMP_URL" 2>/dev/null|githubreflog.py
	done |less
fi
