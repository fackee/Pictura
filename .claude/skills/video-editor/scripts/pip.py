#!/usr/bin/env python3
"""
Picture-in-picture and keyframe animation script

Usage:
  # Basic picture-in-picture (bottom-right corner)
  python3 pip.py --background main.mp4 --overlay pip.mp4 --x 10 --y 10 --scale 0.25 --output out.mp4

  # Keyframe animation (move from left to right with fade in/out)
  python3 pip.py --background main.mp4 --overlay logo.png \
    --keyframes '[{"t":0,"x":0,"y":50,"scale":0.2,"alpha":0.0},{"t":1,"x":200,"y":50,"scale":0.2,"alpha":1.0}]' \
    --output out.mp4

Keyframe fields (all optional except t, unspecified fields carry forward from previous frame):
  t      (required)  Time point (seconds)
  x             Horizontal pixel coordinate
  y             Vertical pixel coordinate
  scale         Scale ratio relative to background width (0.0~1.0)
  alpha         Opacity (0.0~1.0)

Dependencies: pip install ffmpeg-python
"""

import argparse
import json
import os
import sys

try:
    import ffmpeg
except ImportError:
    print("Error: ffmpeg-python not installed, please run: pip install ffmpeg-python", file=sys.stderr)
    sys.exit(1)


def build_lerp_expr(keyframes, field, default):
    """
    Convert keyframe list to FFmpeg time expression (piecewise linear interpolation).
    Format: if(lt(t,t1), v1, if(lt(t,t2), v1+(v2-v1)*(t-t1)/(t2-t1), ... , vN))
    """
    # Filter keyframes containing this field, fill in default values
    pts = []
    last_val = default
    for kf in keyframes:
        val = kf.get(field, last_val)
        pts.append((kf["t"], val))
        last_val = val

    if len(pts) == 0:
        return str(default)
    if len(pts) == 1:
        return str(pts[0][1])

    # Build nested if expression
    def lerp_segment(t1, v1, t2, v2):
        if t2 == t1:
            return str(v2)
        return f"({v1}+({v2}-{v1})*(t-{t1})/({t2}-{t1}))"

    # Build from the last segment backwards
    expr = str(pts[-1][1])
    for i in range(len(pts) - 2, -1, -1):
        t1, v1 = pts[i]
        t2, v2 = pts[i + 1]
        seg = lerp_segment(t1, v1, t2, v2)
        expr = f"if(lt(t,{t1}),{v1},if(lt(t,{t2}),{seg},{expr}))"

    return expr


def apply_pip(background, overlay_file, x, y, scale, alpha, keyframes, start, end, output_file):
    bg = ffmpeg.input(background)
    bg_info = ffmpeg.probe(background)
    bg_w = int(bg_info["streams"][0]["width"])
    bg_h = int(bg_info["streams"][0]["height"])

    is_image = overlay_file.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))
    if is_image:
        ovl_input = ffmpeg.input(overlay_file, loop=1)
    else:
        ovl_input = ffmpeg.input(overlay_file)

    if keyframes:
        kfs = sorted(keyframes, key=lambda k: k["t"])

        # Validate keyframes
        for kf in kfs:
            if "t" not in kf:
                print("Error: Each keyframe must contain a 't' field", file=sys.stderr)
                sys.exit(1)

        x_expr = build_lerp_expr(kfs, "x", x)
        y_expr = build_lerp_expr(kfs, "y", y)
        scale_expr = build_lerp_expr(kfs, "scale", scale)
        alpha_expr = build_lerp_expr(kfs, "alpha", alpha)

        # Scale expression (relative to background width)
        w_expr = f"({scale_expr}*{bg_w})"
        h_expr = f"-1"  # Maintain aspect ratio

        ovl = ovl_input.video.filter("scale", w=w_expr, h=h_expr)

        # Opacity: convert to rgba via format, then adjust alpha channel
        ovl = ovl.filter("format", "rgba")
        ovl = ovl.filter("colorchannelmixer", aa=alpha_expr)

        overlay_opts = {
            "x": x_expr,
            "y": y_expr,
            "format": "auto",
        }
    else:
        # Static picture-in-picture
        w = int(scale * bg_w)
        ovl = ovl_input.video.filter("scale", w=w, h=-1)

        if alpha < 1.0:
            ovl = ovl.filter("format", "rgba")
            ovl = ovl.filter("colorchannelmixer", aa=alpha)

        overlay_opts = {
            "x": x,
            "y": y,
        }

    if start is not None or end is not None:
        t_start = start if start is not None else 0
        t_end = end if end is not None else 999999
        overlay_opts["enable"] = f"between(t,{t_start},{t_end})"

    video = ffmpeg.filter([bg.video, ovl], "overlay", **overlay_opts)

    try:
        ffmpeg.output(video, bg.audio, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Picture-in-picture and keyframe animation")
    parser.add_argument("--background", required=True, help="Background video file")
    parser.add_argument("--overlay", required=True, help="Overlay video or image file")
    parser.add_argument("--output", required=True, help="Output file path")

    parser.add_argument("--x", type=float, default=10, help="Horizontal coordinate (pixels, default: 10)")
    parser.add_argument("--y", type=float, default=10, help="Vertical coordinate (pixels, default: 10)")
    parser.add_argument("--scale", type=float, default=0.25,
                        help="Overlay scale ratio relative to background width (default: 0.25)")
    parser.add_argument("--alpha", type=float, default=1.0,
                        help="Opacity [0.0, 1.0] (default: 1.0)")

    parser.add_argument("--keyframes", default=None,
                        help='Keyframe JSON array, e.g. \'[{"t":0,"x":10,"y":10,"scale":0.25,"alpha":1.0}]\'')
    parser.add_argument("--start", type=float, default=None,
                        help="Overlay start time (seconds, default: video start)")
    parser.add_argument("--end", type=float, default=None,
                        help="Overlay end time (seconds, default: video end)")
    args = parser.parse_args()

    for path in [args.background, args.overlay]:
        if not os.path.isfile(path):
            print(f"Error: File does not exist: {path}", file=sys.stderr)
            sys.exit(1)

    if not (0.0 < args.scale <= 1.0):
        print("Error: --scale must be in (0.0, 1.0] range", file=sys.stderr)
        sys.exit(1)

    if not (0.0 <= args.alpha <= 1.0):
        print("Error: --alpha must be in [0.0, 1.0] range", file=sys.stderr)
        sys.exit(1)

    keyframes = None
    if args.keyframes:
        try:
            keyframes = json.loads(args.keyframes)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid --keyframes format: {e}", file=sys.stderr)
            sys.exit(1)
        if len(keyframes) < 2:
            print("Error: At least 2 keyframes required", file=sys.stderr)
            sys.exit(1)

    apply_pip(
        args.background, args.overlay,
        args.x, args.y, args.scale, args.alpha,
        keyframes, args.start, args.end,
        args.output,
    )


if __name__ == "__main__":
    main()
