#!/usr/bin/env python3
"""
Video transition effects script

Usage:
  python3 transition.py --inputs a.mp4 b.mp4 --type fade --duration 1.0 --output out.mp4
  python3 transition.py --inputs a.mp4 b.mp4 c.mp4 --type fadeblack --duration 0.5 --output out.mp4

Supported transition types:
  fade, fadeblack, fadewhite, dissolve,
  wipeleft, wiperight, wipeup, wipedown,
  slideleft, slideright, slideup, slidedown,
  circleopen, circleclose, zoomin

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

VALID_TRANSITIONS = {
    "fade", "fadeblack", "fadewhite", "dissolve",
    "wipeleft", "wiperight", "wipeup", "wipedown",
    "slideleft", "slideright", "slideup", "slidedown",
    "circleopen", "circleclose", "zoomin",
}


def get_duration(path):
    try:
        info = ffmpeg.probe(path)
        return float(info["format"]["duration"])
    except Exception as e:
        print(f"Error: Unable to read file duration {path}: {e}", file=sys.stderr)
        sys.exit(1)


def apply_transitions(input_files, transition_type, duration, output_file):
    """
    Connect multiple video files sequentially via xfade transitions.
    xfade offset = previous segment duration - transition duration.
    """
    durations = [get_duration(f) for f in input_files]

    inputs = [ffmpeg.input(f) for f in input_files]

    # First video's video/audio streams
    current_v = inputs[0].video
    current_a = inputs[0].audio
    accumulated = 0.0

    for i in range(1, len(inputs)):
        accumulated += durations[i - 1]
        offset = max(accumulated - duration, 0)

        # Video transition
        current_v = ffmpeg.filter(
            [current_v, inputs[i].video],
            "xfade",
            transition=transition_type,
            duration=duration,
            offset=offset,
        )

        # Audio crossfade
        current_a = ffmpeg.filter(
            [current_a, inputs[i].audio],
            "acrossfade",
            d=duration,
        )

        # Subtract overlap for next iteration's accumulated duration
        accumulated -= duration

    try:
        ffmpeg.output(current_v, current_a, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Video transition effects")
    parser.add_argument("--inputs", nargs="+", required=True, metavar="FILE",
                        help="Input video files in order (at least 2)")
    parser.add_argument("--type", default="fade", dest="transition_type",
                        help=f"Transition type (default: fade), options: {', '.join(sorted(VALID_TRANSITIONS))}")
    parser.add_argument("--duration", type=float, default=1.0,
                        help="Transition duration (seconds, default: 1.0)")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    if len(args.inputs) < 2:
        print("Error: At least 2 input files required", file=sys.stderr)
        sys.exit(1)

    for f in args.inputs:
        if not os.path.isfile(f):
            print(f"Error: File does not exist: {f}", file=sys.stderr)
            sys.exit(1)

    if args.transition_type not in VALID_TRANSITIONS:
        print(f"Error: Unsupported transition type '{args.transition_type}'", file=sys.stderr)
        print(f"Available options: {', '.join(sorted(VALID_TRANSITIONS))}", file=sys.stderr)
        sys.exit(1)

    if args.duration <= 0:
        print("Error: Transition duration must be greater than 0", file=sys.stderr)
        sys.exit(1)

    apply_transitions(args.inputs, args.transition_type, args.duration, args.output)


if __name__ == "__main__":
    main()
