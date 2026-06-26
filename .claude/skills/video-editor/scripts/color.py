#!/usr/bin/env python3
"""
Color correction and filter preset script

Usage:
  # Basic color adjustment
  python3 color.py --input in.mp4 --brightness 0.1 --contrast 1.2 --saturation 1.3 --output out.mp4

  # Apply built-in preset
  python3 color.py --input in.mp4 --preset cinematic --output out.mp4

  # Apply custom LUT
  python3 color.py --input in.mp4 --lut my.cube --output out.mp4

Built-in presets: vintage, cinematic, warm, cool, bw, vivid, flat

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


# Built-in presets: mapped to FFmpeg filter parameters
PRESETS = {
    "cinematic": {
        "eq": {"brightness": -0.05, "contrast": 1.15, "saturation": 0.85},
        "curves": "cross_process",
    },
    "vintage": {
        "eq": {"brightness": -0.03, "contrast": 1.05, "saturation": 0.65},
        "curves": "vintage",
    },
    "warm": {
        "eq": {"saturation": 1.1},
        "colortemperature": {"temperature": 5000},
    },
    "cool": {
        "eq": {"saturation": 0.95},
        "colortemperature": {"temperature": 8000},
    },
    "bw": {
        "eq": {"saturation": 0.0},
    },
    "vivid": {
        "eq": {"contrast": 1.1, "saturation": 1.6},
    },
    "flat": {
        "eq": {"contrast": 0.85, "saturation": 0.8},
    },
}


def apply_color(input_file, brightness, contrast, saturation, temperature, preset, lut_file, output_file):
    inp = ffmpeg.input(input_file)
    video = inp.video

    if preset:
        if preset not in PRESETS:
            print(f"Error: Unknown preset '{preset}', available: {', '.join(PRESETS.keys())}", file=sys.stderr)
            sys.exit(1)
        p = PRESETS[preset]

        if "eq" in p:
            eq_params = p["eq"]
            video = video.filter("eq", **eq_params)

        if "curves" in p:
            video = video.filter("curves", preset=p["curves"])

        if "colortemperature" in p:
            video = video.filter("colortemperature", **p["colortemperature"])

    else:
        # Individual parameter color adjustment
        eq_params = {}
        if brightness != 0.0:
            eq_params["brightness"] = brightness
        if contrast != 1.0:
            eq_params["contrast"] = contrast
        if saturation != 1.0:
            eq_params["saturation"] = saturation

        if eq_params:
            video = video.filter("eq", **eq_params)

        if temperature != 0:
            # Color temperature: >0 warmer (lower Kelvin), <0 cooler (higher Kelvin)
            # FFmpeg colortemperature uses Kelvin, neutral is ~6500K
            kelvin = 6500 - temperature * 30
            kelvin = max(1000, min(40000, int(kelvin)))
            video = video.filter("colortemperature", temperature=kelvin)

    if lut_file:
        if not os.path.isfile(lut_file):
            print(f"Error: LUT file does not exist: {lut_file}", file=sys.stderr)
            sys.exit(1)
        video = video.filter("lut3d", file=lut_file)

    try:
        ffmpeg.output(video, inp.audio, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Color correction and filter presets")
    parser.add_argument("--input", required=True, help="Input video file")
    parser.add_argument("--output", required=True, help="Output file path")

    parser.add_argument("--brightness", type=float, default=0.0,
                        help="Brightness adjustment [-1.0, 1.0] (default: 0)")
    parser.add_argument("--contrast", type=float, default=1.0,
                        help="Contrast [0.0, 2.0] (default: 1.0)")
    parser.add_argument("--saturation", type=float, default=1.0,
                        help="Saturation [0.0, 3.0] (default: 1.0)")
    parser.add_argument("--temperature", type=int, default=0,
                        help="Color temperature shift [-100, 100], positive=warm, negative=cool (default: 0)")

    parser.add_argument("--preset", default=None,
                        help=f"Built-in preset: {', '.join(PRESETS.keys())}")
    parser.add_argument("--lut", default=None, help="Custom .cube LUT file path")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    if not (-1.0 <= args.brightness <= 1.0):
        print("Error: --brightness must be in [-1.0, 1.0] range", file=sys.stderr)
        sys.exit(1)
    if not (0.0 <= args.contrast <= 2.0):
        print("Error: --contrast must be in [0.0, 2.0] range", file=sys.stderr)
        sys.exit(1)
    if not (0.0 <= args.saturation <= 3.0):
        print("Error: --saturation must be in [0.0, 3.0] range", file=sys.stderr)
        sys.exit(1)
    if not (-100 <= args.temperature <= 100):
        print("Error: --temperature must be in [-100, 100] range", file=sys.stderr)
        sys.exit(1)

    apply_color(
        args.input,
        args.brightness, args.contrast, args.saturation, args.temperature,
        args.preset, args.lut,
        args.output,
    )


if __name__ == "__main__":
    main()
