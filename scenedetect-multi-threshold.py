from __future__ import print_function
import os
import argparse
from io import StringIO

import scenedetect
from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector

def main(source_path):
    SOURCE_FILENAME = os.path.splitext(os.path.basename(source_path))[0]
    OUTPUT_FOLDER = os.path.join(os.getcwd(), SOURCE_FILENAME)
    STATS_FILE_PATH = os.path.join(OUTPUT_FOLDER, SOURCE_FILENAME + '.stats.csv')

    HIGH_CONTENT_THRESHOLD = 55.0 # Try to get big scene changes - new scenery/setting
    LOW_CONTENT_THRESHOLD = 40.0 # Try to pick up smaller scene changes like camera cuts in same location/setting

    # Create a video_manager point to video file testvideo.mp4. Note that multiple
    # videos can be appended by simply specifying more file paths in the list
    # passed to the VideoManager constructor. Note that appending multiple videos
    # requires that they all have the same frame size, and optionally, framerate.
    video_manager = VideoManager([source_path])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    # Add ContentDetector algorithm (constructor takes detector options like threshold).
    scene_manager.add_detector(ContentDetector(threshold=HIGH_CONTENT_THRESHOLD, min_scene_len=300))
    base_timecode = video_manager.get_base_timecode()

    try:
        # If stats file exists, load it.
        if os.path.exists(STATS_FILE_PATH):
            print('Reading stats from file ', STATS_FILE_PATH)
            # Read stats from CSV file opened in read mode:
            with open(STATS_FILE_PATH, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file, base_timecode)

        # Set downscale factor to improve processing speed (no args means default).
        video_manager.set_downscale_factor()

        # # Start detection 3 seconds in
        # video_manager.set_duration(start_time=base_timecode+3.0)

        # # Only use a small amount of the video
        # start_time = base_timecode + 20     # 00:00:00.667
        # end_time = base_timecode + 20.0     # 00:00:20.000
        # # Set video_manager duration to read frames from 00:00:00 to 00:00:20.
        # video_manager.set_duration(start_time=start_time, end_time=end_time)

        # Start video_manager.
        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list_high_threshold = scene_manager.get_scene_list(base_timecode)
        # Like FrameTimecodes, each scene in the scene_list can be sorted if the
        # list of scenes becomes unsorted.

        # We only write to the stats file if a save is required:
        if stats_manager.is_save_required():
            with open(STATS_FILE_PATH, 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)

        print(';'.join(start.get_timecode() + ',' + end.get_timecode() for start, end in scene_list_high_threshold), file=open(os.path.join(OUTPUT_FOLDER, SOURCE_FILENAME + '-majorScenes.txt'), 'w'))
        print(','.join(frametimecode.get_timecode() for frametimecode in scene_manager.get_cut_list(base_timecode)), file=open(os.path.join(OUTPUT_FOLDER, SOURCE_FILENAME + '-majorSceneCuts.txt'), 'w'))
        
        buf = StringIO()
        buf.write('List of scenes obtained, high threshold (%s):\n' % HIGH_CONTENT_THRESHOLD)
        for i, scene in enumerate(scene_list_high_threshold):
            buf.write('    Scene %2d: Start,End Timecodes: %s,%s Frames: %d,%d\n' % (
                i+1,
                scene[0].get_timecode(), scene[1].get_timecode(),
                scene[0].get_frames(), scene[1].get_frames()))

        # Print detailed list to both stdout and file.
        print(buf.getvalue())
        print(buf.getvalue(), file=open(os.path.join(OUTPUT_FOLDER, SOURCE_FILENAME + '-majorScenesPrettyPrint.txt'), 'w'))

        # scene_manager.write_scene_list(os.path.basename(source_path) + '.scenes.csv', scene_list_high_threshold)

        scene_manager.clear()
        scene_manager.clear_detectors()
        scene_manager.add_detector(ContentDetector(threshold=LOW_CONTENT_THRESHOLD, min_scene_len=150))
        video_manager.release()
        video_manager.reset()
        video_manager.start()

        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list_low_threshold = scene_manager.get_scene_list(base_timecode)
        
        print(';'.join(start.get_timecode() + ',' + end.get_timecode() for start, end in scene_list_low_threshold), file=open(os.path.join(OUTPUT_FOLDER, SOURCE_FILENAME + '-minorScenes.txt'), 'w'))
        print(','.join(frametimecode.get_timecode() for frametimecode in scene_manager.get_cut_list(base_timecode)), file=open(os.path.join(OUTPUT_FOLDER, SOURCE_FILENAME + '-minorSceneCuts.txt'), 'w'))

        buf = StringIO()
        buf.write('List of scenes obtained, low threshold (%s):\n' % LOW_CONTENT_THRESHOLD)
        for i, scene in enumerate(scene_list_low_threshold):
            buf.write('    Scene %2d: Start,End Timecodes: %s,%s Frames: %d,%d\n' % (
                i+1,
                scene[0].get_timecode(), scene[1].get_timecode(),
                scene[0].get_frames(), scene[1].get_frames()))
        
        # Print detailed list to both stdout and file.
        print(buf.getvalue())
        print(buf.getvalue(), file=open(os.path.join(OUTPUT_FOLDER, SOURCE_FILENAME + '-minorScenesPrettyPrint.txt'), 'w'))

        # TODO save timecodes to csv or text file

        # use ffmpeg to split into highly compressed videos
        if scenedetect.video_splitter.is_ffmpeg_available():
            if scene_list_high_threshold:
                scenedetect.video_splitter.split_video_ffmpeg(video_manager.get_video_paths(), scene_list_high_threshold,
                    os.path.join(OUTPUT_FOLDER, '${VIDEO_NAME}-major-scene-${SCENE_NUMBER}.mp4'), SOURCE_FILENAME, 
                    arg_override='-c:v libx264 -preset ultrafast -vf scale=320:-2 -crf 32')

            if scene_list_low_threshold:
                scenedetect.video_splitter.split_video_ffmpeg(video_manager.get_video_paths(), scene_list_low_threshold, 
                    os.path.join(OUTPUT_FOLDER, '${VIDEO_NAME}-minor-scene-${SCENE_NUMBER}.mp4'), SOURCE_FILENAME,
                    arg_override='-c:v libx264 -preset ultrafast -vf scale=320:-2 -crf 32')

    finally:
        video_manager.release()
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="path to the source video")
    args = parser.parse_args()
    main(args.source)