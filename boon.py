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

# FIXME: tigertstr uses \x1bO (SS3) instead of \x1b[ (CSI) as prefix
# https://en.wikipedia.org/wiki/ANSI_escape_code
KEY_BACKSPACE = curses.tigetstr('kbs')
KEY_ESC = b'\x1b'
KEY_HOME = curses.tigetstr('khome')
KEY_END = curses.tigetstr('kend')
KEY_INSERT = curses.tigetstr('kich1')
KEY_DELETE = curses.tigetstr('kdch1')
KEY_PPAGE = curses.tigetstr('kpp')
KEY_NPAGE = curses.tigetstr('knp')
KEY_UP = curses.tigetstr('kcuu1')
KEY_DOWN = curses.tigetstr('kcud1')
KEY_RIGHT = curses.tigetstr('kcuf1')
KEY_LEFT = curses.tigetstr('kcub1')


def getsize():
	# curses.tigetnum('cols') does not update on resize
	try:
		raw = ioctl(sys.stdout, termios.TIOCGWINSZ, '\000' * 8)
		parsed = struct.unpack('hhhh', raw)
		return parsed[1], parsed[0]
	except OSError:
		return 0, 0


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


@contextmanager
def termios_reset(fd):
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
		with termios_reset(fd):
			tty.setcbreak(fd)
			yield
	finally:
		sys.stdout.write(get_cap('rmcup'))
		sys.stdout.write(get_cap('cnorm'))
		sys.stdout.flush()


def getch():
	# NOTE: bytes might contain more than one key
	fd = sys.stdin.fileno()
	try:
		r, _w, _e = select.select([fd], [], [], 0.5)
	except select.error:
		return
	with termios_reset(fd):
		flags = termios.tcgetattr(fd)
		flags[6][termios.VMIN] = 0
		flags[6][termios.VTIME] = 0
		termios.tcsetattr(fd, termios.TCSADRAIN, flags)
		return os.read(fd, 8)


# https://github.com/tartley/colorama/blob/master/colorama/ansi.py
# def set_title(title):
# 	return OSC + '2;' + title + BEL


class App:
	def __init__(self):
		self.old_lines = []
		signal.signal(signal.SIGWINCH, self.on_resize)

	def update(self):
		lines = list(self.render())
		for i, line in enumerate(lines):
			if len(self.old_lines) > i and line == self.old_lines[i]:
				continue
			sys.stdout.write(get_cap('cup', i, 0))
			sys.stdout.write(get_cap('el'))
			sys.stdout.write(line)

		# clear rest of screen
		sys.stdout.write(get_cap('cup', len(lines), 0))
		sys.stdout.write(get_cap('ed'))
		sys.stdout.flush()

		self.old_lines = lines

	def on_resize(self, *args):
		self.cols, self.rows = getsize()
		self.update()

	def run(self):
		with fullscreen():
			self.on_resize()
			while True:
				key = getch()
				if key:
					self.on_key(key)
					self.update()

	def render(self):
		return []

	def on_key(self, key):
		pass


class Example(App):
	def __init__(self):
		super().__init__()
		self.keys = ['f', 'b', 'z']

	def on_key(self, key):
		if key == b'q':
			sys.exit(0)
		elif key == KEY_BACKSPACE:
			self.keys.pop()
		else:
			self.keys.append(key)

	def render(self):
		for key in self.keys:
			yield str(key) + 'test'


if __name__ == '__main__':
	example = Example()
	example.run()
