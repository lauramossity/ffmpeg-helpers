param (
	[Parameter(Mandatory=$true)][string]$source,
	[Parameter(Mandatory=$true)][string]$output,
	[Parameter(Mandatory=$true)][string]$segmentstoremove
)

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

$command = "$ffmpegLoc -i $source"

# TODO if initialized like ,@(), end up with blank initial element
$filenames = @()

$i = 0;
foreach($pair in $segmentArray) {
    # end segment, start cutting from pair start
    $filename = "$($sourcePath.Name)-part$i$($sourcePath.Extension)"
    $filenames += $filename
    $command += " -to $($pair[0]) $filename"

    # start time for next segment
    $command += " -ss $($pair[1])"

    $i++
}

$filename = "$($sourcePath.Name)-part$i$($sourcePath.Extension)"
$filenames += $filename
$command += " $filename"

$command += " -codec:v copy -codec:a copy -avoid_negative_ts 1"
echo "Executing ffmpeg split command:" $command

Invoke-Expression "& $command"

# TODO needs to be UTF-8 or ANSI not UTF-BOM - https://trac.ffmpeg.org/ticket/3718
$(foreach ($file in $filenames) { echo "file `'$file`'" }) | out-file -encoding ASCII segments.txt

$concatCommand = "$ffmpegLoc -f concat -i segments.txt -c copy $($sourcePath.Name)-combined$($sourcePath.Extension)"

echo "Executing ffmpeg concatenation command:" $concatCommand
Invoke-Expression "& $concatCommand"