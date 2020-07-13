import os
import curses
import select
import signal
import struct
import sys
import termios
import tty
from contextlib import contextmanager
from fcntl import ioctl

curses.setupterm()

CSI = '\033['

# tigertstr uses \033O (SS3) instead of \033[ (CSI) as prefix
# https://en.wikipedia.org/wiki/ANSI_escape_code
KEY_BACKSPACE = curses.tigetstr('kbs').decode('ascii')
KEY_ESC = '\x1b'
KEY_HOME = CSI + 'H'
KEY_END = CSI + 'F'
KEY_PPAGE = CSI + '5~'
KEY_NPAGE = CSI + '6~'
KEY_UP = CSI + 'A'
KEY_DOWN = CSI + 'B'
KEY_RIGHT = CSI + 'C'
KEY_LEFT = CSI + 'D'


def isatty():
	return os.isatty(sys.stdout.fileno())


def get_cap(cap, *args):
	# see `man terminfo` for available capabilities
	if not isatty():
		return ''
	code = curses.tigetstr(cap)
	if not code:
		return ''
	if args:
		code = curses.tparm(code, *args)
	return code.decode('ascii')


def move(y, x):
	sys.stdout.write(get_cap('cup', y, x))


def get_size():
	# curses.tigetnum('cols') does not update on resize
	try:
		raw = ioctl(sys.stdout, termios.TIOCGWINSZ, '\000' * 8)
		parsed = struct.unpack('hhhh', raw)
		return parsed[0], parsed[1]
	except OSError:
		return 0, 0


@contextmanager
def tty_restore(fd):
	old = termios.tcgetattr(fd)
	try:
		yield
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old)


@contextmanager
def fullscreen():
	sys.stdout.write(get_cap('civis'))
	sys.stdout.write(get_cap('smcup'))
	sys.stdout.flush()
	try:
		fd = sys.stdin.fileno()
		with tty_restore(fd):
			tty.setcbreak(fd)
			yield
	finally:
		sys.stdout.write(get_cap('rmcup'))
		sys.stdout.write(get_cap('cnorm'))
		sys.stdout.flush()


def getch(timeout=0.5):
	# NOTE: result might contain more than one key
	fd = sys.stdin.fileno()
	try:
		r, _w, _e = select.select([fd], [], [], timeout)
	except select.error:
		return
	with tty_restore(fd):
		flags = termios.tcgetattr(fd)
		flags[6][termios.VMIN] = 0
		flags[6][termios.VTIME] = 0
		termios.tcsetattr(fd, termios.TCSADRAIN, flags)
		return sys.stdin.read(8)


class App:
	def __init__(self):
		self.old_lines = []
		self.running = False
		signal.signal(signal.SIGWINCH, self.on_resize)

	def update(self):
		lines = list(self.render())
		for i, line in enumerate(lines):
			if len(self.old_lines) > i and line == self.old_lines[i]:
				continue
			move(i, 0)
			sys.stdout.write(get_cap('el'))
			sys.stdout.write(line)

		# clear rest of screen
		move(len(lines), 0)
		sys.stdout.write(get_cap('ed'))
		sys.stdout.flush()

		self.old_lines = lines

	def on_resize(self, *args):
		self.rows, self.cols = get_size()
		self.update()

	def run(self):
		self.running = True
		with fullscreen():
			self.on_resize()
			while self.running:
				key = getch()
				if key:
					self.on_key(key)
					self.update()

	def render(self):
		return []

	def on_key(self, key):
		pass
