import unittest
from unittest import TestCase, mock
import re

import ffmpeg_helpers


def assert_called_once_joined_args_match_pattern(mockObject, expectedPattern):
    # Assert called exactly once
    if not mockObject.call_count == 1:
        msg = ("Expected '%s' to be called once. Called %s times.%s"
               % (mockObject._mock_name or 'mock',
                  mockObject.call_count,
                  mockObject._calls_repr()))
        raise AssertionError(msg)

    assert_nth_call_joined_args_match_pattern(mockObject, 1, expectedPattern)


def assert_nth_call_joined_args_match_pattern(mockObject, n, expectedPattern):
    if mockObject.call_args is None:
        expected = ("%s called with %s" % (mockObject._mock_name, expectedPattern))
        actual = 'not called.'
        error_message = ('expected call not found.\nExpected: %s\nActual: %s'
                         % (expected, actual))
        raise AssertionError(error_message)

    if mockObject.call_count < n:
        expected = ("%s called with %s on %dth call" % (mockObject._mock_name, expectedPattern, n))
        actual = 'not called %d times.' % n
        error_message = ('expected call not found.\nExpected: %s\nActual: %s'
                         % (expected, actual))
        raise AssertionError(error_message)

    # Args from the nth call, ordered arguments, first argument, joined into a string
    joinedArgs = ' '.join(mockObject.call_args_list[n - 1][0][0])

    # Assert that the expected string is a substring of the joined ordered arguments
    if not re.search(expectedPattern, joinedArgs):
        expected = ("%s called with args that match the pattern '%s'" % (mockObject._mock_name, expectedPattern))
        actual = ("%s called with %s" % (mockObject._mock_name, mockObject.call_args_list[n - 1]))
        error_message = ('expected call not found.\nExpected: %s\nActual: %s'
                         % (expected, actual))
        raise AssertionError(error_message)


class TestFfmpegHelpers(TestCase):
    def test_export(self):
        with mock.patch('subprocess.run') as MockRun:
            ffmpeg_helpers.main("export -s asdf -d qwerty".split())
            assert_called_once_joined_args_match_pattern(MockRun, " -i asdf")
            assert_called_once_joined_args_match_pattern(MockRun, " -f mp4 qwerty")
            assert_called_once_joined_args_match_pattern(MockRun, "-fpre:v.*lm-camcorder-hq.ffpreset")
            assert_called_once_joined_args_match_pattern(MockRun, "-filter_script:v.*deinterlace-hq.filter")
            MockRun.reset_mock()

            self.assertRaises(SystemExit, ffmpeg_helpers.main, "export -s asdf".split())
            self.assertRaises(SystemExit, ffmpeg_helpers.main, "export -d asdf".split())
            self.assertRaises(SystemExit, ffmpeg_helpers.main, "export --vfs asdf".split())

            # TODO spaces in file paths

    def test_export_using_preset_and_filterscript(self):
        with mock.patch('subprocess.run') as MockRun:
            ffmpeg_helpers.main("export -s inputfile -d outputfile --vfs filterscriptfile --vpf presetfile".split())
            assert_called_once_joined_args_match_pattern(MockRun, " -i inputfile")
            assert_called_once_joined_args_match_pattern(MockRun, " -f mp4 outputfile")
            assert_called_once_joined_args_match_pattern(MockRun, "-fpre:v.*presetfile")
            assert_called_once_joined_args_match_pattern(MockRun, "-filter_script:v.*filterscriptfile")
            MockRun.reset_mock()

    def test_export_time_segment(self):
        with mock.patch('subprocess.run') as MockRun:
            ffmpeg_helpers.main("export -s asdf -d qwerty --time-segment-fast 2:45.784 30".split())
            assert_called_once_joined_args_match_pattern(MockRun, " -ss 2:45.784 -i asdf -t 30")
            assert_called_once_joined_args_match_pattern(MockRun, " -f mp4 qwerty")
            MockRun.reset_mock()

            ffmpeg_helpers.main("export -s asdf -d qwerty --time-segment-slow 2:45.784 5:12.372".split())
            assert_called_once_joined_args_match_pattern(MockRun, " -i asdf -ss 2:45.784 -to 5:12.372")
            assert_called_once_joined_args_match_pattern(MockRun, " -f mp4 qwerty")
            MockRun.reset_mock()

            # TODO spaces in file paths

    def test_edit(self):
        mock_file_1 = '''start_timecode,end_timecode,notes
0:03:44.825,0:08:54.968
0:11:14.424,0:12:50.019'''

        with mock.patch('subprocess.run') as MockRun:
            MockOpen = mock.mock_open(read_data=mock_file_1)
            with(mock.patch('builtins.open', MockOpen, create=True)):
                ffmpeg_helpers.main("edit -s asdf.xyz --segmentsToCut qwerty.csv".split())

                assert_nth_call_joined_args_match_pattern(MockRun, 1,
                                                          " -i asdf.xyz -codec:v copy -codec:a copy "
                                                          "-avoid_negative_ts 1")
                assert_nth_call_joined_args_match_pattern(MockRun, 1,
                                                          "-to 0:03:44.825 asdf-part00.xyz -ss 0:08:54.968 -to "
                                                          "0:11:14.424 asdf-part01.xyz -ss 0:12:50.019 asdf-part02.xyz")
                assert_nth_call_joined_args_match_pattern(MockRun, 2,
                                                          "-f concat -i segments.txt -c copy asdf-combined.xyz")

        # TODO test start timestamp 0
        # TODO check segments file for number of segments generated
        # TODO test bad file and/or one with no lines


suite = unittest.TestLoader().loadTestsFromTestCase(TestFfmpegHelpers)
unittest.TextTestRunner(verbosity=2).run(suite)
