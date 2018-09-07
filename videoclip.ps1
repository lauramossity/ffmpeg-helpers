param (
	[Parameter(Mandatory=$true)][string]$source,
	[Parameter(Mandatory=$true)][string]$output,
	[switch]$fastseek, #if set, the second timestamp arg needs to be an offset rather than an absolute timestamp
	[Parameter(Mandatory=$true)][ValidateCount(2,2)][string[]]$timestamps
)

$ffmpegLoc = 'C:\Program Files\ffmpeg\bin\ffmpeg.exe'

if($fastseek)
{
	$openingArgs = "-ss", $timestamps[0], "-i", $source, "-t", $timestamps[1]
}
else
{
	$openingArgs = "-i", $source, "-ss", $timestamps[0], "-to", $timestamps[1]
}

#Find interlaced frames, deinterlace only interlaced frames, denoise, remove 8px from left and bottom, add black padding back, scale down to 3/4 of the size, 30fps
$videoFilters = "idet, yadif=deint=interlaced, hqdn3d=3, crop=632:472:8:0, pad=640:480:4:4:0x000000, scale=w=iw*3/4:h=ih*3/4, fps=30"

# Audio: 192kbps, 48000, Select left audio channel to mono
# todo test with already mono video

# timestamp args after input for proper end stamp. see https://trac.ffmpeg.org/wiki/Seeking
& $ffmpegLoc @openingArgs -c:a aac -b:a 192k -ar 48000 -af "pan=mono|c0=c0" -vcodec libx264 -pix_fmt yuv420p -crf 26 -preset fast -vf "$videoFilters" -f mp4 $output


# ?
# -x264opts colormatrix=bt709:vbv-maxrate=62500:vbv-bufsize=78125