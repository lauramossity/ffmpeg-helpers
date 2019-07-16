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
    export_video(args)