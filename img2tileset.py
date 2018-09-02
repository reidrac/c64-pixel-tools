#!/usr/bin/env python
#
# Copyright (C) 2018 by Juan J. Martinez <jjm@usebox.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

__version__ = "1.0"

import sys
import os
from argparse import ArgumentParser
from PIL import Image
import subprocess
import tempfile

DEF_W = 4
DEF_H = 8

def main():

    parser = ArgumentParser(description="Image to multicolor tileset (charset)",
                            epilog="Copyright (C) 2018 Juan J Martinez <jjm@usebox.net>",
                            )

    parser.add_argument("--version", action="version", version="%(prog)s "  + __version__)
    parser.add_argument("-i", "--id", dest="id", default="tileset", type=str,
                        help="variable name (default: tileset)")
    parser.add_argument("-b", "--binary", dest="binary", action="store_true",
                        help="output binary instead of ASM code")
    parser.add_argument("--no-attr", dest="no_attr", action="store_true",
                        help="don't include attributes")

    parser.add_argument("image", help="image to convert")
    parser.add_argument("colors", help="colon-separated shared colors (eg. 0:1:12)")

    args = parser.parse_args()

    shared = [int(c.strip()) for c in args.colors.split(":")]

    if len(set(shared)) != 3:
        parser.error("3 different colors expected")

    try:
        image = Image.open(args.image)
    except IOError:
        parser.error("failed to open the image")

    if image.mode != "P":
        parser.error("not an indexed image (no palette)")

    (w, h) = image.size

    if w % DEF_W or h % DEF_H:
        parser.error("%s size is not multiple of the tile size (%dx%d)" % (args.image, DEF_W, DEF_H))

    data = image.getdata()

    fg = []
    out = []
    tiles = 0
    for y in range(0, h, DEF_H):
        for x in range(0, w, DEF_W):
            tile = [data[x + i + ((y + j) * w)] for j in range(DEF_H) for i in range(4)]
            colors = list(set(tile))

            new_fg = [c for c in colors if c not in shared]
            if len(new_fg) > 1:
                parser.error("tile %s doesn't have the expected shared colours (%r found, %r expected)" % (x // DEF_W, colors, shared))
            elif not new_fg:
                new_fg.append(0)

            if new_fg[0] > 7:
                parser.error("tile %s fg color out of range" % (x // DEF_W))

            fg.append(new_fg[0] + 8)
            colors = shared + new_fg

            frame = []
            for i in range(0, len(tile), 4):
                byte = 0
                p = 6
                for k in range(4):
                    byte |= (colors.index(tile[i + k]) & 3) << p
                    p -= 2

                frame.append(byte)
            tiles += 1
            out.extend(frame)

    if tiles > 256:
        parser.error("more than 256 tiles")

    if args.binary:
        if not args.no_attr:
            out = fg + out
        sys.stdout.write(bytearray(out))
        return

    data_out = ""
    for part in range(0, len(out), 8):
        data_out += "\n\t.byte "
        data_out += ', '.join(["$%02x" % b for b in out[part: part + 8]])

    cols_out = ""
    for part in range(0, len(fg), 8):
        cols_out += "\n\t.byte "
        cols_out += ', '.join(["$%02x" % b for b in fg[part: part + 8]])

    print("; %s tiles" % tiles)
    if not args.no_attr:
        print("%s_cols:%s" % (args.id, cols_out))
    print("%s:%s\n" % (args.id, data_out))

if __name__ == "__main__":
    main()

