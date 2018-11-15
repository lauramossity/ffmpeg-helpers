# ffmpeg-helpers

This repository contains documentation of my process for capturing and converting a set of Hi-8 camcorder tapes, with some helper scripts that act as a wrapper around ffmpeg.

## Prerequisites

* VirtualDub FilterMod (packaged with Lagarith codec)
    * For raw capture
    * Also useful for previewing video and grabbing precise timestamps
* ffmpeg
* pyscenedetect: https://pyscenedetect.readthedocs.io/en/latest/
    * Currently using an older version (v0.4) that uses different command line args.

### Optional but also useful

* Mediainfo
* VLC