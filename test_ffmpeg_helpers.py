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

    if mockObject.call_args is None:
        expected = ("%s called with %s" % (mockObject._mock_name, expectedPattern))
        actual = 'not called.'
        error_message = ('expected call not found.\nExpected: %s\nActual: %s'
                % (expected, actual))
        raise AssertionError(error_message)

    # Args from the first (only) call, ordered arguments from the first tuple member, joined into a string
    joinedArgs = ' '.join(mockObject.call_args[0][0])

    # Assert that the expected string is a substring of the joined ordered arguments
    if not re.search(expectedPattern, joinedArgs):
        expected = ("%s called with args that match the pattern '%s'" % (mockObject._mock_name, expectedPattern))
        actual = ("%s called with %s" % (mockObject._mock_name, mockObject.call_args[0]))
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

            ffmpeg_helpers.main("export -s inputfile -d outputfile --vfs filterscriptfile --vpf presetfile".split())
            assert_called_once_joined_args_match_pattern(MockRun, " -i inputfile")
            assert_called_once_joined_args_match_pattern(MockRun, " -f mp4 outputfile")
            assert_called_once_joined_args_match_pattern(MockRun, "-fpre:v.*presetfile")
            assert_called_once_joined_args_match_pattern(MockRun, "-filter_script:v.*filterscriptfile")
            MockRun.reset_mock()

            # ffmpeg_helpers.main("export -s asdf".split())
            # MockRun.assert_not_called()
            # ffmpeg_helpers.main("export -d asdf".split())
            # MockRun.assert_not_called()
            # ffmpeg_helpers.main("export --vfs asdf".split())
            # MockRun.assert_not_called()

            ffmpeg_helpers.main("export -s asdf -d qwerty".split())
            assert_called_once_joined_args_match_pattern(MockRun, " -i asdf")
            assert_called_once_joined_args_match_pattern(MockRun, " -f mp4 qwerty")
            assert_called_once_joined_args_match_pattern(MockRun, "-fpre:v.*lm-camcorder-hq.ffpreset")
            assert_called_once_joined_args_match_pattern(MockRun, "-filter_script:v.*deinterlace-hq.filter")
            MockRun.reset_mock()
            
            ffmpeg_helpers.main("export -s asdf -d qwerty --time-segment-fast 2:45.784 30".split())
            assert_called_once_joined_args_match_pattern(MockRun, " -ss 2:45.784 -i asdf -t 30")
            assert_called_once_joined_args_match_pattern(MockRun, " -f mp4 qwerty")
            MockRun.reset_mock()

            ffmpeg_helpers.main("export -s asdf -d qwerty --time-segment-slow 2:45.784 5:12.372".split())
            assert_called_once_joined_args_match_pattern(MockRun, " -i asdf -ss 2:45.784 -to 5:12.372")
            assert_called_once_joined_args_match_pattern(MockRun, " -f mp4 qwerty")
            MockRun.reset_mock()

            # TODO spaces in file paths



suite = unittest.TestLoader().loadTestsFromTestCase(TestFfmpegHelpers)
unittest.TextTestRunner(verbosity=2).run(suite)