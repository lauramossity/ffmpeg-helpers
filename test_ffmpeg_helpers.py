import unittest
from unittest import TestCase, mock

import ffmpeg_helpers

# class CustomAssertions(TestCase):
#     def assertCmdLineArgsContains(self,):
#         if 

def assert_called_once_with_substring_of_args(mockObject, expectedArgsSubstring):
    # Assert called exactly once
    if not mockObject.call_count == 1:
        msg = ("Expected '%s' to be called once. Called %s times.%s"
                % (mockObject._mock_name or 'mock',
                    mockObject.call_count,
                    mockObject._calls_repr()))
        raise AssertionError(msg)

    if mockObject.call_args is None:
        expected = ("%s called with %s" % (mockObject._mock_name, expectedArgsSubstring))
        actual = 'not called.'
        error_message = ('expected call not found.\nExpected: %s\nActual: %s'
                % (expected, actual))
        raise AssertionError(error_message)

    # Args from the first (only) call, ordered arguments from the first tuple member, joined into a string
    joinedArgs = ' '.join(mockObject.call_args[0][0])

    # Assert that the expected string is a substring of the joined ordered arguments
    if expectedArgsSubstring not in joinedArgs:
        expected = ("%s called with args that contain '%s'" % (mockObject._mock_name, expectedArgsSubstring))
        actual = ("%s called with %s" % (mockObject._mock_name, mockObject.call_args[0]))
        error_message = ('expected call not found.\nExpected: %s\nActual: %s'
                % (expected, actual))
        raise AssertionError(error_message)

class TestFfmpegHelpers(TestCase):
    def test_export(self):
        with mock.patch('subprocess.run') as MockRun:
            ffmpeg_helpers.main("export -s asdf -d asdf".split())
            assert_called_once_with_substring_of_args(MockRun, " -i asdf")
            assert_called_once_with_substring_of_args(MockRun, " -f mp4 asdf")
            # TODO preset and filter filenames
            MockRun.reset_mock()

            # TODO match pattern (to find filename in substring)

suite = unittest.TestLoader().loadTestsFromTestCase(TestFfmpegHelpers)
unittest.TextTestRunner(verbosity=2).run(suite)