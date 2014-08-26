Basic Usage
===========

If you need only the :doc:`built-in tags <tags>`, you can simply use the global default parser::

    import bbcode
    html = bbcode.render_html(text)

Basic formatters can be added using simple string substitution. For instance, adding a [wiki] tag for wikipedia links may look like::

    parser = bbcode.Parser()
    parser.add_simple_formatter('wiki', '<a href="http://wikipedia.org/wiki/%(value)s">%(value)s</a>')



Custom Parser Objects
---------------------

The bbcode ``Parser`` class takes several options when creating:

newline (default: ``'<br />'``)
    What to replace newlines with.

normalize_newlines (default: ``True``)
    Whether to convert CR and CRLF to LF before replacements.

install_defaults (default: ``True``)
    Whether to install the default tag formatters. If False, you will need to specify add tag formatters yourself.

escape_html (default: ``True``)
    Whether to escape special HTML characters (<, >, &, ", and '). Replacements are specified as tuples in ``Parser.REPLACE_ESCAPE``.

replace_links (default: ``True``)
    Whether to automatically create HTML links for URLs in the source text.

replace_cosmetic (default: ``True``)
    Whether to perform cosmetic replacements for ---, --, ..., (c), (reg), and (tm). Replacements are specified as tuples in ``Parser.REPLACE_COSMETIC``.

tag_opener (default: ``'['``)
    The opening tag character(s).

tag_closer (default: ``']'``)
    The closing tag character(s).

linker (default: ``None`` (use the built-in link replacement))
    A function that takes a regular expression match object (and optionally the ``Parser`` context) and returns an HTML replacement string.

linker_takes_context (default: ``False``)
    Whether the linker function accepts a second ``context`` parameter. If ``True``, the linker function will be passed the context sent to ``Parser.format``.

drop_unrecognized (default: ``False``)
    Whether to drop unrecognized (but valid) tags. The default is to leave the tags, unformatted, in the output.


Customizing the Linker
----------------------

The linker is a function that gets called to replace URLs with markup. It takes one or two arguments (depending on whether you set ``linker_takes_context``), and might look like this::

    def my_linker(url):
        href = url
        if '://' not in href:
            href = 'http://' + href
        return '<a href="%s">%s</a>' % (href, url)

    parser = bbcode.Parser(linker=my_linker)
    parser.format('www.apple.com') # returns <a href="http://www.apple.com">www.apple.com</a>

For an example of a linker that may want the render context, imagine a linker that routes all clicks through a local URL::

    def my_linker(url, context):
        href = url
        if '://' not in href:
            href = 'http://' + href
        redir_url = context['request'].build_absolute_url('/redirect/') + '?to=' + urllib.quote(href, safe='/')
        return '<a href="%s">%s</a>' % (redir_url, url)

    parser = bbcode.Parser(linker=my_linker, linker_takes_context=True)
    parser.format('www.apple.com', request=request)
