#!/usr/bin/env bash


# Change this to be appropriate
cd ~/src/vtf-bot/src/

# Check if an instance is running
tmux list-sessions | grep vtf-bot

if [ $? -eq 1 ]; then
	# Nope, go ahead and clean up pid files
	rm ../state/bot.pid ../state/loop.pid 2>/dev/null
fi


echo -e "\n\nStarting under tmux..."

tmux new -d -s "vtf-bot" "./loop.py"

echo -e "\nDone.\n\n"
