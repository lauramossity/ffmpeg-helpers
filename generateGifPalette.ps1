# try running as administrator

$video = $args[0]
$palette = 'palette.png'
$output = $args[1]

& ffmpeg -i $video -vf fps=15,scale=320:-1:flags=lanczos,palettegen -y $palette
& ffmpeg -i $video -i $palette -an -lavfi "fps=15,scale=400:-1:flags=lanczos[x];[x][1:v]paletteuse" $output

remove-item $palette