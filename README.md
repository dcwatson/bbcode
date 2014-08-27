Overview
========

| What           | Where           |
|:--------------:|:---------------:|
| Latest Package | http://pypi.python.org/pypi/bbcode |
| Source Code    | https://github.com/dcwatson/bbcode |
| Documentation  | http://bbcode.readthedocs.org/ |

[![Build Status](https://travis-ci.org/dcwatson/bbcode.svg?branch=master)](https://travis-ci.org/dcwatson/bbcode)


Installation
============

The easiest way to install the bbcode module is with pip, e.g.:

    pip install bbcode


Requirements
============

Python, tested with versions 2.6 through 3.4.


Basic Usage
===========

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


Advantages Over [Postmarkup](https://code.google.com/p/postmarkup/)
===================================================================

* More tag options for how/when to escape - for instance, you can specify
  whether to escape html or perform cosmetic replacements on a tag-by-tag
  basis. Same for auto-linking and transforming newlines.

* More liberal (and accurate) automatic link creation, using John Gruber's
  URL regular expression:
      http://daringfireball.net/2010/07/improved_regex_for_matching_urls

* Does not swallow unrecognized tags. For example, [3] will be output as
  [3], not silently ignored.

* More flexible tag option parser. Tags may have standard bbcode options,
  for example [url=something]text[/url], but may also have named options,
  for example [url=something alt=icon]text[/url]. These options are passed
  to the render function as a standard python dictionary.

* Ability to specify tag opening and closing delimiters (default: [ and ]).
  A side benefit of this is being able to use this library to selectively
  strip HTML tags from a string by using < and >.

* Includes a runnable unittest suite.

* Python 3 support.
