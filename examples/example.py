import sys

import boon


class Example(boon.App):
	items = ['Foo', 'Bar', 'Baz']

	def __init__(self):
		super().__init__()
		self.selection = 0

	def render(self, rows, cols):
		for i in range((rows - 3) // 2):
			yield ''

		template = '{:^%i}' % cols
		for i, item in enumerate(self.items):
			centered = template.format(item)
			if i == self.selection:
				yield boon.get_cap('rev') + centered + boon.get_cap('sgr0')
			else:
				yield centered

	def on_key(self, key):
		if key == boon.KEY_UP:
			self.selection -= 1
		elif key == boon.KEY_DOWN:
			self.selection += 1
		elif key in ['q', '\n']:
			sys.exit(0)
		else:
			self.items.append(key)


example = Example()
example.run()
