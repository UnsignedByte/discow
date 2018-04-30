#!/bin/bash

logs=$(dirname "$(pwd)")/logs
echo $logs
echo "" > "$logs"/log.txt
echo "Build started at $(date).\n" >> "$logs"/log.txt

cd ..
python3 test.py & >> "$logs"/log.txt 2>&1
cd server

while :
do
  git fetch > "$logs"/build_log.txt 2>&1
  if [ -s build_log.txt ]
  then
     echo "Changes detected, pulling... (overwriting all local changes)"
     git fetch --all
     git reset --hard origin/master

     echo "" > "$logs"/build.html
     echo "<html><body style='white-space: pre-wrap'><p style='font-family: monospace'>Build started at " >> "$logs"/build.html
     echo $(date) >> "$logs"/build.html
     echo ".\n" >> "$logs"/build.html

     echo "Build started at $(date).\n" >> "$logs"/log.txt
     sh ./build.sh >> "$logs"/log.txt 2>&1

     echo "Build finished at "
     echo $(date) >> "$logs"/build.html
     echo ".\n" >> "$logs"/build.html
     echo "</p></body></html>" >> "$logs"/build.html

     echo "Build complete."
  fi
  sleep 5
done
