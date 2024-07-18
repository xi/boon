import sys

import boon


class Example(boon.App):
	def __init__(self):
		super().__init__()
		self.text = ''

	def render(self, rows, cols):
		yield self.text

	def on_key(self, key):
		self.text = repr(key)


example = Example()
example.run()
