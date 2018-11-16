param (
	[Parameter(Mandatory=$true)][string]$source,
	[Parameter(Mandatory=$true)][string]$segmentstoremove
)

# Remove the time segments specified in a file.
# Splits the video based on those time segments and re-joins the split clips.
# See https://trac.ffmpeg.org/wiki/Concatenate

$sourcePath = Get-Item $source

$strSegmentList = Get-Content $segmentstoremove -Raw

# Split input list into comma-separated pairs
$segmentPairs = $strSegmentList.Split(";")

# Fill a multi-dimensional array with the comma-separated pairs
$segmentArray = ,@() * $segmentPairs.Length
for($i = 0; $i -lt $segmentPairs.Length; $i++) {
    $segmentArray[$i] = $segmentPairs[$i].Split(",");
}

$ffmpegLoc = "'C:\Program Files\ffmpeg\bin\ffmpeg.exe'"

$splitCommand = "$ffmpegLoc -i $source"

# TODO if initialized like ,@(), end up with blank initial element
$filenames = @()

# Generate the ffmpeg command to split
$i = 0;
foreach($pair in $segmentArray) {
    # end segment, start cutting from pair start
    $filename = "$($sourcePath.BaseName)-part$($i.ToString("00"))$($sourcePath.Extension)"
    $filenames += $filename
    $splitCommand += " -to $($pair[0]) $filename"

    # start time for next segment
    $splitCommand += " -ss $($pair[1])"

    $i++
}

$filename = "$($sourcePath.BaseName)-part$($i.ToString("00"))$($sourcePath.Extension)"
$filenames += $filename
$splitCommand += " $filename"

# Need avoid_negative_ts flag so that split segments will have the 0 timestamp at the start of the video
$splitCommand += " -codec:v copy -codec:a copy -avoid_negative_ts 1"

echo "Executing ffmpeg split command:" $splitCommand
Invoke-Expression "& $splitCommand"

# Generate a file with the list of files to re-join
# Contains lines that look like:
# file 'source-video-part00.mp4'
# Needs to be UTF-8 or ANSI not UTF-BOM - https://trac.ffmpeg.org/ticket/3718
$(foreach ($file in $filenames) { echo "file `'$file`'" }) | out-file -encoding ASCII segments.txt

$concatCommand = "$ffmpegLoc -f concat -i segments.txt -c copy $($sourcePath.BaseName)-combined$($sourcePath.Extension)"

# TODO - concat -i file1.mp4 -i file2.mp4 ... method resulted in file1.mp4: Invalid data found when processing input

echo "Executing ffmpeg concatenation command:" $concatCommand
Invoke-Expression "& $concatCommand"

# TODO clean up intermediate files