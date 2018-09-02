# C64 Pixel Tools

These are two simple tools I used to make [Rescuing Orc](https://www.usebox.net/jjm/rescuing-orc/).

Convert PNG images into sprites and tilesets to be used by the Commodore 64.

 * `img2sprite.py`
 * `img2tileset.py`

Each tool has help in the `CLI` with `-h`.

## Requirements

 * Python 2.7
 * Pillow

##  img2sprite

This tool takes an indexed PNG image and encodes it as a valid multicolor
sprite.

The transparent and sprite specific colors can be specified with a flag,
the shared colours are in ascending order.

The colors are not included in the output.

## img2tileset

This tools takes an indexed PNG image and encodes it as a valid 4x8 multicolor
tileset (charset).

The shared colors must be provided as a colon-separated list (eg. 0:1:12). The
foreground is detected per tile (from 0 to 7, the tool converts it
automatically to the 8 to 15 range).

