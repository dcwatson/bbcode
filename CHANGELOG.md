### 1.1.0

* Now using a `CaseInsensitiveDict` to store tag options, so they retain the source case, but can be accessed case-insensitively.
* Dropped support for Python 2.6, tested against Python 3.8.
* Improved code coverage, formatted with black, and cleaned up Flake8 warnings.

---

### 1.0.33

* Added a `max_tag_depth` argument to the `Parser` class, defaulting to Python's recursion limit (Thanks, Lanny).

### 1.0.32

* List items `[*]` only render inside of `[list]` tags, to avoid producing invalid HTML.
* Switched to use `from __future__ import unicode_literals` so things like `url_template` can handle unicode replacements.
* Test on Python 3.7.

### 1.0.28

* Added a `default_context` argument to the `Parser` class.
* Added a `url_template` argument to the `Parser` class, allowing customization of the default linker (see #19 and #28).

### 1.0.27

* Set built-in `code` tag to `replace_cosmetic=False`.

### 1.0.26

* Allow overriding parser's `replace_html`, `replace_links`, and `replace_cosmetic` on `format` calls.

### 1.0.25

* Allow escaping quotes in tag options using backslash, i.e. `[quote='Sinéad O\'Connor']`.

### 1.0.11

* TagOptions now defaults to strip=False (see #7). list and quote tags have been set to strip=True, as they are typically block-level elements anyway.
* A new "drop_unrecognized" option was added to the Parser. If set to True, unrecognized tags will be dropped (the default is to render them as regular text).

### 1.0.10

* Small bugfix concerning render_embedded (see #6).

### 1.0.9

* Escape quotes correctly to prevent XSS (see #4).

### 1.0.8

* Fixed a bug where escaping and cosmetic replacements were incorrectly performed on URLs (f6e0c11).
