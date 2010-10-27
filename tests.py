#!/usr/bin/env python

import unittest
import bbcode

class ParserTests (unittest.TestCase):
	
	TESTS = (
		('[b]hello world[/b]', '<strong>hello world</strong>'),
		('[b][i]test[/i][/b]', '<strong><em>test</em></strong>'),
		('[b][i]test[/b][/i]', '<strong><em>test</em></strong>'),
		('[b]hello [i]world[/i]', '<strong>hello <em>world</em></strong>'),
		('[tag][soup][/tag]', '[tag][soup][/tag]' ),
		('[b]hello [ world[/b]', '<strong>hello [ world</strong>' ),
		('[b]]he[llo [ w]orld[/b]', '<strong>]he[llo [ w]orld</strong>' ),
		('[b]hello [] world[/b]', '<strong>hello [] world</strong>' ),
		('[/asdf][/b]', '[/asdf]'),
		('[list]\n[*]one\n[*]two\n[/list]', '<ul><li>one</li><li>two</li></ul>'),
		('[b\n oops [i]i[/i] forgot[/b]', '[b<br /> oops <em>i</em> forgot' ),
		('[b]over[i]lap[/b]ped[/i]', '<strong>over<em>lap</em></strong>ped'),
		('>> hey -- a dash...', '&gt;&gt; hey &ndash; a dash&#8230;'),
		('[url]http://foo.com/s.php?some--data[/url]', '<a href="http://foo.com/s.php?some--data">http://foo.com/s.php?some--data</a>'),
		('[url=apple.com]link[/url]', '<a href="apple.com">link</a>'),
		('www.apple.com blah foo.com/bar', '<a href="www.apple.com">www.apple.com</a> blah <a href="foo.com/bar">foo.com/bar</a>'),
		('[color=red]hey now [url=apple.com]link[/url][/color]', '<span style="color:red;">hey now <a href="apple.com">link</a></span>'),
		('[ b ] hello [u] world [/u] [ /b ]', '<strong>hello <u>world</u></strong>'),
	)
	
	def setUp( self ):
		self.parser = bbcode.Parser()
	
	def test_format( self ):
		for src, expected in self.TESTS:
			result = self.parser.format( src )
			self.assertEqual( result, expected )
	
	def test_parse_opts( self ):
		tag_name, opts = self.parser._parse_opts( 'url="http://test.com/s.php?a=bcd efg"  popup' )
		self.assertEqual( tag_name, 'url' )
		self.assertEqual( opts, {'url': 'http://test.com/s.php?a=bcd efg', 'popup': ''} )
		tag_name, opts = self.parser._parse_opts( 'tag sep="=" flag=1' )
		self.assertEqual( tag_name, 'tag' )
		self.assertEqual( opts, {'sep': '=', 'flag': '1'} )
		tag_name, opts = self.parser._parse_opts( ' quote opt1 opt2 author = Watson, Dan   ' )
		self.assertEqual( tag_name, 'quote' )
		self.assertEqual( opts, {'author': 'Watson, Dan', 'opt1': '', 'opt2': ''} )
		tag_name, opts = self.parser._parse_opts( 'quote = Watson, Dan' )
		self.assertEqual( tag_name, 'quote' )
		self.assertEqual( opts, {'quote': 'Watson, Dan'} )
	
	def test_strip( self ):
		result = self.parser.strip( '[b]hello \n[i]world[/i][/b] -- []', strip_newlines=True )
		self.assertEqual( result, 'hello world -- []' )

if __name__ == '__main__':
	unittest.main()
