#!/usr/bin/env python3

import os
import signal


with open("./state/bot.pid", "r") as f:
	bot_pid = int(f.read())

print(f"Sending SIGTERM to bot PID {bot_pid}")
os.kill(bot_pid, signal.SIGTERM)
