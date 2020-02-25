#!/usr/bin/env python
from __future__ import unicode_literals

import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import copy

from test.helper import FakePDL, assertRegexpMatches
from plura_dl import PluraDL
from plura_dl.compat import compat_str, compat_urllib_error
from plura_dl.extractor.common import InfoExtractor
from plura_dl.postprocessor.common import PostProcessor
from plura_dl.utils import ExtractorError, match_filter_func

TEST_URL = 'http://localhost/sample.mp4'


class PDL(FakePDL):
    def __init__(self, *args, **kwargs):
        super(PDL, self).__init__(*args, **kwargs)
        self.downloaded_info_dicts = []
        self.msgs = []

    def process_info(self, info_dict):
        self.downloaded_info_dicts.append(info_dict)

    def to_screen(self, msg):
        self.msgs.append(msg)


def _make_result(formats, **kwargs):
    res = {
        'formats': formats,
        'id': 'testid',
        'title': 'testttitle',
        'extractor': 'testex',
        'extractor_key': 'TestEx',
    }
    res.update(**kwargs)
    return res

class TestFormatSelection(unittest.TestCase):
    def test_prefer_free_formats(self):
        # Same resolution => download webm
        pdl = PDL()
        pdl.params['prefer_free_formats'] = True
        formats = [
            {'ext': 'webm', 'height': 460, 'url': TEST_URL},
            {'ext': 'mp4', 'height': 460, 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['ext'], 'mp4')

        pdl = PDL()
        pdl.params['prefer_free_formats'] = False
        formats = [
            {'ext': 'flv', 'height': 720, 'url': TEST_URL},
            {'ext': 'webm', 'height': 720, 'url': TEST_URL},
        ]
        info_dict['formats'] = formats
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['ext'], 'webm')

    def test_format_selection(self):
        formats = [
            {'format_id': '35', 'ext': 'mp4', 'preference': 1, 'url': TEST_URL},
            {'format_id': 'example-with-dashes', 'ext': 'webm', 'preference': 1, 'url': TEST_URL},
            {'format_id': '45', 'ext': 'webm', 'preference': 2, 'url': TEST_URL},
            {'format_id': '47', 'ext': 'webm', 'preference': 3, 'url': TEST_URL},
            {'format_id': '2', 'ext': 'flv', 'preference': 4, 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        pdl = PDL({'format': '20/47'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], '47')

        pdl = PDL({'format': '20/71/worst'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], '35')

        pdl = PDL()
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], '2')

        pdl = PDL({'format': 'webm/mp4'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], '47')

        pdl = PDL({'format': '3gp/40/mp4'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], '35')

        pdl = PDL({'format': 'example-with-dashes'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'example-with-dashes')

    def test_format_selection_audio(self):
        formats = [
            {'format_id': 'audio-low', 'ext': 'webm', 'preference': 1, 'vcodec': 'none', 'url': TEST_URL},
            {'format_id': 'audio-mid', 'ext': 'webm', 'preference': 2, 'vcodec': 'none', 'url': TEST_URL},
            {'format_id': 'audio-high', 'ext': 'flv', 'preference': 3, 'vcodec': 'none', 'url': TEST_URL},
            {'format_id': 'vid', 'ext': 'mp4', 'preference': 4, 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        pdl = PDL({'format': 'bestaudio'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'audio-high')

        pdl = PDL({'format': 'worstaudio'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'audio-low')

        formats = [
            {'format_id': 'vid-low', 'ext': 'mp4', 'preference': 1, 'url': TEST_URL},
            {'format_id': 'vid-high', 'ext': 'mp4', 'preference': 2, 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        pdl = PDL({'format': 'bestaudio/worstaudio/best'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'vid-high')

    def test_format_selection_video(self):
        formats = [
            {'format_id': 'dash-video-low', 'ext': 'mp4', 'preference': 1, 'acodec': 'none', 'url': TEST_URL},
            {'format_id': 'dash-video-high', 'ext': 'mp4', 'preference': 2, 'acodec': 'none', 'url': TEST_URL},
            {'format_id': 'vid', 'ext': 'mp4', 'preference': 3, 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        pdl = PDL({'format': 'bestvideo'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'dash-video-high')

        pdl = PDL({'format': 'worstvideo'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'dash-video-low')

        pdl = PDL({'format': 'bestvideo[format_id^=dash][format_id$=low]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'dash-video-low')

        formats = [
            {'format_id': 'vid-vcodec-dot', 'ext': 'mp4', 'preference': 1, 'vcodec': 'avc1.123456', 'acodec': 'none', 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        pdl = PDL({'format': 'bestvideo[vcodec=avc1.123456]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'vid-vcodec-dot')

    def test_format_selection_string_ops(self):
        formats = [
            {'format_id': 'abc-cba', 'ext': 'mp4', 'url': TEST_URL},
            {'format_id': 'zxc-cxz', 'ext': 'webm', 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        # equals (=)
        pdl = PDL({'format': '[format_id=abc-cba]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'abc-cba')

        # does not equal (!=)
        pdl = PDL({'format': '[format_id!=abc-cba]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'zxc-cxz')

        pdl = PDL({'format': '[format_id!=abc-cba][format_id!=zxc-cxz]'})
        self.assertRaises(ExtractorError, pdl.process_ie_result, info_dict.copy())

        # starts with (^=)
        pdl = PDL({'format': '[format_id^=abc]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'abc-cba')

        # does not start with (!^=)
        pdl = PDL({'format': '[format_id!^=abc]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'zxc-cxz')

        pdl = PDL({'format': '[format_id!^=abc][format_id!^=zxc]'})
        self.assertRaises(ExtractorError, pdl.process_ie_result, info_dict.copy())

        # ends with ($=)
        pdl = PDL({'format': '[format_id$=cba]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'abc-cba')

        # does not end with (!$=)
        pdl = PDL({'format': '[format_id!$=cba]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'zxc-cxz')

        pdl = PDL({'format': '[format_id!$=cba][format_id!$=cxz]'})
        self.assertRaises(ExtractorError, pdl.process_ie_result, info_dict.copy())

        # contains (*=)
        pdl = PDL({'format': '[format_id*=bc-cb]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'abc-cba')

        # does not contain (!*=)
        pdl = PDL({'format': '[format_id!*=bc-cb]'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'zxc-cxz')

        pdl = PDL({'format': '[format_id!*=abc][format_id!*=zxc]'})
        self.assertRaises(ExtractorError, pdl.process_ie_result, info_dict.copy())

        pdl = PDL({'format': '[format_id!*=-]'})
        self.assertRaises(ExtractorError, pdl.process_ie_result, info_dict.copy())

    def test_youtube_format_selection(self):
        order = [
            '38', '37', '46', '22', '45', '35', '44', '18', '34', '43', '6', '5', '17', '36', '13',
            # Apple HTTP Live Streaming
            '96', '95', '94', '93', '92', '132', '151',
            # 3D
            '85', '84', '102', '83', '101', '82', '100',
            # Dash video
            '137', '248', '136', '247', '135', '246',
            '245', '244', '134', '243', '133', '242', '160',
            # Dash audio
            '141', '172', '140', '171', '139',
        ]

    def test_audio_only_extractor_format_selection(self):
        # For extractors with incomplete formats (all formats are audio-only or
        # video-only) best and worst should fallback to corresponding best/worst
        # video-only or audio-only formats (as per
        # https://github.com/ytdl-org/plura-dl/pull/5556)
        formats = [
            {'format_id': 'low', 'ext': 'mp3', 'preference': 1, 'vcodec': 'none', 'url': TEST_URL},
            {'format_id': 'high', 'ext': 'mp3', 'preference': 2, 'vcodec': 'none', 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        pdl = PDL({'format': 'best'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'high')

        pdl = PDL({'format': 'worst'})
        pdl.process_ie_result(info_dict.copy())
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'low')

    def test_format_not_available(self):
        formats = [
            {'format_id': 'regular', 'ext': 'mp4', 'height': 360, 'url': TEST_URL},
            {'format_id': 'video', 'ext': 'mp4', 'height': 720, 'acodec': 'none', 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        # This must fail since complete video-audio format does not match filter
        # and extractor does not provide incomplete only formats (i.e. only
        # video-only or audio-only).
        pdl = PDL({'format': 'best[height>360]'})
        self.assertRaises(ExtractorError, pdl.process_ie_result, info_dict.copy())

    def test_format_selection_issue_10083(self):
        # See https://github.com/ytdl-org/youtube-dl/issues/10083
        formats = [
            {'format_id': 'regular', 'height': 360, 'url': TEST_URL},
            {'format_id': 'video', 'height': 720, 'acodec': 'none', 'url': TEST_URL},
            {'format_id': 'audio', 'vcodec': 'none', 'url': TEST_URL},
        ]
        info_dict = _make_result(formats)

        pdl = PDL({'format': 'best[height>360]/bestvideo[height>360]+bestaudio'})
        pdl.process_ie_result(info_dict.copy())
        self.assertEqual(pdl.downloaded_info_dicts[0]['format_id'], 'video+audio')

    def test_invalid_format_specs(self):
        def assert_syntax_error(format_spec):
            pdl = PDL({'format': format_spec})
            info_dict = _make_result([{'format_id': 'foo', 'url': TEST_URL}])
            self.assertRaises(SyntaxError, pdl.process_ie_result, info_dict)

        assert_syntax_error('bestvideo,,best')
        assert_syntax_error('+bestaudio')
        assert_syntax_error('bestvideo+')
        assert_syntax_error('/')

    def test_format_filtering(self):
        formats = [
            {'format_id': 'A', 'filesize': 500, 'width': 1000},
            {'format_id': 'B', 'filesize': 1000, 'width': 500},
            {'format_id': 'C', 'filesize': 1000, 'width': 400},
            {'format_id': 'D', 'filesize': 2000, 'width': 600},
            {'format_id': 'E', 'filesize': 3000},
            {'format_id': 'F'},
            {'format_id': 'G', 'filesize': 1000000},
        ]
        for f in formats:
            f['url'] = 'http://_/'
            f['ext'] = 'unknown'
        info_dict = _make_result(formats)

        pdl = PDL({'format': 'best[filesize<3000]'})
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'D')

        pdl = PDL({'format': 'best[filesize<=3000]'})
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'E')

        pdl = PDL({'format': 'best[filesize <= ? 3000]'})
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'F')

        pdl = PDL({'format': 'best [filesize = 1000] [width>450]'})
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'B')

        pdl = PDL({'format': 'best [filesize = 1000] [width!=450]'})
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'C')

        pdl = PDL({'format': '[filesize>?1]'})
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'G')

        pdl = PDL({'format': '[filesize<1M]'})
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'E')

        pdl = PDL({'format': '[filesize<1MiB]'})
        pdl.process_ie_result(info_dict)
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['format_id'], 'G')

        pdl = PDL({'format': 'all[width>=400][width<=600]'})
        pdl.process_ie_result(info_dict)
        downloaded_ids = [info['format_id'] for info in pdl.downloaded_info_dicts]
        self.assertEqual(downloaded_ids, ['B', 'C', 'D'])

        pdl = PDL({'format': 'best[height<40]'})
        try:
            pdl.process_ie_result(info_dict)
        except ExtractorError:
            pass
        self.assertEqual(pdl.downloaded_info_dicts, [])

    def test_default_format_spec(self):
        pdl = PDL({'simulate': True})
        self.assertEqual(pdl._default_format_spec({}), 'bestvideo+bestaudio/best')

        pdl = PDL({})
        self.assertEqual(pdl._default_format_spec({'is_live': True}), 'best/bestvideo+bestaudio')

        pdl = PDL({'simulate': True})
        self.assertEqual(pdl._default_format_spec({'is_live': True}), 'bestvideo+bestaudio/best')

        pdl = PDL({'outtmpl': '-'})
        self.assertEqual(pdl._default_format_spec({}), 'best/bestvideo+bestaudio')

        pdl = PDL({})
        self.assertEqual(pdl._default_format_spec({}, download=False), 'bestvideo+bestaudio/best')
        self.assertEqual(pdl._default_format_spec({'is_live': True}), 'best/bestvideo+bestaudio')


class TestPluraDL(unittest.TestCase):
    def test_subtitles(self):
        def s_formats(lang, autocaption=False):
            return [{
                'ext': ext,
                'url': 'http://localhost/video.%s.%s' % (lang, ext),
                '_auto': autocaption,
            } for ext in ['vtt', 'srt', 'ass']]
        subtitles = dict((l, s_formats(l)) for l in ['en', 'fr', 'es'])
        auto_captions = dict((l, s_formats(l, True)) for l in ['it', 'pt', 'es'])
        info_dict = {
            'id': 'test',
            'title': 'Test',
            'url': 'http://localhost/video.mp4',
            'subtitles': subtitles,
            'automatic_captions': auto_captions,
            'extractor': 'TEST',
        }

        def get_info(params={}):
            params.setdefault('simulate', True)
            pdl = PDL(params)
            pdl.report_warning = lambda *args, **kargs: None
            return pdl.process_video_result(info_dict, download=False)

        result = get_info()
        self.assertFalse(result.get('requested_subtitles'))
        self.assertEqual(result['subtitles'], subtitles)
        self.assertEqual(result['automatic_captions'], auto_captions)

        result = get_info({'writesubtitles': True})
        subs = result['requested_subtitles']
        self.assertTrue(subs)
        self.assertEqual(set(subs.keys()), set(['en']))
        self.assertTrue(subs['en'].get('data') is None)
        self.assertEqual(subs['en']['ext'], 'ass')

        result = get_info({'writesubtitles': True, 'subtitlesformat': 'foo/srt'})
        subs = result['requested_subtitles']
        self.assertEqual(subs['en']['ext'], 'srt')

        result = get_info({'writesubtitles': True, 'subtitleslangs': ['es', 'fr', 'it']})
        subs = result['requested_subtitles']
        self.assertTrue(subs)
        self.assertEqual(set(subs.keys()), set(['es', 'fr']))

        result = get_info({'writesubtitles': True, 'writeautomaticsub': True, 'subtitleslangs': ['es', 'pt']})
        subs = result['requested_subtitles']
        self.assertTrue(subs)
        self.assertEqual(set(subs.keys()), set(['es', 'pt']))
        self.assertFalse(subs['es']['_auto'])
        self.assertTrue(subs['pt']['_auto'])

        result = get_info({'writeautomaticsub': True, 'subtitleslangs': ['es', 'pt']})
        subs = result['requested_subtitles']
        self.assertTrue(subs)
        self.assertEqual(set(subs.keys()), set(['es', 'pt']))
        self.assertTrue(subs['es']['_auto'])
        self.assertTrue(subs['pt']['_auto'])

    def test_add_extra_info(self):
        test_dict = {
            'extractor': 'Foo',
        }
        extra_info = {
            'extractor': 'Bar',
            'playlist': 'funny videos',
        }
        PDL.add_extra_info(test_dict, extra_info)
        self.assertEqual(test_dict['extractor'], 'Foo')
        self.assertEqual(test_dict['playlist'], 'funny videos')

    def test_prepare_filename(self):
        info = {
            'id': '1234',
            'ext': 'mp4',
            'width': None,
            'height': 1080,
            'title1': '$PATH',
            'title2': '%PATH%',
        }

        def fname(templ):
            pdl = PluraDL({'outtmpl': templ})
            return pdl.prepare_filename(info)
        self.assertEqual(fname('%(id)s.%(ext)s'), '1234.mp4')
        self.assertEqual(fname('%(id)s-%(width)s.%(ext)s'), '1234-NA.mp4')
        # Replace missing fields with 'NA'
        self.assertEqual(fname('%(uploader_date)s-%(id)s.%(ext)s'), 'NA-1234.mp4')
        self.assertEqual(fname('%(height)d.%(ext)s'), '1080.mp4')
        self.assertEqual(fname('%(height)6d.%(ext)s'), '  1080.mp4')
        self.assertEqual(fname('%(height)-6d.%(ext)s'), '1080  .mp4')
        self.assertEqual(fname('%(height)06d.%(ext)s'), '001080.mp4')
        self.assertEqual(fname('%(height) 06d.%(ext)s'), ' 01080.mp4')
        self.assertEqual(fname('%(height)   06d.%(ext)s'), ' 01080.mp4')
        self.assertEqual(fname('%(height)0 6d.%(ext)s'), ' 01080.mp4')
        self.assertEqual(fname('%(height)0   6d.%(ext)s'), ' 01080.mp4')
        self.assertEqual(fname('%(height)   0   6d.%(ext)s'), ' 01080.mp4')
        self.assertEqual(fname('%%'), '%')
        self.assertEqual(fname('%%%%'), '%%')
        self.assertEqual(fname('%%(height)06d.%(ext)s'), '%(height)06d.mp4')
        self.assertEqual(fname('%(width)06d.%(ext)s'), 'NA.mp4')
        self.assertEqual(fname('%(width)06d.%%(ext)s'), 'NA.%(ext)s')
        self.assertEqual(fname('%%(width)06d.%(ext)s'), '%(width)06d.mp4')
        self.assertEqual(fname('Hello %(title1)s'), 'Hello $PATH')
        self.assertEqual(fname('Hello %(title2)s'), 'Hello %PATH%')

    def test_format_note(self):
        pdl = PluraDL()
        self.assertEqual(pdl._format_note({}), '')
        assertRegexpMatches(self, pdl._format_note({
            'vbr': 10,
        }), r'^\s*10k$')
        assertRegexpMatches(self, pdl._format_note({
            'fps': 30,
        }), r'^30fps$')

    def test_postprocessors(self):
        filename = 'post-processor-testfile.mp4'
        audiofile = filename + '.mp3'

        class SimplePP(PostProcessor):
            def run(self, info):
                with open(audiofile, 'wt') as f:
                    f.write('EXAMPLE')
                return [info['filepath']], info

        def run_pp(params, PP):
            with open(filename, 'wt') as f:
                f.write('EXAMPLE')
            pdl = PluraDL(params)
            pdl.add_post_processor(PP())
            pdl.post_process(filename, {'filepath': filename})

        run_pp({'keepvideo': True}, SimplePP)
        self.assertTrue(os.path.exists(filename), '%s doesn\'t exist' % filename)
        self.assertTrue(os.path.exists(audiofile), '%s doesn\'t exist' % audiofile)
        os.unlink(filename)
        os.unlink(audiofile)

        run_pp({'keepvideo': False}, SimplePP)
        self.assertFalse(os.path.exists(filename), '%s exists' % filename)
        self.assertTrue(os.path.exists(audiofile), '%s doesn\'t exist' % audiofile)
        os.unlink(audiofile)

        class ModifierPP(PostProcessor):
            def run(self, info):
                with open(info['filepath'], 'wt') as f:
                    f.write('MODIFIED')
                return [], info

        run_pp({'keepvideo': False}, ModifierPP)
        self.assertTrue(os.path.exists(filename), '%s doesn\'t exist' % filename)
        os.unlink(filename)

    def test_match_filter(self):
        class FilterPDL(PDL):
            def __init__(self, *args, **kwargs):
                super(FilterPDL, self).__init__(*args, **kwargs)
                self.params['simulate'] = True

            def process_info(self, info_dict):
                super(PDL, self).process_info(info_dict)

            def _match_entry(self, info_dict, incomplete):
                res = super(FilterPDL, self)._match_entry(info_dict, incomplete)
                if res is None:
                    self.downloaded_info_dicts.append(info_dict)
                return res

        first = {
            'id': '1',
            'url': TEST_URL,
            'title': 'one',
            'extractor': 'TEST',
            'duration': 30,
            'filesize': 10 * 1024,
            'playlist_id': '42',
            'uploader': "變態妍字幕版 太妍 тест",
            'creator': "тест ' 123 ' тест--",
        }
        second = {
            'id': '2',
            'url': TEST_URL,
            'title': 'two',
            'extractor': 'TEST',
            'duration': 10,
            'description': 'foo',
            'filesize': 5 * 1024,
            'playlist_id': '43',
            'uploader': "тест 123",
        }
        videos = [first, second]

        def get_videos(filter_=None):
            pdl = FilterPDL({'match_filter': filter_})
            for v in videos:
                pdl.process_ie_result(v, download=True)
            return [v['id'] for v in pdl.downloaded_info_dicts]

        res = get_videos()
        self.assertEqual(res, ['1', '2'])

        def f(v):
            if v['id'] == '1':
                return None
            else:
                return 'Video id is not 1'
        res = get_videos(f)
        self.assertEqual(res, ['1'])

        f = match_filter_func('duration < 30')
        res = get_videos(f)
        self.assertEqual(res, ['2'])

        f = match_filter_func('description = foo')
        res = get_videos(f)
        self.assertEqual(res, ['2'])

        f = match_filter_func('description =? foo')
        res = get_videos(f)
        self.assertEqual(res, ['1', '2'])

        f = match_filter_func('filesize > 5KiB')
        res = get_videos(f)
        self.assertEqual(res, ['1'])

        f = match_filter_func('playlist_id = 42')
        res = get_videos(f)
        self.assertEqual(res, ['1'])

        f = match_filter_func('uploader = "變態妍字幕版 太妍 тест"')
        res = get_videos(f)
        self.assertEqual(res, ['1'])

        f = match_filter_func('uploader != "變態妍字幕版 太妍 тест"')
        res = get_videos(f)
        self.assertEqual(res, ['2'])

        f = match_filter_func('creator = "тест \' 123 \' тест--"')
        res = get_videos(f)
        self.assertEqual(res, ['1'])

        f = match_filter_func("creator = 'тест \\' 123 \\' тест--'")
        res = get_videos(f)
        self.assertEqual(res, ['1'])

        f = match_filter_func(r"creator = 'тест \' 123 \' тест--' & duration > 30")
        res = get_videos(f)
        self.assertEqual(res, [])

    def test_playlist_items_selection(self):
        entries = [{
            'id': compat_str(i),
            'title': compat_str(i),
            'url': TEST_URL,
        } for i in range(1, 5)]
        playlist = {
            '_type': 'playlist',
            'id': 'test',
            'entries': entries,
            'extractor': 'test:playlist',
            'extractor_key': 'test:playlist',
            'webpage_url': 'http://example.com',
        }

        def get_downloaded_info_dicts(params):
            pdl = PDL(params)
            # make a deep copy because the dictionary and nested entries
            # can be modified
            pdl.process_ie_result(copy.deepcopy(playlist))
            return pdl.downloaded_info_dicts

        def get_ids(params):
            return [int(v['id']) for v in get_downloaded_info_dicts(params)]

        result = get_ids({})
        self.assertEqual(result, [1, 2, 3, 4])

        result = get_ids({'playlistend': 10})
        self.assertEqual(result, [1, 2, 3, 4])

        result = get_ids({'playlistend': 2})
        self.assertEqual(result, [1, 2])

        result = get_ids({'playliststart': 10})
        self.assertEqual(result, [])

        result = get_ids({'playliststart': 2})
        self.assertEqual(result, [2, 3, 4])

        result = get_ids({'playlist_items': '2-4'})
        self.assertEqual(result, [2, 3, 4])

        result = get_ids({'playlist_items': '2,4'})
        self.assertEqual(result, [2, 4])

        result = get_ids({'playlist_items': '10'})
        self.assertEqual(result, [])

        result = get_ids({'playlist_items': '3-10'})
        self.assertEqual(result, [3, 4])

        result = get_ids({'playlist_items': '2-4,3-4,3'})
        self.assertEqual(result, [2, 3, 4])

        # Tests for https://github.com/ytdl-org/youtube-dl/issues/10591
        # @{
        result = get_downloaded_info_dicts({'playlist_items': '2-4,3-4,3'})
        self.assertEqual(result[0]['playlist_index'], 2)
        self.assertEqual(result[1]['playlist_index'], 3)

        result = get_downloaded_info_dicts({'playlist_items': '2-4,3-4,3'})
        self.assertEqual(result[0]['playlist_index'], 2)
        self.assertEqual(result[1]['playlist_index'], 3)
        self.assertEqual(result[2]['playlist_index'], 4)

        result = get_downloaded_info_dicts({'playlist_items': '4,2'})
        self.assertEqual(result[0]['playlist_index'], 4)
        self.assertEqual(result[1]['playlist_index'], 2)
        # @}

    def test_urlopen_no_file_protocol(self):
        # see https://github.com/ytdl-org/youtube-dl/issues/8227
        pdl = PDL()
        self.assertRaises(compat_urllib_error.URLError, pdl.urlopen, 'file:///etc/passwd')

    def test_do_not_override_ie_key_in_url_transparent(self):
        pdl = PDL()

        class Foo1IE(InfoExtractor):
            _VALID_URL = r'foo1:'

            def _real_extract(self, url):
                return {
                    '_type': 'url_transparent',
                    'url': 'foo2:',
                    'ie_key': 'Foo2',
                    'title': 'foo1 title',
                    'id': 'foo1_id',
                }

        class Foo2IE(InfoExtractor):
            _VALID_URL = r'foo2:'

            def _real_extract(self, url):
                return {
                    '_type': 'url',
                    'url': 'foo3:',
                    'ie_key': 'Foo3',
                }

        class Foo3IE(InfoExtractor):
            _VALID_URL = r'foo3:'

            def _real_extract(self, url):
                return _make_result([{'url': TEST_URL}], title='foo3 title')

        pdl.add_info_extractor(Foo1IE(pdl))
        pdl.add_info_extractor(Foo2IE(pdl))
        pdl.add_info_extractor(Foo3IE(pdl))
        pdl.extract_info('foo1:')
        downloaded = pdl.downloaded_info_dicts[0]
        self.assertEqual(downloaded['url'], TEST_URL)
        self.assertEqual(downloaded['title'], 'foo1 title')
        self.assertEqual(downloaded['id'], 'testid')
        self.assertEqual(downloaded['extractor'], 'testex')
        self.assertEqual(downloaded['extractor_key'], 'TestEx')


if __name__ == '__main__':
    unittest.main()
