#!/usr/bin/env python3
"""
Text and subtitle overlay script

Usage:
  # Add static text (centered, 0~5 seconds)
  python3 subtitle.py --input in.mp4 --text "Title" --start 0 --end 5 --x center --y 100 --output out.mp4

  # Burn SRT subtitles
  python3 subtitle.py --input in.mp4 --srt subs.srt --output out.mp4

  # Burn ASS subtitles
  python3 subtitle.py --input in.mp4 --ass subs.ass --output out.mp4

Position keywords:
  --x: pixel value or "center"
  --y: pixel value or "top" / "center" / "bottom"

Dependencies: pip install ffmpeg-python
"""

import argparse
import os
import sys

try:
    import ffmpeg
except ImportError:
    print("Error: ffmpeg-python not installed, please run: pip install ffmpeg-python", file=sys.stderr)
    sys.exit(1)

# Mapping of y position keywords to FFmpeg drawtext expressions
Y_KEYWORDS = {
    "top": "50",
    "center": "(h-text_h)/2",
    "bottom": "h-text_h-50",
}

X_KEYWORDS = {
    "center": "(w-text_w)/2",
}


def build_x_expr(x_val):
    if isinstance(x_val, str) and x_val in X_KEYWORDS:
        return X_KEYWORDS[x_val]
    return str(x_val)


def build_y_expr(y_val):
    if isinstance(y_val, str) and y_val in Y_KEYWORDS:
        return Y_KEYWORDS[y_val]
    return str(y_val)


def add_text(input_file, text, start, end, x, y, size, color, font, shadow, output_file):
    x_expr = build_x_expr(x)
    y_expr = build_y_expr(y)

    drawtext_opts = {
        "text": text,
        "fontsize": size,
        "fontcolor": color,
        "x": x_expr,
        "y": y_expr,
        "shadowx": shadow,
        "shadowy": shadow,
        "shadowcolor": "black@0.6",
    }

    if font:
        drawtext_opts["fontfile"] = font

    if start is not None and end is not None:
        drawtext_opts["enable"] = f"between(t,{start},{end})"

    try:
        inp = ffmpeg.input(input_file)
        video = inp.video.filter("drawtext", **drawtext_opts)
        ffmpeg.output(video, inp.audio, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def burn_srt(input_file, srt_file, output_file):
    srt_path = os.path.abspath(srt_file).replace("\\", "/").replace(":", "\\:")
    try:
        inp = ffmpeg.input(input_file)
        video = inp.video.filter("subtitles", srt_path)
        ffmpeg.output(video, inp.audio, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def burn_ass(input_file, ass_file, output_file):
    ass_path = os.path.abspath(ass_file).replace("\\", "/").replace(":", "\\:")
    try:
        inp = ffmpeg.input(input_file)
        video = inp.video.filter("ass", ass_path)
        ffmpeg.output(video, inp.audio, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Text and subtitle overlay")
    parser.add_argument("--input", required=True, help="Input video file")
    parser.add_argument("--output", required=True, help="Output file path")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--text", help="Static text content")
    mode.add_argument("--srt", help="SRT subtitle file path")
    mode.add_argument("--ass", help="ASS subtitle file path")

    parser.add_argument("--start", type=float, default=None, help="Text appear time (seconds, --text mode)")
    parser.add_argument("--end", type=float, default=None, help="Text disappear time (seconds, --text mode)")
    parser.add_argument("--x", default="center", help="Horizontal position (pixel value or center, default: center)")
    parser.add_argument("--y", default="bottom", help="Vertical position (pixel value or top/center/bottom, default: bottom)")
    parser.add_argument("--size", type=int, default=48, help="Font size (default: 48)")
    parser.add_argument("--color", default="white", help="Font color (default: white)")
    parser.add_argument("--font", default=None, help="Font file path (optional)")
    parser.add_argument("--shadow", type=int, default=2, help="Shadow offset pixels (default: 2)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.text:
        add_text(
            args.input, args.text,
            args.start, args.end,
            args.x, args.y,
            args.size, args.color,
            args.font, args.shadow,
            args.output,
        )
    elif args.srt:
        if not os.path.isfile(args.srt):
            print(f"Error: SRT file does not exist: {args.srt}", file=sys.stderr)
            sys.exit(1)
        burn_srt(args.input, args.srt, args.output)
    elif args.ass:
        if not os.path.isfile(args.ass):
            print(f"Error: ASS file does not exist: {args.ass}", file=sys.stderr)
            sys.exit(1)
        burn_ass(args.input, args.ass, args.output)


if __name__ == "__main__":
    main()
