#!/usr/bin/env python

import re

# Taken from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
_url_re = re.compile( r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?]))', re.MULTILINE )

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
	
	REPLACE_ESCAPE = (
		('<', '&lt;'),
		('>', '&gt;'),
		('&', '&amp;'),
	)
	
	REPLACE_COSMETIC = (
		('--', '&ndash;'),
		('---', '&mdash;'),
		('...', '&#8230;'),
		('(c)', '&copy;'),
		('(reg)', '&reg;'),
		('(tm)', '&trade;'),
	)
	
	def __init__( self, newline='<br />', normalize_newlines=True, install_defaults=True, escape=True, prettify=True, linkify=True ):
		self.newline = newline
		self.normalize_newlines = normalize_newlines
		self.recognized_tags = {}
		self.escape = escape
		self.prettify = prettify
		self.linkify = linkify
		if install_defaults:
			self.install_default_formatters()
	
	def add_formatter( self, tag_name, render_func, **kwargs ):
		"""
		Installs a render function for the specified tag name. The render function
		should have the following signature:
		
			def render( value, options, context, parent ):
				...
		
		The arguments are as follows:
			
			value
				The context between start and end tags, or None for standalone tags.
				Whether this has been rendered depends on render_embedded tag option.
			options
				A dictionary of options specified on the opening tag, or None.
			context
				The user-defined context value passed into the format call.
			parent
				The parent TagOptions, if the tag is being rendered inside another tag,
				otherwise None.
		"""
		options = TagOptions( tag_name.strip().lower(), **kwargs )
		self.recognized_tags[options.tag_name] = (render_func, options)
	
	def add_simple_formatter( self, tag_name, format, **kwargs ):
		def _render( value, options, context, parent ):
			fmt = {}
			if options:
				fmt.update( options )
			fmt.update( {'value': value} )
			return format % fmt
		self.add_formatter( tag_name, _render, **kwargs )
	
	def install_default_formatters( self ):
		self.add_simple_formatter( 'b', '<strong>%(value)s</strong>' )
		self.add_simple_formatter( 'i', '<em>%(value)s</em>' )
		self.add_simple_formatter( 'list', '<ul>%(value)s</ul>', transform_newlines=False )
		self.add_simple_formatter( '*', '<li>%(value)s</li>', newline_closes=True )
	
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
		if self.escape:
			for find, repl in self.REPLACE_ESCAPE:
				data = data.replace( find, repl )
		if self.prettify:
			for find, repl in self.REPLACE_COSMETIC:
				data = data.replace( find, repl )
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
						# This tag renders embedded tags, simply recurse.
						inner = self._format_tokens( subtokens, context, parent=tag )
					else:
						# Otherwise, just concatenate all the token text.
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

g_parser = None

def render_html( input, context=None ):
	"""
	A module-level convenience method that creates a default bbcode parser,
	and renders the input string as HTML.
	"""
	global g_parser
	if g_parser is None:
		g_parser = Parser()
	return g_parser.format( input, context )

if __name__ == '__main__':
	import sys
	print render_html( sys.stdin.read() )
