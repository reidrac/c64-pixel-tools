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
from argparse import ArgumentParser
from PIL import Image

DEF_W = 12
DEF_H = 21

def main():

    parser = ArgumentParser(description="Image to multicolor sprite",
                            epilog="Copyright (C) 2018 Juan J Martinez <jjm@usebox.net>",
                            )

    parser.add_argument("--version", action="version", version="%(prog)s "  + __version__)
    parser.add_argument("-i", "--id", dest="id", default="sprite", type=str,
                        help="variable name (default: sprite)")
    parser.add_argument("--tc", dest="tc", default=None, type=int,
                        help="palette index for the transparent color (default: use order)")
    parser.add_argument("--sc", dest="sc", default=None, type=int,
                        help="palette index for the sprite main color (default: use order)")
    parser.add_argument("-b", "--binary", dest="binary", action="store_true",
                        help="output binary instead of ASM code")


    parser.add_argument("image", help="image to convert", nargs="?")

    args = parser.parse_args()

    if not args.image:
        parser.error("required parameter: image")

    if args.tc:
        args.tc = int(args.tc)
        if not (0 <= args.tc < 16):
            parser.error("--tc expects an integer in [0, 15]")

    if args.sc:
        args.sc = int(args.sc)
        if not (0 <= args.sc < 16):
            parser.error("--sc expects an integer in [0, 15]")

    try:
        image = Image.open(args.image)
    except IOError:
        parser.error("failed to open the image")

    if image.mode != "P":
        parser.error("not an indexed image (no palette)")

    (w, h) = image.size

    if w % DEF_W or h % DEF_H:
        parser.error("%s size is not multiple of the sprite size (%dx%d)" % (args.image, DEF_W, DEF_H))

    data = image.getdata()

    # get the image unique colors
    colors = []
    for c in data:
        if c not in colors:
            colors.append(c)

    if len(colors) > 4:
        parser.error("the input image has more than 4 colours (%d found)" % len(colors))
    elif len(colors) < 4:
        colors.extend([0 for _ in range(4 - len(colors))])

    colors = sorted(colors)

    if args.tc not in colors:
        parser.error("transparent color not present")
    else:
        colors.remove(args.tc)
        colors = [ args.tc ] + colors

    if args.sc not in colors:
        parser.error("sprite color not present")
    else:
        colors.remove(args.sc)
        colors.insert(-1, args.sc)

    out = []
    for x in range(0, w, DEF_W):
        frame = []
        for y in range(h):
            for i in range(0, DEF_W, 4):
                byte = 0
                p = 6
                for k in range(4):
                    byte |= (colors.index(data[x + i + k + (y * w)]) & 3) << p
                    p -= 2
                frame.append(byte)
        out.append(frame)

    if args.binary:
        for frame in out:
            sys.stdout.write(bytearray(frame))
        return

    frames = len(out)

    data_out = ""
    for block in out:
        for part in range(0, len(block), 8):
            data_out += "\n\t.byte "
            data_out += ', '.join(["$%02x" % b for b in block[part: part + 8]])

    print("; frames: %s (%s bytes per frame)" % (frames, len(out[0])))
    print("%s:%s\n" % (args.id, data_out))

if __name__ == "__main__":
    main()

