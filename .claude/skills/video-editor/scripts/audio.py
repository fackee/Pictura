#!/usr/bin/env python3
"""
Audio processing script: detach, mix, denoise, fade in/out

Usage:
  # Detach audio and video
  python3 audio.py --input in.mp4 --detach --output-video silent.mp4 --output-audio audio.mp3

  # Mix in background music
  python3 audio.py --input in.mp4 --bgm bgm.mp3 --bgm-volume 0.3 --output out.mp4

  # Noise reduction
  python3 audio.py --input in.mp4 --denoise --output out.mp4

  # Fade in/out
  python3 audio.py --input in.mp4 --fade-in 2.0 --fade-out 3.0 --output out.mp4

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


def get_duration(path):
    try:
        info = ffmpeg.probe(path)
        return float(info["format"]["duration"])
    except Exception as e:
        print(f"Error: Unable to read file duration {path}: {e}", file=sys.stderr)
        sys.exit(1)


def detach_audio(input_file, output_video, output_audio):
    """Separate video and audio into two independent files."""
    inp = ffmpeg.input(input_file)
    try:
        # Output silent video
        ffmpeg.output(inp.video, output_video, an=None).overwrite_output().run(quiet=True)
        # Output audio
        ffmpeg.output(inp.audio, output_audio).overwrite_output().run(quiet=True)
        print(f"Video (silent): {output_video}")
        print(f"Audio: {output_audio}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def process_audio(input_file, bgm_file, bgm_volume, main_volume,
                  denoise, fade_in, fade_out, output_file):
    """Comprehensive audio processing: mixing + denoising + fade in/out."""
    duration = get_duration(input_file)
    inp = ffmpeg.input(input_file)
    audio = inp.audio

    # Volume adjustment
    if main_volume != 1.0:
        audio = audio.filter("volume", main_volume)

    # Noise reduction
    if denoise:
        audio = audio.filter("afftdn", nr=12, nf=-50, tn=1)

    # Fade in
    if fade_in and fade_in > 0:
        audio = audio.filter("afade", t="in", ss=0, d=fade_in)

    # Fade out
    if fade_out and fade_out > 0:
        fade_start = max(duration - fade_out, 0)
        audio = audio.filter("afade", t="out", st=fade_start, d=fade_out)

    # Mix in background music
    if bgm_file:
        bgm = ffmpeg.input(bgm_file, stream_loop=-1, t=duration).audio
        if bgm_volume != 1.0:
            bgm = bgm.filter("volume", bgm_volume)
        audio = ffmpeg.filter([audio, bgm], "amix", inputs=2, duration="first")

    try:
        ffmpeg.output(inp.video, audio, output_file).overwrite_output().run(quiet=True)
        print(f"Done: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: FFmpeg execution failed\n{e.stderr.decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Audio processing: detach, mix, denoise, fade in/out")
    parser.add_argument("--input", required=True, help="Input video file")
    parser.add_argument("--bgm", default=None, help="Background music file path")
    parser.add_argument("--bgm-volume", type=float, default=0.3,
                        help="Background music volume ratio (0.0~1.0, default: 0.3)")
    parser.add_argument("--main-volume", type=float, default=1.0,
                        help="Main volume ratio (0.0~2.0, default: 1.0)")
    parser.add_argument("--detach", action="store_true",
                        help="Detach audio and video (use with --output-video / --output-audio)")
    parser.add_argument("--output-video", default=None, help="Detach mode: silent video output path")
    parser.add_argument("--output-audio", default=None, help="Detach mode: audio output path")
    parser.add_argument("--denoise", action="store_true", help="Enable noise reduction")
    parser.add_argument("--fade-in", type=float, default=None, help="Audio fade-in duration (seconds)")
    parser.add_argument("--fade-out", type=float, default=None, help="Audio fade-out duration (seconds)")
    parser.add_argument("--output", default=None, help="Output file path (required in non-detach mode)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.bgm and not os.path.isfile(args.bgm):
        print(f"Error: BGM file does not exist: {args.bgm}", file=sys.stderr)
        sys.exit(1)

    if args.detach:
        ov = args.output_video or "output_silent.mp4"
        oa = args.output_audio or "output_audio.mp3"
        detach_audio(args.input, ov, oa)
    else:
        if not args.output:
            print("Error: --output must be provided in non-detach mode", file=sys.stderr)
            sys.exit(1)
        process_audio(
            args.input,
            args.bgm,
            args.bgm_volume,
            args.main_volume,
            args.denoise,
            args.fade_in,
            args.fade_out,
            args.output,
        )


if __name__ == "__main__":
    main()
