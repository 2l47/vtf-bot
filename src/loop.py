#!/usr/bin/env python3

import os
import sys
import time



# Is there an instance running already?
if os.path.exists("../state/loop.pid"):
	raise RuntimeError("An instance of loop.py is already running!")

# Write our PID to the file so we can kill the loop externally if necessary
with open("../state/loop.pid", "w") as f:
	f.write(str(os.getpid()))


print("Starting loop...")
while not os.path.exists("../state/want_shutdown"):
	# -B prevents python from writing bytecode
	os.system(f"python3 -B ./bot.py {' '.join(sys.argv[1:])}")
	time.sleep(0.5)

print("Loop ending.")
os.remove("../state/want_shutdown")
os.remove("../state/loop.pid")
