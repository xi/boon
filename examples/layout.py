import textwrap
import boon

LOREM = """Aspernatur dolor quas explicabo adipisci. Velit possimus
eveniet odio quo quia. Earum quia vel officia et ea. Dolores quia et est
recusandae rem neque et. Magnam voluptates ut nulla commodi laboriosam
vitae.

Quod facilis nobis nihil blanditiis. Minima voluptatum alias ut rerum
numquam eos. Aspernatur dolorem omnis quae cumque fugiat reiciendis vel.
Deserunt necessitatibus sit at voluptates aut id omnis. Aspernatur odit
impedit delectus. Voluptatem ducimus totam repudiandae quisquam quis aut
fugiat.

In a est iste. Molestiae qui consequatur ut aspernatur alias temporibus
est delectus. A ut cum omnis eaque. Veritatis fugit rem vel."""


def fix_width(s, w):
	return '{0:{1}.{1}}'.format(s, w)


def columns(rows, cols, sep=''):
	cols = [(iter(i), w) for i, w in cols]
	for _ in range(rows):
		yield sep.join(fix_width(next(i, ''), w) for i, w in cols)


def box(s, rows, cols):
	lines = iter(textwrap.wrap(s, cols))
	c = cols - 2
	yield '+%s+' % ('-' * c)
	for _ in range(rows - 2):
		yield '|%s|' % fix_width(next(lines, ''), c)
	yield '+%s+' % ('-' * c)


def overlay(rows, bottom, top, y, x):
	bottom = iter(bottom)
	top = iter(top)
	for i in range(rows):
		if i < y:
			yield next(bottom, '')
		else:
			b = next(bottom, '')
			t = next(top, '')
			yield b[:x] + t + b[x + len(t):]


class Example(boon.App):
	def __init__(self):
		super().__init__()
		self.factor = 0.5

	def render(self, rows, cols):
		sep = ' | '
		left = int((cols - len(sep)) * self.factor)
		right = cols - len(sep) - left
		bottom = columns(rows, [
			(textwrap.wrap(LOREM, left), left),
			(textwrap.wrap(LOREM, right), right),
		], sep=sep)
		top = box(LOREM, rows // 2, cols // 2)
		return overlay(rows, bottom, top, rows // 4, cols // 4)

	def on_key(self, key):
		if key == 'q':
			self.running = False
		elif key == '>':
			self.factor += 0.1
		elif key == '<':
			self.factor -= 0.1


example = Example()
example.run()
