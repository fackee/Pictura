#!/usr/bin/env python3
"""
export_mp4.py - Playwright headless browser frame capture + ffmpeg MP4 synthesis

Usage:
    python3 export_mp4.py --html input.html --output output.mp4 [options]

Protocol:
    The HTML file must set `window.animationReady = true` when the first frame
    is fully rendered. The script waits up to 10s for this signal before
    starting frame capture.
"""

import argparse
import subprocess
import shutil
import sys
import os
import tempfile


def main():
    parser = argparse.ArgumentParser(
        description="Export HTML animation to MP4 via Playwright + ffmpeg"
    )
    parser.add_argument("--html", required=True, help="Path to the HTML file")
    parser.add_argument("--output", default="output.mp4", help="Output MP4 path (default: output.mp4)")
    parser.add_argument("--width", type=int, default=1920, help="Viewport width (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height (default: 1080)")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default: 24)")
    parser.add_argument("--duration", type=float, default=3.0, help="Animation duration in seconds (default: 3)")
    parser.add_argument(
        "--bg-color",
        default="#000000",
        help="Background color hex like '#000000' (default: #000000)",
    )
    parser.add_argument("--scale", type=float, default=1.0, help="Output scale factor (default: 1.0)")
    parser.add_argument(
        "--crf",
        type=int,
        default=18,
        help="ffmpeg CRF quality 0-51, lower=better (default: 18)",
    )
    parser.add_argument(
        "--preset",
        default="medium",
        choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
        help="ffmpeg encoding speed preset (default: medium)",
    )
    parser.add_argument(
        "--wait",
        type=float,
        default=0.5,
        help="Extra wait time (seconds) after animationReady before capture (default: 0.5)",
    )

    args = parser.parse_args()

    # Check ffmpeg availability
    if not shutil.which("ffmpeg"):
        print(
            "Error: ffmpeg is not installed. Install with:\n"
            "  brew install ffmpeg        (macOS)\n"
            "  apt-get install ffmpeg     (Ubuntu/Debian)\n"
            "  yum install ffmpeg         (CentOS/RHEL)",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate HTML file
    html_path = os.path.abspath(args.html)
    if not os.path.isfile(html_path):
        print(f"Error: HTML file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    # Validate output directory
    output_path = os.path.abspath(args.output)
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Validate parameters
    if args.fps < 1 or args.fps > 60:
        print("Error: --fps must be between 1 and 60", file=sys.stderr)
        sys.exit(1)
    if args.duration <= 0:
        print("Error: --duration must be positive", file=sys.stderr)
        sys.exit(1)
    if args.scale <= 0:
        print("Error: --scale must be positive", file=sys.stderr)
        sys.exit(1)
    if args.crf < 0 or args.crf > 51:
        print("Error: --crf must be between 0 and 51", file=sys.stderr)
        sys.exit(1)

    bg_color = args.bg_color.strip().lower()
    hex_color = bg_color.lstrip("#")
    if len(hex_color) != 6 or not all(c in "0123456789abcdef" for c in hex_color):
        print(f"Error: Invalid background color '{args.bg_color}'. Use hex like '#000000'", file=sys.stderr)
        sys.exit(1)
    bg_rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    # Lazy import with clear error message
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Error: playwright is not installed. Install with:\n"
            "  pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    total_frames = int(args.fps * args.duration)
    frame_interval_ms = 1000.0 / args.fps
    out_width = int(args.width * args.scale)
    out_height = int(args.height * args.scale)

    print(f"Capturing {total_frames} frames at {args.fps} FPS ({args.duration}s)...")
    print(f"Viewport: {args.width}x{args.height}, Output: {out_width}x{out_height}")
    print(f"Background: {args.bg_color}")
    print(f"CRF: {args.crf}, Preset: {args.preset}")

    # Use a temporary directory for frame PNGs
    with tempfile.TemporaryDirectory(prefix="export_mp4_") as tmp_dir:
        frame_pattern = os.path.join(tmp_dir, "frame_%06d.png")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": args.width, "height": args.height},
                device_scale_factor=1.0,
            )
            page = context.new_page()

            # Load the HTML file
            file_url = f"file://{html_path}"
            page.goto(file_url, wait_until="load")

            # Wait for animationReady signal (10s timeout)
            try:
                page.wait_for_function(
                    "() => window.animationReady === true",
                    timeout=10000,
                )
            except Exception:
                print(
                    "Warning: window.animationReady was not set to true within 10s. "
                    "Starting capture anyway. Ensure your HTML sets this signal.",
                    file=sys.stderr,
                )

            # Extra wait for rendering stabilization
            if args.wait > 0:
                page.wait_for_timeout(int(args.wait * 1000))

            # Capture frames as PNG files
            for i in range(total_frames):
                frame_path = os.path.join(tmp_dir, f"frame_{i + 1:06d}.png")
                screenshot_bytes = page.screenshot(
                    clip={"x": 0, "y": 0, "width": args.width, "height": args.height},
                    type="png",
                )
                with open(frame_path, "wb") as f:
                    f.write(screenshot_bytes)

                # Advance to next frame
                if i < total_frames - 1:
                    page.wait_for_timeout(int(frame_interval_ms))

            browser.close()

        print(f"Captured {total_frames} frames. Encoding MP4 with ffmpeg...")

        # Build ffmpeg command
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(args.fps),
            "-i", frame_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", str(args.crf),
            "-preset", args.preset,
            "-movflags", "+faststart",
        ]

        # Scale if needed
        if args.scale != 1.0:
            # Ensure even dimensions for yuv420p
            sw = out_width if out_width % 2 == 0 else out_width - 1
            sh = out_height if out_height % 2 == 0 else out_height - 1
            ffmpeg_cmd.extend(["-vf", f"scale={sw}:{sh}"])

        ffmpeg_cmd.append(output_path)

        # Run ffmpeg
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: ffmpeg failed with return code {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(1)

    file_size = os.path.getsize(output_path)
    print(f"MP4 saved: {output_path} ({_format_size(file_size)})")


def _format_size(size_bytes):
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


if __name__ == "__main__":
    main()
