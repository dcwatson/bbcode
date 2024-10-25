Overview
========

**Latest Package**
http://pypi.python.org/pypi/bbcode

**Source Code**
https://github.com/dcwatson/bbcode

**Documentation**
https://dcwatson.github.io/bbcode/

[![CI Status](https://github.com/dcwatson/bbcode/workflows/CI/badge.svg)](https://github.com/dcwatson/bbcode/actions)


Installation
============

The easiest way to install the bbcode module is with pip, e.g.:

    pip install bbcode


Requirements
============

Python 3.9+


Basic Usage
===========

```python
# Using the default parser.
import bbcode
html = bbcode.render_html(text)

# Installing simple formatters.
parser = bbcode.Parser()
parser.add_simple_formatter('hr', '<hr />', standalone=True)
parser.add_simple_formatter('sub', '<sub>%(value)s</sub>')
parser.add_simple_formatter('sup', '<sup>%(value)s</sup>')

# A custom render function.
def render_color(tag_name, value, options, parent, context):
    return '<span style="color:%s;">%s</span>' % (tag_name, value)

# Installing advanced formatters.
for color in ('red', 'blue', 'green', 'yellow', 'black', 'white'):
    parser.add_formatter(color, render_color)

# Calling format with context.
html = parser.format(text, somevar='somevalue')
```
