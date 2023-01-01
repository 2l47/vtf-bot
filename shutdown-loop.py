#!/usr/bin/env python3

import os
import signal


with open("./state/loop.pid", "r") as f:
	loop_pid = int(f.read())

print(f"Sending SIGTERM to loop PID {loop_pid}")
os.kill(loop_pid, signal.SIGTERM)
os.remove("loop.pid")
