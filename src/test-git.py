import subprocess
import os
def is_tool_installed(name):
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
    return True

print(is_tool_installed("git"))
print(is_tool_installed("git-lfs"))
