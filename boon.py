import os
import curses
import selectors
import shutil
import signal
import sys
import termios
import tty
from contextlib import contextmanager

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


def getch():
	# NOTE: result might contain more than one key
	fd = sys.stdin.fileno()
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
		self.timeout = 0.5
		self.selector = selectors.DefaultSelector()

		# self-pipe to avoid concurrency issues with signal
		self.resize_in, self.resize_out = os.pipe2(os.O_NONBLOCK)
		signal.signal(signal.SIGWINCH, self.on_resize)

	def update(self, force=False):
		lines = list(self.render(self.rows, self.cols))
		for i, line in enumerate(lines):
			if not force and len(self.old_lines) > i and line == self.old_lines[i]:
				continue
			move(i, 0)
			sys.stdout.write(get_cap('el'))
			sys.stdout.write(line)

		# clear rest of screen
		if len(lines) < self.rows:
			move(len(lines), 0)
			sys.stdout.write(get_cap('ed'))
		sys.stdout.flush()

		self.old_lines = lines

	def on_resize(self, *args):
		os.write(self.resize_out, b'.')

	def select(self, *fileobjs):
		with self.selector as sel:
			for fileobj in fileobjs:
				sel.register(fileobj, selectors.EVENT_READ)
			while self.running:
				yield from sel.select()

	def run(self):
		self.running = True
		with fullscreen():
			self.on_resize()
			for key, mask in self.select(self.resize_in):
				if key.fileobj is self.resize_in:
					os.read(self.resize_in, 8)
					self.cols, self.rows = shutil.get_terminal_size()
					self.update(force=True)
				else:
					if key.fileobj is sys.stdin:
						self.on_key(getch())
					elif callable(key.data):
						key.data()
					self.update()

	def render(self, rows, cols):
		return []

	def on_key(self, key):
		pass
