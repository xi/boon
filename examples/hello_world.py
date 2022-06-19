import boon


class Example(boon.App):
	def render(self, rows, cols):
		yield 'Hello World'

	def on_key(self, key):
		if key == 'q':
			self.running = False


example = Example()
example.run()
