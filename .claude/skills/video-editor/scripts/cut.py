#!/usr/bin/env python3
"""
Video cutting and concatenation script

Usage:
  # Extract multiple segments from a single video and concatenate
  python3 cut.py --input input.mp4 --segments '[{"start":0,"end":5},{"start":10,"end":20}]' --output out.mp4

  # Concatenate multiple video files directly
  python3 cut.py --inputs a.mp4 b.mp4 c.mp4 --output out.mp4

Dependencies: pip install ffmpeg-python
"""

import argparse
import json
import os
import sys
import tempfile

try:
    import ffmpeg
except ImportError:
    print("Error: ffmpeg-python not installed, please run: pip install ffmpeg-python", file=sys.stderr)
    sys.exit(1)


def probe_duration(path):
    try:
        info = ffmpeg.probe(path)
        return float(info["format"]["duration"])
    except Exception as e:
        print(f"Error: Unable to read file info {path}: {e}", file=sys.stderr)
        sys.exit(1)


def cut_segments(input_file, segments, output_file):
    """Extract multiple segments from a single video and concatenate them in order."""
    if not segments:
        print("Error: --segments cannot be empty", file=sys.stderr)
        sys.exit(1)

    clips_v = []
    clips_a = []
    for i, seg in enumerate(segments):
        start = seg.get("start", 0)
        end = seg.get("end")
        if end is None:
            print(f"Error: segment {i} missing 'end' field", file=sys.stderr)
            sys.exit(1)
        if end <= start:
            print(f"Error: segment {i} end ({end}) must be greater than start ({start})", file=sys.stderr)
            sys.exit(1)

        duration = end - start
        inp = ffmpeg.input(input_file, ss=start, t=duration)
        clips_v.append(inp.video)
        clips_a.append(inp.audio)

    concat = ffmpeg.concat(*[val for pair in zip(clips_v, clips_a) for val in pair], v=1, a=1)
    out_v = concat.video
    out_a = concat.audio

    try:
        ffmpeg.output(out_v, out_a, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def concat_files(input_files, output_file):
    """Concatenate multiple video files directly."""
    # When using concat demuxer (requires consistent encoding), a file list is needed
    # For compatibility with different encodings, use filter_complex concat
    streams_v = []
    streams_a = []
    for f in input_files:
        inp = ffmpeg.input(f)
        streams_v.append(inp.video)
        streams_a.append(inp.audio)

    n = len(input_files)
    interleaved = [val for pair in zip(streams_v, streams_a) for val in pair]
    concat = ffmpeg.concat(*interleaved, v=1, a=1)

    try:
        ffmpeg.output(concat.video, concat.audio, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Video cutting and concatenation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Single input video file (use with --segments)")
    group.add_argument("--inputs", nargs="+", metavar="FILE", help="Multiple video files (concatenate in order)")
    parser.add_argument("--segments", help='Segment list JSON, e.g. \'[{"start":0,"end":5}]\' (requires --input)')
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    if args.input:
        if not args.segments:
            print("Error: --segments must be provided when using --input", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(args.input):
            print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
            sys.exit(1)
        try:
            segments = json.loads(args.segments)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid --segments format: {e}", file=sys.stderr)
            sys.exit(1)
        cut_segments(args.input, segments, args.output)

    elif args.inputs:
        for f in args.inputs:
            if not os.path.isfile(f):
                print(f"Error: Input file does not exist: {f}", file=sys.stderr)
                sys.exit(1)
        if len(args.inputs) < 2:
            print("Error: --inputs requires at least 2 files", file=sys.stderr)
            sys.exit(1)
        concat_files(args.inputs, args.output)


if __name__ == "__main__":
    main()
