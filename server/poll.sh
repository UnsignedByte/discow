#!/bin/bash


home=$(dirname "$(pwd)")
dat="$home"/Data
logs="$home"/logs
echo "Logging to $logs."
echo "" > "$logs"/log.txt
echo "Build started at $(date)." >> "$logs"/log.txt
echo "Running python " >> "$logs"/log.txt
python3.6 -V >> "$logs"/log.txt
echo "" >> "$logs"/log.txt

cd ..
python3.6 -u test.py >> "$logs"/log.txt 2>&1 &
pid=$!
cd server

control_c() {
    pkill -f test.py
    exit
}

trap control_c SIGINT

echo "" > "$logs"/build_log.txt

while :
do
  if ! kill -0 "$pid"; then
    echo "Server has crashed. Restarting..."  >> "$logs"/log.txt
    echo "Build started at $(date)." >> "$logs"/log.txt
    echo "Running python " >> "$logs"/log.txt
    python3.6 -V >> "$logs"/log.txt
    echo "" >> "$logs"/log.txt

    pkill -f test.py >> "$logs"/log.txt

    cd ..
    python3.6 -u test.py >> "$logs"/log.txt 2>&1 &
    pid=$!
    cd server
  fi
  blog=$(md5sum "$logs"/build_log.txt)
  git fetch >> "$logs"/build_log.txt 2>&1
  if [ $? -eq  0 ]; then
    newblog=$(md5sum "$logs"/build_log.txt)
    if [ "$blog" != "$newblog" ]
    then
       echo "Changes detected, pulling... (overwriting all local changes)"
       git fetch --all
       git reset --hard origin/master

       echo "" > "$logs"/build.html
       echo "<html><body style='white-space: pre-wrap'><p style='font-family: monospace'>Build started at " >> "$logs"/build.html
       echo $(date) >> "$logs"/build.html
       echo ".\n" >> "$logs"/build.html

       echo "Build started at $(date)." >> "$logs"/log.txt
       echo "Running python " >> "$logs"/log.txt
       python3.6 -V >> "$logs"/log.txt
       echo "" >> "$logs"/log.txt

       pkill -f test.py >> "$logs"/log.txt

       cd ..
       mv "$dat"/Backup/user_data.txt "$dat"/user_data.txt 
       python3.6 -u test.py >> "$logs"/log.txt 2>&1 &
       pid=$!
       cd server

       echo "Build finished at "
       echo $(date) >> "$logs"/build.html
       echo ".\n" >> "$logs"/build.html
       echo "</p></body></html>" >> "$logs"/build.html

       echo "Build complete."
    fi
  else
    echo "Attempted fetch with ERROR at $(date)" >> "$logs"/build_log.txt
  fi
  sleep 5
done
