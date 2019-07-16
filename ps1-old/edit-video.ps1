param (
	[Parameter(Mandatory=$true)][string]$source,
	[Parameter(Mandatory=$true)][string]$segmentstoremove
)

# Remove the time segments specified in a csv file.
# Splits the video based on those time segments and re-joins the split clips.
# The timestamps in the file must be in order from earliest to latest.
# See https://trac.ffmpeg.org/wiki/Concatenate

# TODO strip whitespace
$sourcePath = Get-Item $source
$sourcePathBaseName = (Get-Item -Path $sourcePath).Basename.replace(' ', '_')

# Requires columns named start_timecode and end_timecode
$segmentRows = Import-Csv $segmentstoremove

$splitCommand = "ffmpeg -i '$source'"

# Need avoid_negative_ts flag so that split segments will have the 0 timestamp at the start of the video
$splitCommand += " -codec:v copy -codec:a copy -avoid_negative_ts 1"

# If initialized like ,@(), initial element is blank (?)
$filenames = @()

# Generate the ffmpeg command to split
# TODO error if no valid rows
# TODO error if segments are out of order
# TODO error if exactly adjacent segments
$i = 0;
foreach($segmentRow in $segmentRows) {
    # If the timestamp is not 0 (contains characters other than 0, :, or .)
    if( $segmentRow.start_timecode -match '.*[^:.0].*' ) {
        # end segment, start cutting from pair start
        $filename = "$($sourcePathBaseName)-part$($i.ToString("00"))$($sourcePath.Extension)"
        $filenames += $filename
        $splitCommand += " -to $($segmentRow.start_timecode) $filename"
    }

    # start time for next segment
    $splitCommand += " -ss $($segmentRow.end_timecode)"

    $i++
}

$filename = "$($sourcePathBaseName)-part$($i.ToString("00"))$($sourcePath.Extension)"
$filenames += $filename
$splitCommand += " $filename"

Write-Host "Executing ffmpeg split command:" $splitCommand -ForegroundColor Yellow
Invoke-Expression "& $splitCommand"

# Generate a file segments.txt with the list of files to re-join
# Contains lines that look like:
# file 'source-video-part00.mp4'
# Needs to be UTF-8 or ANSI not UTF-BOM - https://trac.ffmpeg.org/ticket/3718
$(foreach ($file in $filenames) { echo "file `'$file`'" }) | out-file -encoding ASCII segments.txt

$concatCommand = "ffmpeg -f concat -i segments.txt -c copy $($sourcePathBaseName)-combined$($sourcePath.Extension)"

# TODO - concat -i file1.mp4 -i file2.mp4 ... method resulted in file1.mp4: Invalid data found when processing input

Write-Host "Executing ffmpeg concatenation command:" $concatCommand -ForegroundColor Yellow
Invoke-Expression "& $concatCommand"

# TODO clean up intermediate files