#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import os
import re
import sys
import tempfile
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plura_dl.utils import PluraDLCookieJar


class TestPluraDLCookieJar(unittest.TestCase):
    def test_keep_session_cookies(self):
        cookiejar = PluraDLCookieJar('./test/testdata/cookies/session_cookies.txt')
        cookiejar.load(ignore_discard=True, ignore_expires=True)
        tf = tempfile.NamedTemporaryFile(delete=False)
        try:
            cookiejar.save(filename=tf.name, ignore_discard=True, ignore_expires=True)
            temp = tf.read().decode('utf-8')
            self.assertTrue(re.search(
                r'www\.foobar\.foobar\s+FALSE\s+/\s+TRUE\s+0\s+PluraDLExpiresEmpty\s+PluraDLExpiresEmptyValue', temp))
            self.assertTrue(re.search(
                r'www\.foobar\.foobar\s+FALSE\s+/\s+TRUE\s+0\s+PluraDLExpires0\s+PluraDLExpires0Value', temp))
        finally:
            tf.close()
            os.remove(tf.name)

    def test_strip_httponly_prefix(self):
        cookiejar = PluraDLCookieJar('./test/testdata/cookies/httponly_cookies.txt')
        cookiejar.load(ignore_discard=True, ignore_expires=True)

        def assert_cookie_has_value(key):
            self.assertEqual(cookiejar._cookies['www.foobar.foobar']['/'][key].value, key + '_VALUE')

        assert_cookie_has_value('HTTPONLY_COOKIE')
        assert_cookie_has_value('JS_ACCESSIBLE_COOKIE')


if __name__ == '__main__':
    unittest.main()
