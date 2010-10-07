#!/usr/bin/env python

TESTS = (
	('[b]hello world[/b]', '<strong>hello world</strong>'),
	('[b][i]test[/i][/b]', '<strong><em>test</em></strong>'),
	('[b][i]test[/b][/i]', '<strong><em>test</em></strong>'),
	('[b]hello [i]world[/i]', '<strong>hello <em>world</em></strong>'),
	('[tag][soup][/tag]', '[tag][soup][/tag]' ),
	('[b]hello [ world[/b]', '<strong>hello [ world</strong>' ),
	('[b]]he[llo [ w]orld[/b]', '<strong>]he[llo [ w]orld</strong>' ),
	('[b]hello [] world[/b]', '<strong>hello [] world</strong>' ),
	('[hr][/b]', '<hr />'),
	('[/asdf]', '[/asdf]'),
	('[list]\n[*]one\n[*]two\n[/list]', '<ul>\n<li>one</li><li>two</li></ul>'),
	('[b\n oops [i]i[/i] forgot[/b]', '[b<br /> oops <em>i</em> forgot' ),
	('[b]over[i]lap[/b]ped[/i]', '<strong>over<em>lap</em></strong>ped'),
	('[quote author=Dan]hey [b]now[/b][/quote]', '<blockquote>hey <strong>now</strong></blockquote>' ),
)

class TagOptions (object):
	
	tag_name = None
	newline_closes = False
	standalone = False
	render_embedded = True
	transform_newlines = True
	
	def __init__( self, tag_name, **kwargs ):
		self.tag_name = tag_name
		for attr, value in kwargs.items():
			setattr( self, attr, bool(value) )

class Parser (object):
	
	TOKEN_TAG_START = 1
	TOKEN_TAG_END = 2
	TOKEN_NEWLINE = 3
	TOKEN_DATA = 4
	
	def __init__( self, newline='<br />', normalize_newlines=True ):
		self.newline = newline
		self.normalize_newlines = normalize_newlines
		self.recognized_tags = {}
	
	def add_formatter( self, tag_name, render_func, **kwargs ):
		options = TagOptions( tag_name.strip().lower(), **kwargs )
		self.recognized_tags[options.tag_name] = (render_func, options)
	
	def _newline_tokenize( self, data ):
		"""
		Given a string that does not contain any tags, this function will
		return a list of NEWLINE and DATA tokens such that if you concatenate
		their data, you will have the original string.
		"""
		parts = data.split( '\n' )
		tokens = []
		for num, part in enumerate(parts):
			if part:
				tokens.append( (self.TOKEN_DATA, None, None, part) )
			if num < (len(parts) - 1):
				tokens.append( (self.TOKEN_NEWLINE, None, None, '\n') )
		return tokens
	
	def _parse_opts( self, data ):
		"""
		Given a tag string, this function will parse any options out of it and
		return a tuple of (tag_name, options_dict). Options may be quoted in order
		to preserve spaces, and free-standing options are allowed. The tag name
		itself may also serve as an option if it is immediately followed by an equal
		sign. Here are some examples:
			quote author="Dan Watson"
				tag_name=quote, options={'author': 'Dan Watson'}
			url="http://test.com/s.php?a=bcd efg" popup
				tag_name=url, options={'url': 'http://test.com/s.php?a=bcd efg', 'popup': ''}
		"""
		name = None
		opts = {}
		in_value = False
		in_quote = False
		attr = ''
		value = ''
		for pos, ch in enumerate(data):
			if in_value:
				if in_quote:
					if ch == '"':
						in_quote = False
					else:
						value += ch
				else:
					if ch == '"':
						in_quote = True
					elif ch == ' ':
						opts[attr] = value
						attr = ''
						value = ''
						in_value = False
					else:
						value += ch
			else:
				if ch == '=':
					in_value = True
					if name is None:
						name = attr
				elif ch == ' ':
					if name is None:
						name = attr
					elif attr:
						opts[attr] = ''
					attr = ''
				else:
					attr += ch
			if attr and pos == len(data) - 1:
				opts[attr] = value
		return name, opts
	
	def _parse_tag( self, tag ):
		"""
		Given a tag string (characters enclosed by []), this function will
		parse any options and return a tuple of the form:
			(valid, tag_name, closer, options)
		"""
		if (tag[0] != '[') or (tag[-1] != ']') or ('\n' in tag):
			return (False, tag, False, None)
		# TODO: should [b] == [ b ]?
		tag_name = tag[1:-1].strip()
		if not tag_name:
			return (False, tag, False, None)
		closer = False
		opts = None
		if tag_name[0] == '/':
			tag_name = tag_name[1:]
			closer = True
		# Parse options inside the opening tag, if needed.
		if (('=' in tag_name) or (' ' in tag_name)) and not closer:
			tag_name, opts = self._parse_opts( tag_name )
		return (True, tag_name.strip().lower(), closer, opts)
	
	def tokenize( self, data ):
		if self.normalize_newlines:
			data = data.replace( '\r\n', '\n' ).replace( '\r', '\n' )
		pos = 0
		start = 0
		end = 0
		tokens = []
		while pos < len(data):
			start = data.find( '[', pos )
			if start >= pos:
				# Check to see if there was data between this start and the last end.
				if start > pos:
					tl = self._newline_tokenize( data[pos:start] )
					tokens.extend( tl )
				end = data.find( ']', start )
				new_check = data.find( '[', start+1 )
				if new_check > 0 and new_check < end:
					tokens.extend( self._newline_tokenize(data[start:new_check]) )
					pos = new_check
				elif end > start:
					tag = data[start:end+1]
					valid, tag_name, closer, opts = self._parse_tag( tag )
					if valid and tag_name in self.recognized_tags:
						if closer:
							tokens.append( (self.TOKEN_TAG_END, tag_name, None, tag) )
						else:
							tokens.append( (self.TOKEN_TAG_START, tag_name, opts, tag) )
					else:
						tokens.extend( self._newline_tokenize(tag) )
					pos = end + 1
				else:
					# An unmatched [
					break
			else:
				# No more tags left to parse.
				break
		if pos < len(data):
			tl = self._newline_tokenize( data[pos:] )
			tokens.extend( tl )
		return tokens
	
	def _find_closing_token( self, tag, tokens, pos ):
		"""
		Given the current tag options, a list of tokens, and the current position
		in the token list, this function will find the position of the closing token
		associated with the specified tag. This may be a closing tag, a newline, or
		simply the end of the list (to ensure tags are closed).
		"""
		embed_count = 0
		while pos < len(tokens):
			token_type, tag_name, tag_opts, token_text = tokens[pos]
			if token_type == self.TOKEN_NEWLINE and tag.newline_closes:
				# If for some crazy reason there are embedded tags that both close on newline,
				# the first newline will automatically close all those nested tags.
				return pos
			elif token_type == self.TOKEN_TAG_START and tag_name == tag.tag_name:
				embed_count += 1
			elif token_type == self.TOKEN_TAG_END and tag_name == tag.tag_name:
				if embed_count > 0:
					embed_count -= 1
				else:
					return pos
			pos += 1
		return pos
	
	def _format_tokens( self, tokens, context, parent=None ):
		idx = 0
		formatted = ''
		while idx < len(tokens):
			token_type, tag_name, tag_opts, token_text = tokens[idx]
			if token_type == self.TOKEN_TAG_START:
				render_func, tag = self.recognized_tags[tag_name]
				if tag.standalone:
					formatted += render_func( None, tag_opts, context, parent )
				else:
					# First, find the extent of this tag's tokens
					end = self._find_closing_token( tag, tokens, idx+1 )
					subtokens = tokens[idx+1:end]
					if tag.render_embedded:
						inner = self._format_tokens( subtokens, context, parent=tag )
					else:
						if tag.transform_newlines:
							inner = ''.join( [t[3] if t[0] != self.TOKEN_NEWLINE else self.newline for t in subtokens] )
						else:
							inner = ''.join( [t[3] for t in subtokens] )
					formatted += render_func( inner, tag_opts, context, parent )
					idx = end
			elif token_type == self.TOKEN_NEWLINE:
				formatted += self.newline if (parent is None or parent.transform_newlines) else token_text
			elif token_type == self.TOKEN_DATA:
				formatted += token_text
			idx += 1
		return formatted
	
	def format( self, data, context=None ):
		tokens = self.tokenize( data )
		return self._format_tokens( tokens, context )

