param (
	[Parameter(Mandatory=$true)][string]$source,
	[Parameter(Mandatory=$true)][string]$output,
	[switch]$fastseek, #if set, the second timestamp arg needs to be an offset rather than an absolute timestamp
	[ValidateCount(2,2)][string[]]$timestamps,
	[string]$vfilterscript,
	[string]$vpresetfile
)

# timestamp args after input for proper end stamp. see https://trac.ffmpeg.org/wiki/Seeking
if($timestamps) {
	if($fastseek) {
		$sourceAndSeekArgs = "-ss", $timestamps[0], "-i", "'$source'",  "-t", $timestamps[1]
	} else {
		$sourceAndSeekArgs = "-i", "'$source'", "-ss", $timestamps[0], "-to", $timestamps[1]
	}
} else {
	$sourceAndSeekArgs = "-i", "'$source'"
}

#Find interlaced frames, deinterlace only interlaced frames, denoise, remove 8px from left and bottom, add black padding back, ensure original scale
$videoFilters = "yadif=mode=send_field:parity=tff:deint=all, hqdn3d=8, crop=632:472:8:0, scale=640:480"

$defaultFilterScriptLoc = Join-Path -Path $PSScriptRoot -ChildPath "deinterlace-hq.filter"

if($vfilterscript) {
	$videoFilterArgs = "-filter_script:v $vfilterscript"
} elseif(Test-Path $defaultFilterScriptLoc) {
	$videoFilterArgs = "-filter_script:v $defaultFilterScriptLoc"
} else {
	$videoFilterArgs = "-vf '$videoFilters'"
}

$defaultPresetFileLoc = Join-Path -Path $PSScriptRoot -ChildPath "lm-camcorder-hq.ffpreset"

if($vpresetfile) {
	$videoPresetArgs = "-fpre:v $vpresetfile"
} elseif(Test-Path $defaultPresetFileLoc) {
	$videoPresetArgs = "-fpre:v $defaultPresetFileLoc"
}

# Audio: 192kbps, 48000, Select left audio channel to mono
$audioFilters = 'pan=mono|c0=c0'
$audioArgs = "-c:a aac -b:a 192k -ar 48000 -af '$audioFilters'"

# Need to hardcode pix_fmt - not allowed in preset file
$command = "ffmpeg $sourceAndSeekArgs $audioArgs $videoPresetArgs -pix_fmt yuv420p $videoFilterArgs -f mp4 '$output'"

Write-Host "Executing ffmpeg command:" $command -ForegroundColor Yellow
Invoke-Expression "& $command"