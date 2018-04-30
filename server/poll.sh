#!/bin/bash

sh ./build.sh >> build.html
while :
do
  git fetch > build_log.txt 2>&1
  if [ -s build_log.txt ]
  then
     echo "Changes detected, pulling... (overwriting all local changes)"
     git fetch --all
     git reset --hard origin/master

     echo "" > build.html
     echo "<html><body style='white-space: pre-wrap'><p style='font-family: monospace'>Build started at " >> build.html
     echo $(date) >> build.html
     echo ".\n" >> build.html

     sh ./build.sh >> build.html 2>&1

     echo "Build finished at "
     echo $(date) >> build.html
     echo ".\n" >> build.html
     echo "</p></body></html>" >> build.html

     echo "Build complete."
  fi
  sleep 5
done