if __name__ == '__main__':
	p = Parser()
	p.add_formatter( 'b', lambda value, opts, c, p: '<strong>%s</strong>' % value )
	p.add_formatter( 'i', lambda value, opts, c, p: '<em>%s</em>' % value )
	p.add_formatter( 'issue', lambda value, opts, c, p: '<a href="/%s/">%s</a>' % (value, value) )
	p.add_formatter( 'quote', lambda value, opts, c, p: '<blockquote>%s</blockquote>' % value )
	p.add_formatter( 'code', lambda value, opts, c, p: '<code>%s</code>' % value, render_embedded=False, transform_newlines=False )
	p.add_formatter( 'hr', lambda value, opts, c, p: '<hr />', standalone=True )
	p.add_formatter( 'list', lambda value, opts, c, p: '<ul>%s</ul>' % value, transform_newlines=False )
	p.add_formatter( '*', lambda value, opts, c, p: '<li>%s</li>' % value, newline_closes=True )
#	print p._newline_tokenize( '\nhey\n \n\nnow\n\n\n' )
#	print p._parse_opts( 'quote author="Dan Watson"' )
#	print p._parse_opts( 'url="http://test.com/s.php?a=bcd efg" popup' )
#	s = 'hey there\nthis is [b]a test[/b]\n[issue prj=hello]12345[/issue] woop [quote author="Dan Watson"]hey now[/quote]'
#	print s
#	print p.tokenize( s )
#	print p.format( s )
#	print p.format( '[b]hey [i]there[/i][/b]' )
	for src, result in TESTS:
		val = p.format( src )
		if val != result:
			print 'FAIL: %s -> %s (expected %s)' % (src, val, result)
			print p.tokenize( src )
#	data = open('testfile','rb').read()
#	print p.format( data )
