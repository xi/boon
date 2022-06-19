import sys
import termios
from boon import tty_restore

def getpass(prompt):
	fd = sys.stdin.fileno()
	with tty_restore(fd):
		flags = termios.tcgetattr(fd)
		flags[3] &= ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSADRAIN, flags)
		return input(prompt)

print(getpass('Password: '))
