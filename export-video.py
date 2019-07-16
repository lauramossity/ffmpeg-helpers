import argparse
import os

def main(source_path):
    print("hello")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_PRESET_FILE = "lm-camcorder-hq.ffpreset"
    DEFAULT_FILTER_SCRIPT = "deinterlace-hq.filter"
    
    # TODO use subparsers

    parser = argparse.ArgumentParser()

    ioGroup = parser.add_argument_group("I/O")
    ioGroup.add_argument("-s", "--source", help="path to the source video", required=True)
    ioGroup.add_argument("-d", "--destination", metavar="DEST", help="path to the destination video file", required=True)
    
    videoSettingsGroup = parser.add_argument_group("ffmpeg video settings")
    videoSettingsGroup.add_argument("--vfs", "--vfilterscript", metavar="VIDEO_FILTER_SCRIPT",
                        help="ffmpeg filter script to be used in the -filter_script:v argument (default: " + DEFAULT_FILTER_SCRIPT + ")", 
                        default=os.path.join(SCRIPT_DIR, DEFAULT_FILTER_SCRIPT))
    videoSettingsGroup.add_argument("--vpf", "--vpresetfile", metavar="VIDEO_PRESET_FILE",
                        help="ffmpeg preset file to be used in the -fpre:v argument (default: " + DEFAULT_PRESET_FILE + ")",
                        default=os.path.join(SCRIPT_DIR, DEFAULT_PRESET_FILE))
    
    # https://trac.ffmpeg.org/wiki/Seeking
    timestampGroup = parser.add_argument_group("Extract segment", "See https://trac.ffmpeg.org/wiki/Seeking for details")
    timestampMutexGroup = timestampGroup.add_mutually_exclusive_group()
    timestampMutexGroup.add_argument("--time-segment-fast", nargs=2, metavar=("START_TIMESTAMP", "TIME_LENGTH"), help="Time segment to extract using the keyframe method. May be inaccurate on stream copy. Example: 1:01.123 2")
    timestampMutexGroup.add_argument("--time-segment-slow", nargs=2, metavar=("START_TIMESTAMP", "END_TIMESTAMP"), help="Time segment to extract using a slow seek. Example: 1:01.123 1:03:123")
    
    args = parser.parse_args()
    main(args.source)