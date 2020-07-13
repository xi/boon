# boon - unix terminal framework

Boon is an alternative to curses. It occupies a similar level of abstraction
(somewhere between terminfo and your application), but uses different concepts.
It is just over 100loc and has no dependencies outside the standard library.

The high level API aims to be declarative and is partly inspired by react. The
lines of the terminal are represented as a list of strings. On each update,
this list is regenerated and compared to the previous version. Only the lines
that have changed are rendered to the terminal.

Boon does not provide utilities for color and styling. You can either use the
low level API or a third party library such as
[colorama](https://github.com/tartley/colorama/) or
[blessings](https://github.com/erikrose/blessings/).


## Example

```python
import boon

class Example(boon.App):
  def render(self, rows, cols):
    yield 'Hello World'

  def on_key(self, key):
    if key == 'q':
      self.running = False

example = Example()
example.run()
```


## High level API

### `App.run()`

Call to start the main loop.

### `App.running`

Set to `False` to stop the main loop.

### `App.render(rows, cols)`

Overwrite to define your view. For every line in the UI, this functions should
yield a string.

### `App.on_key(key)`

Overwrite to react to key presses. `key` is a string containing either a
character or an escape sequence. Boon contains constants for the most common
escape sequences:

- `KEY_BACKSPACE`
- `KEY_ESC`
- `KEY_HOME`
- `KEY_END`
- `KEY_PPAGE`
- `KEY_NPAGE`
- `KEY_UP`
- `KEY_DOWN`
- `KEY_RIGHT`
- `KEY_LEFT`

Note that boon reads all available input, so in rare occasions `key` might
contain more than one key. This should not be an issue in practice though.


## Low level API

### `get_cap(cap, *args) -> str`

Get a capability from the terminfo database. If stdout is not a tty or if the
capability is not supported by the terminal this returns an empty string. The
full list of capabilities is available in the [terminfo
manpage](http://manpages.ubuntu.com/manpages/man5/terminfo.5.html)

```python
print(get_cap('setaf', 13) + 'foo' + get_cap('sgr0'))
```

### `move(y, x)`

Move the cursor to the given position.

### `tty_restore(fd)`

Context manager that restores tty settings after the nested block.

```python
def getpass(prompt):
  fd = sys.stdin.fileno()
  with tty_restore(fd):
    flags = termios.tcgetattr(fd)
    flags[3] &= ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSADRAIN, flags)
    return input(prompt)
```

### `fullscreen()`

Context manager that enters cup and cbreak mode and also hides the cursor.
Everything is restored to the previous state after the nested block.

### `getch(timeout=0.5) -> string`

Reads from stdin. If no keys are available within the given timeout, `None` is
returned. See `App.on_key()` for details on the return value.
