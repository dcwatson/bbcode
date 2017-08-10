#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import bbcode
import sys

class ParserTests (unittest.TestCase):

    TESTS = (
        ('[B]hello world[/b]', '<strong>hello world</strong>'),
        ('[b][i]test[/i][/b]', '<strong><em>test</em></strong>'),
        ('[b][i]test[/b][/i]', '<strong><em>test</em></strong>'),
        ('[b]hello [i]world[/i]', '<strong>hello <em>world</em></strong>'),
        ('[tag][soup][/tag]', '[tag][soup][/tag]'),
        ('[b]hello [ world[/b]', '<strong>hello [ world</strong>'),
        ('[b]]he[llo [ w]orld[/b]', '<strong>]he[llo [ w]orld</strong>'),
        ('[b]hello [] world[/b]', '<strong>hello [] world</strong>'),
        ('[/asdf][/b]', '[/asdf]'),
        ('[list]\n[*]one\n[*]two\n[/list]', '<ul><li>one</li><li>two</li></ul>'),
        ('[list=1]\n[*]one\n[*]two\n[/list]', '<ol style="list-style-type:decimal;"><li>one</li><li>two</li></ol>'),
        ('[b\n oops [i]i[/i] forgot[/b]', '[b<br /> oops <em>i</em> forgot'),
        ('[b]over[i]lap[/b]ped[/i]', '<strong>over<em>lap</em></strong>ped'),
        ('>> hey -- a dash...', '&gt;&gt; hey &ndash; a dash&#8230;'),
        ('[url]http://foo.com/s.php?some--data[/url]', '<a href="http://foo.com/s.php?some--data">http://foo.com/s.php?some--data</a>'),
        ('[url=apple.com]link[/url]', '<a href="http://apple.com">link</a>'),
        ('www.apple.com blah foo.com/bar', '<a href="http://www.apple.com">www.apple.com</a> blah <a href="http://foo.com/bar">foo.com/bar</a>'),
        ('[color=red]hey now [url=apple.com]link[/url][/color]', '<span style="color:red;">hey now <a href="http://apple.com">link</a></span>'),
        ('[ b ] hello [u] world [/u] [ /b ]', '<strong> hello <u> world </u> </strong>'),
        ('[quote] \r\ntesting\nstrip [/quote]', '<blockquote>testing<br />strip</blockquote>'),
        ('[color red]this is red[/color]', '<span style="color:red;">this is red</span>'),
        ('[color]nothing[/color]', 'nothing'),
        ('[url="<script>alert(1);</script>"]xss[/url]', '<a href="&lt;script&gt;alert(1);&lt;/script&gt;">xss</a>'),
        ('[color=<script></script>]xss[/color]', '<span style="color:inherit;">xss</span>'),
        # Known issue: since HTML is escaped first, the trailing &gt is captured by the URL regex.
        # ('<http://foo.com/blah_blah>', '&lt;<a href="http://foo.com/blah_blah">http://foo.com/blah_blah</a>&gt;'),
        ('[COLOR=red]hello[/color]', '<span style="color:red;">hello</span>'),
        ('[URL=apple.com]link[/URL]', '<a href="http://apple.com">link</a>'),
        ('[list] [*]Entry 1 [*]Entry 2 [*]Entry 3   [/list]', '<ul><li>Entry 1</li><li>Entry 2</li><li>Entry 3</li></ul>'),
        ('[url=relative/url.html]link[/url]', '<a href="relative/url.html">link</a>'),
        ('[url=/absolute/url.html]link[/url]', '<a href="/absolute/url.html">link</a>'),
        ('[url=test.html]page[/url]', '<a href="test.html">page</a>'),
        # Tests to make sure links don't get cosmetic replacements.
        ('[url=http://test.com/my--page]test[/url]', '<a href="http://test.com/my--page">test</a>'),
        ('http://test.com/my...page(c)', '<a href="http://test.com/my...page(c)">http://test.com/my...page(c)</a>'),
        ('multiple http://apple.com/page link http://foo.com/foo--bar test', 'multiple <a href="http://apple.com/page">http://apple.com/page</a> link <a href="http://foo.com/foo--bar">http://foo.com/foo--bar</a> test'),
        ('[url=http://foo.com]<script>alert("XSS");</script>[/url]', '<a href="http://foo.com">&lt;script&gt;alert(&quot;XSS&quot;);&lt;/script&gt;</a>'),
        ('[url]123" onmouseover="alert(\'Hacked\');[/url]', '<a href="123&quot; onmouseover=&quot;alert(&#39;Hacked&#39;);">123&quot; onmouseover=&quot;alert(&#39;Hacked&#39;);</a>'),
        ('[code python]lambda code: [code] + [1, 2][/code]', '<code>lambda code: [code] + [1, 2]</code>'),
        ('[color="red; font-size:1000px;"]test[/color]', '<span style="color:red;">test</span>'),
        ('[color=#f4f4C3 barf]hi[/color]', '<span style="color:#f4f4C3;">hi</span>'),
        ('[list]\n[*]item with[code]some\ncode[/code] and text after[/list]', '<ul><li>item with<code>some\ncode</code> and text after</li></ul>'),
        ('x[sub]test[/sub]y', 'x<sub>test</sub>y'),
        ('x[sup]3[/sup] + 7', 'x<sup>3</sup> + 7'),
        ('line one[hr]line two', 'line one<hr />line two'),
        ('hello :[ world', 'hello :[ world'),
        ('[url]javascript:alert("XSS");[/url]', ''),
        ('[url]\x01javascript:alert(1)[/url]', ''),
        ('[url]javascript\x01:alert(1)[/url]', ''),
        ('[url]vbscript:alert(1)[/url]', ''),
        ('http://www.google.com"onmousemove="alert(\'XSS\');"', '<a href="http://www.google.com%22onmousemove=%22alert(\'XSS\')">http://www.google.com"onmousemove="alert(\'XSS\')</a>;&quot;'),
        ('[url=data:text/html;base64,PHNjcmlwdD5hbGVydCgiMSIpOzwvc2NyaXB0Pg==]xss[/url]', ''),
        ("[color='red']single[/color]", '<span style="color:red;">single</span>'),
        ('[quote author="name][clan"]blah[/quote]', '<blockquote>blah</blockquote>'),
        ('http://github.com/ http://example.org http://github.com/dcwatson/', '<a href="http://github.com/">http://github.com/</a> <a href="http://example.org">http://example.org</a> <a href="http://github.com/dcwatson/">http://github.com/dcwatson/</a>'),
        ('[b]Hello, [wor"ld][/b] out', '<strong>Hello, [wor&quot;ld]</strong> out'),
        ('[center]a\nb[code]c\nd[/code]\ne\nf\n', '<div style="text-align:center;">a<br />b<code>c\nd</code>e<br />f<br /></div>'),
        ('<a id="test">[b]test[/b]</a>', '&lt;a id=&quot;test&quot;&gt;<strong>test</strong>&lt;/a&gt;'),
    )

    URL_TESTS = """
        http://foo.com/blah_blah
        (Something like http://foo.com/blah_blah)
        http://foo.com/blah_blah_(wikipedia)
        http://foo.com/more_(than)_one_(parens)
        (Something like http://foo.com/blah_blah_(wikipedia))
        http://foo.com/blah_(wikipedia)#cite-1
        http://foo.com/blah_(wikipedia)_blah#cite-1
        http://foo.com/(something)?after=parens
        http://foo.com/blah_blah.
        http://foo.com/blah_blah/.
        <http://foo.com/blah_blah>
        <http://foo.com/blah_blah/>
        http://foo.com/blah_blah,
        http://www.extinguishedscholar.com/wpglob/?p=364.
        <tag>http://example.com</tag>
        Just a www.example.com link.
        http://example.com/something?with,commas,in,url, but not at end
        bit.ly/foo
        http://asdf.xxxx.yyyy.com/vvvvv/PublicPages/Login.aspx?ReturnUrl=%2fvvvvv%2f(asdf@qwertybean.com/qwertybean)
    """.strip()

    def setUp(self):
        self.parser = bbcode.Parser()

    def test_format(self):
        for src, expected in self.TESTS:
            result = self.parser.format(src)
            self.assertEqual(result, expected)

    def test_parse_opts(self):
        tag_name, opts = self.parser._parse_opts('url="http://test.com/s.php?a=bcd efg"  popup')
        self.assertEqual(tag_name, 'url')
        self.assertEqual(opts, {'url': 'http://test.com/s.php?a=bcd efg', 'popup': ''})
        tag_name, opts = self.parser._parse_opts('tag sep="=" flag=1')
        self.assertEqual(tag_name, 'tag')
        self.assertEqual(opts, {'sep': '=', 'flag': '1'})
        tag_name, opts = self.parser._parse_opts(' quote opt1 opt2 author = Watson, Dan   ')
        self.assertEqual(tag_name, 'quote')
        self.assertEqual(opts, {'author': 'Watson, Dan', 'opt1': '', 'opt2': ''})
        tag_name, opts = self.parser._parse_opts('quote = Watson, Dan')
        self.assertEqual(tag_name, 'quote')
        self.assertEqual(opts, {'quote': 'Watson, Dan'})
        tag_name, opts = self.parser._parse_opts("""Quote='Dan "Darsh" Watson'""")
        self.assertEqual(tag_name, 'quote')
        self.assertEqual(opts, {'quote': 'Dan "Darsh" Watson'})
        # combine single and double quotes in a value
        tag_name, opts = self.parser._parse_opts("quote='Lan \"Please Don\\\'t\" Rogers'")
        self.assertEqual(tag_name, 'quote')
        self.assertEqual(opts, {'quote': 'Lan "Please Don\'t" Rogers'})
        # Ensure backslash is still representable
        tag_name, opts = self.parser._parse_opts("""quote='\\\\"q\\\\"'""")
        self.assertEqual(tag_name, 'quote')
        self.assertEqual(opts, {'quote': '\\"q\\"'})
        # Make sure lookahead for unescaping doesn't go OOB
        tag_name, opts = self.parser._parse_opts("quote='\\")
        self.assertEqual(tag_name, 'quote')
        self.assertEqual(opts, {'quote': '\\'})
        tag_name, opts = self.parser._parse_opts("quote=Back\\Slash")
        self.assertEqual(tag_name, 'quote')
        self.assertEqual(opts, {'quote': 'Back\\Slash'})

    def test_strip(self):
        result = self.parser.strip('[b]hello \n[i]world[/i][/b] -- []', strip_newlines=True)
        self.assertEqual(result, 'hello world -- []')
        html_parser = bbcode.Parser(tag_opener='<', tag_closer='>', drop_unrecognized=True)
        result = html_parser.strip('<div class="test"><b>hello</b> <i>world</i><img src="test.jpg" /></div>')
        self.assertEqual(result, 'hello world')

    def test_linker(self):
        def _contextual_link(url, context):
            return '<a href="%s" target="_blank">%s</a>' % (url, context["substitution"])
        def _link(url):
            return _contextual_link(url, {"substitution": url})
        # Test noncontextual linker
        p = bbcode.Parser(linker=_link)
        s = p.format('hello www.apple.com world')
        self.assertEqual(s, 'hello <a href="www.apple.com" target="_blank">www.apple.com</a> world')
        # Test contextual linker
        p = bbcode.Parser(linker=_contextual_link, linker_takes_context=True)
        s = p.format('hello www.apple.com world', substitution="oh hai")
        self.assertEqual(s, 'hello <a href="www.apple.com" target="_blank">oh hai</a> world')

    def test_urls(self):
        for line in self.URL_TESTS.splitlines():
            num = len(bbcode._url_re.findall(line))
            self.assertEqual(num, 1, 'Found %d links in "%s"' % (num, line.strip()))

    def test_unicode(self):
        if sys.version_info >= (3,):
            src = '[center]ƒünk¥ • §tüƒƒ[/center]'
            dst = '<div style="text-align:center;">ƒünk¥ • §tüƒƒ</div>'
        else:
            src = unicode('[center]ƒünk¥ • §tüƒƒ[/center]', 'utf-8')
            dst = unicode('<div style="text-align:center;">ƒünk¥ • §tüƒƒ</div>', 'utf-8')
        self.assertEqual(self.parser.format(src), dst)

    def test_format_overrides(self):
        formatted = self.parser.format('<a id="test">[b]test[/b]</a>', escape_html=False)
        self.assertEqual(formatted, '<a id="test"><strong>test</strong></a>')
        formatted = self.parser.format('<a href="http://www.apple.com">Apple(c)</a>', escape_html=False, replace_links=False)
        self.assertEqual(formatted, '<a href="http://www.apple.com">Apple&copy;</a>')


if __name__ == '__main__':
    unittest.main()
