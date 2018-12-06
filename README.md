# ffmpeg-helpers

This repository contains documentation of my process for capturing and converting a set of Hi-8 camcorder tapes, with some helper scripts that act as a wrapper around ffmpeg and pyscenedetect.

## Dependencies

* VirtualDub FilterMod (packaged with Lagarith codec)
    * For raw capture
    * Also useful for previewing video and grabbing precise timestamps
* ffmpeg
* pyscenedetect: https://pyscenedetect.readthedocs.io/en/latest/
    * Requires python and other documented dependencies
    * Currently using an older version (v0.4) that uses different command line args.

    

### Optional but also useful

* Mediainfo
* VLC
---
## Lossless Capture using VirtualDub
TODO
### Fixing audio sync problems
TODO

---
## Processing and Compression using ffmpeg
TODO

```
.\export-video.ps1 -source lossless-source-video.avi -output output-file.mp4 -vfilterscript .\deinterlace-hq.filter -vpresetfile .\lm-camcorder-hq.ffpreset
```

### Filter and Preset File Reference
TODO

---
## Editing and Splitting using pyscenedetect and ffmpeg
### Scene Detection
Scene detection MUST be done on content that has been deinterlaced (H264 MP4 output from [Processing and compression using ffmpeg](#processing-and-compression-using-ffmpeg) )  
The [scenedetect-multi-threshold.py](scenedetect-multi-threshold.py) script uses the pyscenedetect library to find scenes at two thresholds (55 and 40) in content-aware detection mode. The high threshold scenes are likely to be useful for splitting out major sections of the video and the lower threshold is likely to be useful for chapter markers.

Example usage:
```
python .\scenedetect-multi-threshold.py .\path\to\a-deinterlaced-video.mp4
```
The script prints the timestamps and frames for each scene found at both thresholds. From the timestamps, construct a `.segments` file described below in [Editing](#editing).

<!---
TODO: In the working directory, if ffmpeg is available, the script will split the video for each set of scenes and put the split videos in the working directory. These will be low-quality, compressed videos intended to assist with previewing the found scenes.
--->

It also writes out a `stats.csv` file in the working directory containing the stats for each frame of the video. This is reused in the second pass for the second threshold and on subsequent runs if found.
#### Dependencies
* Python (script developed against 3.7)
* PySceneDetect v0.5
    * OpenCV / cv2 python module: `python -m pip install opencv-python`
    * numpy: `python -m pip install numpy`
    * tqdm (optional): `python -m pip install tqdm`
<!---
    * ffmpeg in path (optional, if split video previews are desired)
--->

Alternatively, the standalone PySceneDetect can be used to do each threshold separately.
<!-- TODO: Add example --->

### Editing
TODO
```
edit-video.ps1 -source path\to\source\video.mp4 -segmentstoremove path\to\file\with\segments.segments
```
A `.segments` file contains a list of pairs of time intervals to be removed. Each pair is separated by `;` and the timestamps in the pair are separated by `,`  
Example:
```
01:00,02:00;15:11.1,18:45.8
```
In this case, video from 1 minute in to 2 minutes in, and from 15:11.1 to 18:45.8 will be removed from the output video.

<!-- TODO: investigate why the output here is variable frame rate and deinterlaced video is fixed frame rate? --->

---
## Gifs
TODO