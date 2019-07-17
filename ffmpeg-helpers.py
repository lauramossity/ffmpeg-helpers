import argparse
import os
import subprocess

def export_video(args):
    print(args)

    # Path to source video and which segment
    sourceAndSeekArgs = ["-i", args.source]
    if(args.time_segment_fast):
        sourceAndSeekArgs = ["-ss", args.time_segment_fast[0], "-i", args.source, "-t", args.time_segment_fast[1]]
    elif(args.time_segment_slow):
        sourceAndSeekArgs = ["-i", args.source, "-ss", args.time_segment_slow[0], "-to", args.time_segment_slow[1]]

    # Audio: 192kbps, 48000, Select left audio channel to mono
    audioFilters = "'pan=mono|c0=c0'"
    audioArgs = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-af", audioFilters]
    
    ffmpegArgs = ["ffmpeg", *sourceAndSeekArgs, *audioArgs]

    # Format/encoding presets
    if(args.vpf):
        ffmpegArgs.extend(["-fpre:v", args.vpf])

    ffmpegArgs.extend(["-pix_fmt", "yuv420p"])

    # Video output filters
    if(args.vfs):
        ffmpegArgs.extend(["-filter_script:v", args.vfs])
    else:
        #Find interlaced frames, deinterlace only interlaced frames, denoise, remove 8px from left and bottom, add black padding back, ensure original scale
        ffmpegArgs.extend(["-vf", "'yadif=mode=send_field:parity=tff:deint=all, hqdn3d=8, crop=632:472:8:0, scale=640:480'"])

    # Output
    ffmpegArgs.extend(["-f", "mp4", args.destination])

    print("Running ffmpeg command:")
    print(' '.join(ffmpegArgs) + '\n\n')
    subprocess.run(ffmpegArgs)

def create_gif(args):
    print("Create Gif function")

def edit_video(args):
    print("Edit Video function")

def init_video_clip_subparser(subparsers, name, function, helpMessage, defaultFilterScript, defaultPresetfile):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    subparser = subparsers.add_parser(name, help=helpMessage)
    subparser.set_defaults(func=function)

    # TODO make destination optional
    ioGroup = subparser.add_argument_group("I/O")
    ioGroup.add_argument("-s", "--source", help="path to the source video", required=True)
    ioGroup.add_argument("-d", "--destination", metavar="DEST", help="path to the destination video file", required=True)
    
    videoSettingsGroup = subparser.add_argument_group("ffmpeg video settings")
    videoSettingsGroup.add_argument("--vfs", "--vfilterscript", metavar="VIDEO_FILTER_SCRIPT",
                        help="ffmpeg filter script to be used in the -filter_script:v argument (default: " + defaultFilterScript + ")", 
                        default=os.path.join(SCRIPT_DIR, defaultFilterScript))
    videoSettingsGroup.add_argument("--vpf", "--vpresetfile", metavar="VIDEO_PRESET_FILE",
                        help="ffmpeg preset file to be used in the -fpre:v argument (default: " + defaultPresetfile + ")",
                        default=os.path.join(SCRIPT_DIR, defaultPresetfile))
    
    # TODO make segment mandatory for gif
    # https://trac.ffmpeg.org/wiki/Seeking
    timestampGroup = subparser.add_argument_group("Extract segment", "See https://trac.ffmpeg.org/wiki/Seeking for details")
    timestampMutexGroup = timestampGroup.add_mutually_exclusive_group()
    timestampMutexGroup.add_argument("--time-segment-fast", nargs=2, metavar=("START_TIMESTAMP", "TIME_LENGTH"), help="Time segment to extract using the keyframe method. May be inaccurate on stream copy. Example: 1:01.123 2")
    timestampMutexGroup.add_argument("--time-segment-slow", nargs=2, metavar=("START_TIMESTAMP", "END_TIMESTAMP"), help="Time segment to extract using a slow seek. Example: 1:01.123 1:03:123")
    
    return subparser

if __name__ == "__main__":
    DEFAULT_FILTER_SCRIPT = "deinterlace-hq.filter"
    DEFAULT_PRESET_FILE = "lm-camcorder-hq.ffpreset"

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands')

    init_video_clip_subparser(subparsers, 'export', export_video, "Convert a video or video segment to a new format", DEFAULT_FILTER_SCRIPT, DEFAULT_PRESET_FILE)

    # TODO destination should be gif location? or just autogenerate file name
    init_video_clip_subparser(subparsers, 'gif', create_gif, "Export a video clip as a gif", "deinterlace-small.filter", "lm-camcorder-small.ffpreset")

    edit_parser = subparsers.add_parser("edit", help="Remove segments from a video")
    edit_parser.set_defaults(func=edit_video)
    edit_parser.add_argument("-s", "--source", help="path to the source video", required=True)
    edit_parser.add_argument("--segmentsToCut", help="path to a CSV file of segments to cut", required=True)

    args = parser.parse_args()
    args.func(args)