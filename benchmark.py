#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cProfile
import datetime
import pstats
import random
import time

import bbcode

try:
    import StringIO
except ImportError:
    import io as StringIO


def word(length, allowed_chars='abcdefghijklmnopqrstuvwxyz'):
    return ''.join(random.choice(allowed_chars) for i in range(length))


def generate_lines(lines):
    fmt = '%d\t[%s]\t[%s]\t[%s]\t%s'
    for i in range(lines):
        level = word(random.randint(1, 10))
        module = word(random.randint(1, 10))
        sentence = ' '.join(word(random.randint(2, 7)) for i in range(10))
        yield fmt % (i, datetime.datetime.now().isoformat(), level, module, sentence)


if __name__ == '__main__':
    for num in (100, 1000, 10000):
        doc = '\n'.join(generate_lines(num))
        pr = cProfile.Profile()
        start = time.time()
        pr.enable()
        fmt = bbcode.render_html(doc)
        pr.disable()
        elapsed = time.time() - start
        print('%d lines: %.6fs (%.2f kB)' % (num, elapsed, len(doc) / 1024.0))
        s = StringIO.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print(s.getvalue())
