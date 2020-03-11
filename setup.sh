# Authored by SherlockOy 09/04/2019
#
#
# How to use?
#
# For Mac OS X uers only. Linux user may install xterm and use the script provided by the lecturer.
# Windows users, well, have a nice day.
# Paste this file to your working directory.
# Use Terminal or iTerm to go to your working directory.
#
# First step:
# run
#   $ chmod +x ./setup.sh
# to make it executable
# 
# Second step:
# run 
#   $ ./setup.sh
#
# 8 terminal windows will be set up with an interval of 1 second to launch your P2P application.
#
# You are free to improve this script, enjoy.


#!/bin/bash
current_path= "$PWD"
osascript - "$@" <<EOF
tell application "Terminal"
    activate
    set shell1 to do script "cd ${PWD}"  
    delay 1
    do script "python3 cdht.py 1 3 4 400 0.1" in shell1
    set custom title of shell1 to "Peer 1"

    set shell2 to do script "cd ${PWD}"  
    delay 1
    do script "python3 cdht.py 3 4 5 400 0.1" in shell2
    set custom title of shell2 to "Peer 3"

    set shell3 to do script "cd ${PWD}"  
    delay 1
    do script "python3 cdht.py 4 5 8 400 0.1" in shell3
    set custom title of shell3 to "Peer 4"
    
    set shell4 to do script "cd ${PWD}"  
    delay 1
    do script "python3 cdht.py 5 8 10 400 0.1" in shell4
    set custom title of shell4 to "Peer 5"

    set shell5 to do script "cd ${PWD}"  
    delay 1
    do script "python3 cdht.py 8 10 12 400 0.1" in shell5
    set custom title of shell5 to "Peer 8"

    set shell6 to do script "cd ${PWD}"  
    delay 1
    do script "python3 cdht.py 10 12 15 400 0.1" in shell6
    set custom title of shell6 to "Peer 10"

    set shell7 to do script "cd ${PWD}"  
    delay 1
    do script "python3 cdht.py 12 15 1 400 0.1" in shell7
    set custom title of shell7 to "Peer 12"

    set shell8 to do script "cd ${PWD}"  
    delay 1
    do script "python3 cdht.py 15 1 3 400 0.1" in shell8
    set custom title of shell8 to "Peer 15"

end tell
EOF
