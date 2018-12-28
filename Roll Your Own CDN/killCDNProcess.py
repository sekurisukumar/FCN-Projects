import os, sys

os.system("kill $(ps aux | grep python | grep " + sys.argv[1]  + " | awk '{print $2}')")

