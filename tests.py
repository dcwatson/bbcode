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
		('[list]\n[*]one\n[*]two\n[/list]', '<ul>\n<li>one</li><li>two</li></ul>'),
		('[b\n oops [i]i[/i] forgot[/b]', '[b<br /> oops <em>i</em> forgot' ),
		('[b]over[i]lap[/b]ped[/i]', '<strong>over<em>lap</em></strong>ped'),
	)
	
	def setUp( self ):
		self.parser = bbcode.Parser()
	
	def test_format( self ):
		for src, expected in self.TESTS:
			result = self.parser.format( src )
			self.assertEqual( result, expected )
	
	def test_parse_opts( self ):
		tag_name, opts = self.parser._parse_opts( 'url="http://test.com/s.php?a=bcd efg" popup' )
		self.assertEqual( tag_name, 'url' )
		self.assertEqual( opts, {'url': 'http://test.com/s.php?a=bcd efg', 'popup': ''} )

if __name__ == '__main__':
	unittest.main()
