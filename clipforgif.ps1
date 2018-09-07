param (
	[Parameter(Mandatory=$true)][string]$source,
	[Parameter(Mandatory=$true)][string]$output,
	[switch]$fastseek, #if set, the second timestamp arg needs to be an offset rather than an absolute timestamp
	[Parameter(Mandatory=$true)][ValidateCount(2,2)][string[]]$timestamps
	#[Parameter(Mandatory=$true)][string]$trim #trim=$trim filter doesn't work
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

# removed -crf 27 -preset fast, trying slow
# removed padding  pad=640:480:4:4:0x000000,
# replaced yadif=deint=interlaced - might get better quality, gif isn't compressed video anyway

#trim before other filters to get right frames

& $ffmpegLoc @openingArgs -an -vcodec libx264 -pix_fmt yuv420p -preset slow -vf "idet, yadif=mode=send_field:parity=auto:deint=interlaced, hqdn3d=3, crop=632:472:8:0, scale=w=iw*1/2:h=ih*1/2, fps=15" -f mp4 $output