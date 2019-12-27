## Advanced Tag Formatters

[Simple formatters](index.md) are great for basic string substitution tags. But if you need to handle tag options, or
have access to the parser context or parent tag, you can write a formatter function that returns whatever HTML you like:

```python
# A custom render function that uses the tag name as a color style.
def render_color(tag_name, value, options, parent, context):
    return '<span style="color:%s;">%s</span>' % (tag_name, value)

# Installing advanced formatters.
for color in ('red', 'blue', 'green', 'yellow', 'black', 'white'):
    parser.add_formatter(color, render_color)
```


## Advanced Quote Example

Suppose you want to support an author option on your quote tags. Your formatting function might look something like
this:

```python
def render_quote(tag_name, value, options, parent, context):
    author = u''
    # [quote author=Somebody]
    if 'author' in options:
        author = options['author']
    # [quote=Somebody]
    elif 'quote' in options:
        author = options['quote']
    # [quote Somebody]
    elif len(options) == 1:
        key, val = list(options.items())[0]
        if val:
            author = val
        elif key:
            author = key
    # [quote Firstname Lastname]
    elif options:
        author = ' '.join([k for k in options.keys()])
    extra = '<small>%s</small>' % author if author else ''
    return '<blockquote><p>%s</p>%s</blockquote>' % (value, extra)

# Now register our new quote tag, telling it to strip off whitespace, and the newline after the [/quote].
parser.add_formatter('quote', render_quote, strip=True, swallow_trailing_newline=True)
```

## Custom Tag Options

When registering a formatter (simple or advanced), you may pass several keyword options for controlling the parsing and
rendering behavior.

* `newline_closes=False` - True if a newline should automatically close this tag.
* `same_tag_closes=False` - True if another start of the same tag should automatically close this tag.
* `standalone=False` - True if this tag does not have a closing tag.
* `render_embedded=True` - True if tags should be rendered inside this tag.
* `transform_newlines=True` - True if newlines should be converted to markup.
* `escape_html=True` - True if HTML characters (<, >, and &) should be escaped inside this tag.
* `replace_links=True` - True if URLs should be replaced with link markup inside this tag.
* `replace_cosmetic=True` - True if cosmetic replacements (elipses, dashes, etc.) should be performed inside this tag.
* `strip=False` - True if leading and trailing whitespace should be stripped inside this tag.
* `swallow_trailing_newline=False` - True if this tag should swallow the first trailing newline (i.e. for block
  elements).
