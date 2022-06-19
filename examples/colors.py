import boon

def print_colors(start, end):
	for i in range(start, end):
		print(boon.get_cap('setab', i) + '{:>4}'.format(i), end='')
	print(boon.get_cap('sgr0'))

print_colors(0, 8)
print_colors(8, 16)
for start in range(16, 232, 6):
	print_colors(start, start + 6)
print_colors(232, 256)
