#!/usr/bin/env python3
"""
JSON-driven video render engine.
Usage: python3 scripts/render.py --project project.json [--output output.mp4] [--base-dir /path/to/assets]
"""

import argparse
import json
import math
import os
import sys
import tempfile

# ---------------------------------------------------------------------------
# Lazy imports – checked at runtime so the error message is actionable
# ---------------------------------------------------------------------------
def _require(pkg, install_hint):
    import importlib
    try:
        return importlib.import_module(pkg)
    except ImportError:
        print(f"[error] Missing package '{pkg}'. Install with: {install_hint}", file=sys.stderr)
        sys.exit(1)


def load_dotenv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, ".env"),
        os.path.join(script_dir, "..", ".env"),
    ]
    for path in candidates:
        path = os.path.normpath(path)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            break


# ---------------------------------------------------------------------------
# System font discovery & theme-based auto-selection
# ---------------------------------------------------------------------------

def _scan_system_fonts():
    """Return list of all .ttf/.otf/.ttc font paths on the current system."""
    import glob as _glob
    import platform
    system = platform.system()
    search_dirs = []
    if system == "Darwin":
        search_dirs = [
            "/System/Library/Fonts",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts"),
            "/System/Library/Fonts/Supplemental",
        ]
    elif system == "Linux":
        search_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"),
        ]
    elif system == "Windows":
        search_dirs = [
            "C:/Windows/Fonts",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
        ]
    fonts = []
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for ext in ("*.ttf", "*.otf", "*.ttc", "*.TTF", "*.OTF", "*.TTC"):
            fonts.extend(_glob.glob(os.path.join(d, ext)))
            fonts.extend(_glob.glob(os.path.join(d, "**", ext), recursive=True))
    return sorted(set(fonts))


# Ordered candidate list per theme.
# Each entry: (priority, keyword_list_in_filename, description)
# The font selector picks the first available match for the theme.
_THEME_FONT_CANDIDATES = {
    # ---------- Chinese themes ----------
    "tech": [
        # Heiti/Sans-serif → tech feel
        ("STHeiti Medium.ttc",      "Clean heiti, tech feel"),
        ("Hiragino Sans GB.ttc",    "Hiragino sans, clear and modern"),
        ("STHeiti Light.ttc",       "Light heiti"),
        ("simhei.ttf",              "SimHei (Windows)"),
        ("NotoSansCJKsc-Bold.otf",  "Noto Sans CJK (Linux)"),
        ("NotoSansCJKsc-Regular.otf", "Noto Sans CJK Regular (Linux)"),
        ("Arial Unicode.ttf",       "Fallback Unicode"),
    ],
    "modern": [
        ("Hiragino Sans GB.ttc",    "Hiragino sans"),
        ("STHeiti Medium.ttc",      "Heiti"),
        ("NotoSansCJKsc-Bold.otf",  "Noto Sans CJK"),
        ("Arial Unicode.ttf",       "Fallback"),
    ],
    "literature": [
        # Songti/Serif → literature, documentary
        ("Songti.ttc",              "Songti, literary and classical feel"),
        ("STSong.ttf",              "STSong"),
        ("simsun.ttc",              "SimSun (Windows)"),
        ("NotoSerifCJKsc-Regular.otf", "Noto Serif CJK (Linux)"),
        ("Arial Unicode.ttf",       "Fallback"),
    ],
    "elegant": [
        ("Songti.ttc",              "Songti"),
        ("Hiragino Sans GB.ttc",    "Hiragino sans"),
        ("Arial Unicode.ttf",       "Fallback"),
    ],
    "cute": [
        # Rounded → cute, kids, vlog
        ("Hiragino Sans GB.ttc",    "Hiragino sans (rounded)"),
        ("STHeiti Medium.ttc",      "Heiti"),
        ("Arial Unicode.ttf",       "Fallback"),
    ],
    "vlog": [
        ("Hiragino Sans GB.ttc",    "Clean sans-serif"),
        ("STHeiti Medium.ttc",      "Heiti"),
        ("Arial Unicode.ttf",       "Fallback"),
    ],
    "documentary": [
        ("Songti.ttc",              "Songti, weighty feel"),
        ("Hiragino Sans GB.ttc",    "Hiragino sans"),
        ("Arial Unicode.ttf",       "Fallback"),
    ],
    "news": [
        ("STHeiti Medium.ttc",      "Heiti, news feel"),
        ("Hiragino Sans GB.ttc",    "Hiragino sans"),
        ("Arial Unicode.ttf",       "Fallback"),
    ],
    # ---------- English / default ----------
    "default": [
        ("STHeiti Medium.ttc",      "Heiti"),
        ("Hiragino Sans GB.ttc",    "Hiragino sans"),
        ("STHeiti Light.ttc",       "Light heiti"),
        ("Arial Unicode.ttf",       "Arial Unicode"),
        ("Arial Bold.ttf",          "Arial Bold"),
        ("Arial.ttf",               "Arial"),
    ],
}

# Keywords in project_name / title that trigger each theme
_THEME_KEYWORDS = {
    "tech":        ["ai", "人工智能", "科技", "技术", "tech", "digital", "数字", "算法", "编程", "代码",
                    "互联网", "网络", "区块链", "芯片", "机器人", "未来"],
    "literature":  ["文学", "诗", "故事", "散文", "小说", "历史", "纪录", "古代", "传统", "文化",
                    "documentary", "history"],
    "elegant":     ["优雅", "品质", "高端", "奢华", "艺术", "elegant", "luxury"],
    "cute":        ["可爱", "萌", "儿童", "宝宝", "cute", "kids"],
    "vlog":        ["vlog", "日常", "生活", "旅行", "travel", "lifestyle", "美食"],
    "documentary": ["纪录片", "历史", "人文", "地理", "documentary"],
    "news":        ["新闻", "资讯", "播报", "快讯", "news"],
    "modern":      ["现代", "时尚", "潮流", "fashion", "modern"],
}


def pick_font_for_theme(theme: str, all_fonts: list) -> str:
    """Return the best matching font path for the given theme."""
    # Build basename → full path index (case-insensitive)
    font_index = {}
    for path in all_fonts:
        font_index[os.path.basename(path).lower()] = path

    candidates = _THEME_FONT_CANDIDATES.get(theme, _THEME_FONT_CANDIDATES["default"])
    # Also append default fallbacks not already in list
    seen = {c[0].lower() for c in candidates}
    for c in _THEME_FONT_CANDIDATES["default"]:
        if c[0].lower() not in seen:
            candidates = candidates + [c]

    for filename, desc in candidates:
        path = font_index.get(filename.lower())
        if path:
            return path
    return ""  # caller falls back to PIL default


def detect_theme(project: dict) -> str:
    """Detect the video theme from project_name and segment titles."""
    text = project.get("project_name", "").lower()
    for seg in project.get("segments", []):
        text += " " + seg.get("title", "").lower()

    for theme, keywords in _THEME_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                return theme
    return "default"


def resolve_global_font(project: dict, settings: dict, base_dir: str) -> str:
    """
    Resolve the global_font to use for subtitles.
    Priority:
      1. Explicit path in output_settings.global_font (if file exists)
      2. Auto-select from system fonts based on project theme
      3. Empty string (PIL will use its built-in default)
    """
    explicit = settings.get("global_font", "")
    if explicit:
        path = explicit if os.path.isabs(explicit) else os.path.join(base_dir, explicit)
        if os.path.isfile(path):
            print(f"[font] Using explicit font: {path}")
            return path
        else:
            print(f"[font] Explicit font not found: {path}, falling back to auto-select")

    # Auto-select
    all_fonts = _scan_system_fonts()
    theme = detect_theme(project)
    chosen = pick_font_for_theme(theme, all_fonts)
    if chosen:
        print(f"[font] Theme='{theme}', auto-selected: {os.path.basename(chosen)}")
        return chosen

    print("[font] No suitable system font found, using PIL built-in default")
    return ""


# ---------------------------------------------------------------------------
# FX helpers (all operate on moviepy clips)
# ---------------------------------------------------------------------------

def apply_fx_in(clip, fx_in, fps):
    """Apply entrance animation to a clip."""
    if not fx_in:
        return clip
    fx_type = fx_in.get("type", "")
    duration = fx_in.get("duration", 0.3)

    if fx_type == "fade_in":
        return clip.with_effects([mpe.vfx.FadeIn(duration)])

    if fx_type == "zoom_in":
        # Scale from 0 → 1 over `duration` seconds
        w, h = clip.size

        def zoom_in_filter(get_frame, t):
            frame = get_frame(t)
            progress = min(t / duration, 1.0) if duration > 0 else 1.0
            scale = 0.1 + 0.9 * progress
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            import numpy as np
            from PIL import Image
            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            # center-pad back to original size
            result = Image.new("RGB", (w, h), (0, 0, 0))
            offset_x = (w - new_w) // 2
            offset_y = (h - new_h) // 2
            result.paste(img, (offset_x, offset_y))
            return np.array(result)

        return clip.transform(zoom_in_filter, apply_to="mask" if clip.mask else "video")

    if fx_type == "slide_in":
        direction = fx_in.get("direction", "left")
        w, h = clip.size
        canvas_w, canvas_h = w, h

        def slide_in_pos(t):
            progress = min(t / duration, 1.0) if duration > 0 else 1.0
            # ease out: progress^0.5
            eased = progress ** 0.5
            if direction == "left":
                start_x = -canvas_w
                return (int(start_x + eased * canvas_w), 0)
            elif direction == "right":
                return (int((1 - eased) * canvas_w), 0)
            elif direction == "top":
                start_y = -canvas_h
                return (0, int(start_y + eased * canvas_h))
            elif direction == "bottom":
                return (0, int((1 - eased) * canvas_h))
            return (0, 0)

        # Store slide offset; will be applied when building layer
        clip._slide_in_pos_fn = slide_in_pos
        clip._slide_in_duration = duration
        return clip

    return clip


def apply_fx_out(clip, fx_out):
    """Apply exit animation to a clip."""
    if not fx_out:
        return clip
    fx_type = fx_out.get("type", "")
    duration = fx_out.get("duration", 0.3)

    if fx_type == "fade_out":
        return clip.with_effects([mpe.vfx.FadeOut(duration)])

    return clip


def apply_fx_loop(clip, fx_loop):
    """Apply looping/continuous animation to a clip."""
    if not fx_loop:
        return clip
    fx_type = fx_loop.get("type", "")

    if fx_type == "ken_burns":
        scale_start = fx_loop.get("scale_start", 1.0)
        scale_end = fx_loop.get("scale_end", 1.05)
        w, h = clip.size
        total = clip.duration

        def kb_filter(get_frame, t):
            frame = get_frame(t)
            progress = t / total if total > 0 else 0
            scale = scale_start + (scale_end - scale_start) * progress
            new_w = int(w * scale)
            new_h = int(h * scale)
            import numpy as np
            from PIL import Image
            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            # center crop back to original
            x0 = (new_w - w) // 2
            y0 = (new_h - h) // 2
            img = img.crop((x0, y0, x0 + w, y0 + h))
            return np.array(img)

        return clip.transform(kb_filter)

    if fx_type == "pan":
        direction = fx_loop.get("direction", "up_to_down")
        speed = fx_loop.get("speed", 1.02)
        w, h = clip.size
        total = clip.duration

        def pan_filter(get_frame, t):
            frame = get_frame(t)
            import numpy as np
            from PIL import Image
            progress = t / total if total > 0 else 0
            # expand image, then pan across
            scale = speed
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            if direction in ("up_to_down", "top_to_bottom"):
                x0 = (new_w - w) // 2
                y0 = int((new_h - h) * progress)
                y0 = max(0, min(y0, new_h - h))
                img = img.crop((x0, y0, x0 + w, y0 + h))
            elif direction in ("down_to_up", "bottom_to_top"):
                x0 = (new_w - w) // 2
                y0 = int((new_h - h) * (1 - progress))
                y0 = max(0, min(y0, new_h - h))
                img = img.crop((x0, y0, x0 + w, y0 + h))
            elif direction in ("left_to_right",):
                y0 = (new_h - h) // 2
                x0 = int((new_w - w) * progress)
                x0 = max(0, min(x0, new_w - w))
                img = img.crop((x0, y0, x0 + w, y0 + h))
            else:
                x0 = (new_w - w) // 2
                y0 = (new_h - h) // 2
                img = img.crop((x0, y0, x0 + w, y0 + h))
            return np.array(img)

        return clip.transform(pan_filter)

    if fx_type == "fade_in_out_pulse":
        period = fx_loop.get("period", 3.0)
        # pulse: opacity oscillates between 0.7 and 1.0
        def pulse_filter(get_frame, t):
            import numpy as np
            frame = get_frame(t).copy()
            alpha = 0.85 + 0.15 * math.sin(2 * math.pi * t / period)
            return (frame * alpha).astype(frame.dtype)

        return clip.transform(pulse_filter)

    return clip


def apply_border(clip, border):
    """Apply border + rounded corners via PIL mask."""
    if not border:
        return clip
    width = border.get("width", 0)
    color_hex = border.get("color", "#FFFFFF")
    radius = border.get("radius", 0)

    from PIL import Image, ImageDraw
    import numpy as np

    w, h = clip.size

    def border_filter(get_frame, t):
        frame = get_frame(t)
        img = Image.fromarray(frame).convert("RGBA")

        # Create rounded-rect mask
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        r = min(radius, w // 2, h // 2)
        draw.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=r, fill=255)

        # Draw border on top
        if width > 0:
            # parse hex color
            ch = color_hex.lstrip("#")
            br, bg, bb = int(ch[0:2], 16), int(ch[2:4], 16), int(ch[4:6], 16)
            draw_full = ImageDraw.Draw(img)
            for i in range(width):
                draw_full.rounded_rectangle(
                    [(i, i), (w - 1 - i, h - 1 - i)],
                    radius=max(0, r - i),
                    outline=(br, bg, bb, 255),
                    width=1,
                )

        # Apply mask (makes corners transparent)
        img.putalpha(mask)
        return np.array(img)

    clipped = clip.transform(border_filter)
    clipped = clipped.with_effects([mpe.vfx.MaskColor(color=(0, 0, 0))])
    # Instead, keep RGBA by using image clip approach
    # Return as-is; composite will handle alpha
    return clip.transform(border_filter)


# ---------------------------------------------------------------------------
# Subtitle rendering
# ---------------------------------------------------------------------------

def make_subtitle_clip(text, style, canvas_w, canvas_h, duration, global_font):
    """
    Create a subtitle ImageClip centered near the bottom of the canvas.
    Automatically wraps text to fit within the canvas width (with margins).

    Style fields (all optional):
      font_size      int    46       Font size (px)
      color          str   "#FFFFFF" Text color (foreground)
      stroke_color   str   "#000000" Stroke color (outline)
      stroke_width   int    3        Stroke width (px), 0 = disabled
      bottom_margin  int    120      Distance from bottom of frame (px)
      font           str   global_font Font file path
    """
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    import textwrap

    font_size     = style.get("font_size", 46)
    color_hex     = style.get("color", "#FFFFFF")
    stroke_color  = style.get("stroke_color", "#000000")
    stroke_width  = int(style.get("stroke_width", 3))
    bottom_margin = int(style.get("bottom_margin", 120))
    font_path     = style.get("font", global_font)

    # Horizontal margin on each side for text wrapping
    side_margin = int(canvas_w * 0.06)
    max_text_w = canvas_w - 2 * side_margin

    def hex_to_rgba(h, default_alpha=255):
        h = h.lstrip("#")
        if len(h) == 8:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), default_alpha)

    fg_rgba  = hex_to_rgba(color_hex)
    st_rgba  = hex_to_rgba(stroke_color)

    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size) if (font_path and os.path.isfile(font_path)) \
               else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Word-wrap text to fit within max_text_w
    def wrap_text(text, font, max_width, draw, stroke_width):
        """Wrap text into lines that fit within max_width pixels."""
        lines = []
        # Split by explicit newlines first
        for paragraph in text.split('\n'):
            if not paragraph:
                lines.append("")
                continue
            words = paragraph.split(' ')
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                bbox = draw.textbbox((0, 0), test_line, font=font, stroke_width=stroke_width)
                line_w = bbox[2] - bbox[0]
                if line_w <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    # Handle single word wider than max_width: force it
                    current_line = word
            if current_line:
                lines.append(current_line)
        return lines

    dummy = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy)

    lines = wrap_text(text, font, max_text_w, dummy_draw, stroke_width)

    # Measure total text block size
    line_heights = []
    line_widths = []
    for line in lines:
        if not line:
            line_heights.append(font_size)
            line_widths.append(0)
            continue
        bbox = dummy_draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    line_spacing = int(font_size * 0.25)
    total_text_w = max(line_widths) if line_widths else 0
    total_text_h = sum(line_heights) + line_spacing * (len(lines) - 1)

    # Canvas-size transparent image
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Text block anchor: horizontally centered, near bottom
    block_x = (canvas_w - total_text_w) // 2
    block_y = canvas_h - bottom_margin - total_text_h

    # Render each line
    y_offset = block_y
    for i, line in enumerate(lines):
        line_w = line_widths[i]
        tx = (canvas_w - line_w) // 2
        ty = y_offset
        draw.text((tx, ty), line, font=font, fill=fg_rgba, stroke_width=stroke_width, stroke_fill=st_rgba)
        y_offset += line_heights[i] + line_spacing

    frame = np.array(img)

    from moviepy import ImageClip
    sub_clip = ImageClip(frame[:, :, :3], duration=duration)

    # Fix: convert uint8 alpha (0~255) to float (0.0~1.0) for MoviePy mask
    alpha_data = frame[:, :, 3].astype(np.float64) / 255.0
    mask_clip = ImageClip(alpha_data, is_mask=True, duration=duration)
    return sub_clip.with_mask(mask_clip)


# ---------------------------------------------------------------------------
# Core: build one segment
# ---------------------------------------------------------------------------

def build_segment(seg, settings, base_dir):
    """Return (video_composite, audio_composite) for a single segment."""
    from moviepy import (
        ImageClip, VideoFileClip, CompositeVideoClip, CompositeAudioClip,
        AudioFileClip, concatenate_audioclips,
    )
    import numpy as np

    seg_duration = float(seg["duration"])
    canvas_w = settings["resolution"]["width"]
    canvas_h = settings["resolution"]["height"]
    fps = settings.get("fps", 30)
    global_font = settings.get("global_font", "")
    # Resolve font relative to base_dir
    if global_font and not os.path.isabs(global_font):
        global_font = os.path.join(base_dir, global_font)

    # ---------- Visual track ----------
    visual_layers = sorted(seg.get("visual_track", []), key=lambda l: l.get("z_index", 0))
    video_clips = []

    for layer in visual_layers:
        ltype = layer.get("type", "image")
        fpath = os.path.join(base_dir, layer["file_path"])
        z = layer.get("z_index", 0)
        start = float(layer.get("start_time", 0.0))
        end = float(layer.get("end_time", seg_duration))
        layer_dur = end - start
        layout = layer.get("layout", {})
        lx = layout.get("x", 0)
        ly = layout.get("y", 0)
        lw = layout.get("width", canvas_w)
        lh = layout.get("height", canvas_h)
        volume = float(layer.get("volume", 1.0))
        border = layer.get("border")
        fx = layer.get("fx", {})

        if not os.path.isfile(fpath):
            print(f"[warn] file not found: {fpath}", file=sys.stderr)
            continue

        # Load clip
        if ltype == "image":
            raw = ImageClip(fpath, duration=layer_dur)
        else:  # video
            trim = layer.get("source_trim", {})
            t_start = float(trim.get("start", 0.0))
            t_end = trim.get("end")
            raw = VideoFileClip(fpath).without_audio() if volume == 0 else VideoFileClip(fpath)
            if t_end is not None:
                raw = raw.subclipped(t_start, float(t_end))
            else:
                raw = raw.subclipped(t_start)
            # Loop if layer_dur > source duration
            if raw.duration < layer_dur:
                loops = math.ceil(layer_dur / raw.duration)
                from moviepy import concatenate_videoclips
                raw = concatenate_videoclips([raw] * loops)
            raw = raw.subclipped(0, layer_dur)

        # Resize to layout dimensions
        clip = raw.resized((lw, lh))

        # Apply border (must come before FX so shape is established)
        if border:
            clip = apply_border_moviepy(clip, border)

        # Apply FX
        fx_in = fx.get("in")
        fx_out = fx.get("out")
        fx_loop = fx.get("loop")
        fx_static = fx.get("type") == "static"

        if not fx_static:
            if fx_loop:
                clip = apply_fx_loop(clip, fx_loop)
            if fx_in:
                clip = apply_fx_in(clip, fx_in, fps)
            if fx_out:
                clip = apply_fx_out(clip, fx_out)

        # Position in canvas (start_time offset within segment)
        # Handle slide_in position override
        if hasattr(clip, '_slide_in_pos_fn'):
            pos_fn = clip._slide_in_pos_fn
            slide_dur = clip._slide_in_duration

            def make_pos(px, py, pfn, pdur):
                def pos(t):
                    if t < pdur:
                        dx, dy = pfn(t)
                        return (px + dx, py + dy)
                    return (px, py)
                return pos

            position = make_pos(lx, ly, pos_fn, slide_dur)
        else:
            position = (lx, ly)

        clip = clip.with_start(start).with_position(position)
        video_clips.append(clip)

    # Compose segment video
    if video_clips:
        seg_video = CompositeVideoClip(video_clips, size=(canvas_w, canvas_h)).with_duration(seg_duration)
    else:
        # Black frame fallback
        import numpy as np
        black = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        seg_video = ImageClip(black, duration=seg_duration)

    # ---------- Subtitle track (overlay on video) ----------
    audio_track = seg.get("audio_track", {})
    narrations = audio_track.get("narration", [])
    subtitle_clips = []

    default_sub_style = {
        "font_size": 46,
        "color": "#FFFFFF",
        "stroke_color": "#000000",
        "stroke_width": 3,
        "bottom_margin": 120,
    }

    for narr in narrations:
        subtitle = narr.get("subtitle")
        if not subtitle:
            continue
        narr_start = float(narr.get("start_time", 0.0))
        # Determine narration duration: end_time > source_trim > audio file duration > remainder of segment
        narr_end = narr.get("end_time")
        if narr_end is not None:
            narr_dur = float(narr_end) - narr_start
        else:
            trim = narr.get("source_trim", {})
            t_start = float(trim.get("start", 0.0))
            t_end = trim.get("end")
            if t_end is not None:
                narr_dur = float(t_end) - t_start
            else:
                # Try to get duration from the actual audio file
                narr_dur = None
                narr_file = narr.get("file_path")
                if narr_file:
                    narr_fpath = os.path.join(base_dir, narr_file)
                    if os.path.isfile(narr_fpath):
                        try:
                            from moviepy import AudioFileClip as _AFC
                            _a = _AFC(narr_fpath)
                            narr_dur = _a.duration
                            _a.close()
                        except Exception:
                            pass
                if narr_dur is None:
                    narr_dur = seg_duration - narr_start

        text = subtitle.get("text", "")
        style = dict(default_sub_style)
        style.update(subtitle.get("style_override", {}))
        # Merge global_font into style
        if "font" not in style and global_font:
            style["font"] = global_font

        sub_clip = make_subtitle_clip(text, style, canvas_w, canvas_h, narr_dur, global_font)
        sub_clip = sub_clip.with_start(narr_start)
        subtitle_clips.append(sub_clip)

    if subtitle_clips:
        all_clips = [seg_video] + subtitle_clips
        seg_video = CompositeVideoClip(all_clips, size=(canvas_w, canvas_h)).with_duration(seg_duration)

    # ---------- Audio track ----------
    audio_clips = []

    # Narration
    for narr in narrations:
        fpath = os.path.join(base_dir, narr["file_path"])
        if not os.path.isfile(fpath):
            print(f"[warn] narration not found: {fpath}", file=sys.stderr)
            continue
        trim = narr.get("source_trim", {})
        t_start = float(trim.get("start", 0.0))
        t_end = trim.get("end")
        narr_start = float(narr.get("start_time", 0.0))
        vol = float(narr.get("volume", 1.0))

        a = AudioFileClip(fpath)
        if t_end is not None:
            a = a.subclipped(t_start, float(t_end))
        else:
            a = a.subclipped(t_start)
        if vol != 1.0:
            a = a.with_volume_scaled(vol)
        a = a.with_start(narr_start)
        audio_clips.append(a)

    # BGM
    for bgm in audio_track.get("bgm", []):
        fpath = os.path.join(base_dir, bgm["file_path"])
        if not os.path.isfile(fpath):
            print(f"[warn] bgm not found: {fpath}", file=sys.stderr)
            continue
        trim = bgm.get("source_trim", {})
        t_start = float(trim.get("start", 0.0))
        t_end = trim.get("end")
        bgm_start = float(bgm.get("start_time", 0.0))
        vol = float(bgm.get("volume", 0.3))
        fx_bgm = bgm.get("fx", {})

        a = AudioFileClip(fpath)
        if t_end is not None:
            a = a.subclipped(t_start, float(t_end))
        else:
            a = a.subclipped(t_start)
        if vol != 1.0:
            a = a.with_volume_scaled(vol)

        fade_in_dur = fx_bgm.get("fade_in", 0)
        fade_out_dur = fx_bgm.get("fade_out", 0)
        if fade_in_dur > 0:
            a = a.with_effects([mpe.afx.AudioFadeIn(fade_in_dur)])
        if fade_out_dur > 0:
            a = a.with_effects([mpe.afx.AudioFadeOut(fade_out_dur)])

        a = a.with_start(bgm_start)
        audio_clips.append(a)

    # SFX
    for sfx in audio_track.get("sfx", []):
        fpath = os.path.join(base_dir, sfx["file_path"])
        if not os.path.isfile(fpath):
            print(f"[warn] sfx not found: {fpath}", file=sys.stderr)
            continue
        sfx_start = float(sfx.get("start_time", 0.0))
        vol = float(sfx.get("volume", 1.0))

        a = AudioFileClip(fpath)
        if vol != 1.0:
            a = a.with_volume_scaled(vol)
        a = a.with_start(sfx_start)
        audio_clips.append(a)

    if audio_clips:
        seg_audio = CompositeAudioClip(audio_clips).with_duration(seg_duration)
        seg_video = seg_video.with_audio(seg_audio)

    return seg_video


def apply_border_moviepy(clip, border):
    """Apply rounded border using PIL, returns clip with border drawn."""
    from PIL import Image, ImageDraw
    import numpy as np

    width_px = border.get("width", 0)
    color_hex = border.get("color", "#FFFFFF")
    radius = border.get("radius", 0)
    w, h = clip.size

    ch = color_hex.lstrip("#")
    br, bg, bb = int(ch[0:2], 16), int(ch[2:4], 16), int(ch[4:6], 16)
    r = min(radius, w // 2, h // 2)

    def border_filter(get_frame, t):
        frame = get_frame(t).copy()
        img = Image.fromarray(frame)

        if r > 0:
            # Create rounded mask
            mask = Image.new("L", (w, h), 0)
            md = ImageDraw.Draw(mask)
            md.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=r, fill=255)
            img_rgba = img.convert("RGBA")
            img_rgba.putalpha(mask)
            # Composite over black background
            bg_img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
            bg_img.paste(img_rgba, (0, 0), img_rgba)
            img = bg_img.convert("RGB")

        if width_px > 0:
            draw = ImageDraw.Draw(img)
            for i in range(width_px):
                rr = max(0, r - i)
                draw.rounded_rectangle([(i, i), (w - 1 - i, h - 1 - i)],
                                        radius=rr, outline=(br, bg, bb), width=1)

        return np.array(img)

    return clip.transform(border_filter)


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------

def render(project_path, output_path, base_dir=None):
    with open(project_path, encoding="utf-8") as f:
        project = json.load(f)

    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(project_path))

    settings = project.get("output_settings", {})
    if not settings.get("resolution"):
        settings["resolution"] = {"width": 1080, "height": 1920}

    # Resolve font: explicit path → system auto-select by theme
    settings["global_font"] = resolve_global_font(project, settings, base_dir)

    fps = settings.get("fps", 30)
    video_codec = settings.get("video_codec", "libx264")
    audio_codec = settings.get("audio_codec", "aac")

    from moviepy import concatenate_videoclips

    segments = project.get("segments", [])
    if not segments:
        print("[error] No segments found in project JSON.", file=sys.stderr)
        sys.exit(1)

    seg_clips = []
    for i, seg in enumerate(segments):
        sid = seg.get("segment_id", f"seg_{i+1:03d}")
        print(f"  Building segment {sid} ({seg.get('title', '')})")
        clip = build_segment(seg, settings, base_dir)
        seg_clips.append(clip)

    print("  Concatenating segments...")
    final = concatenate_videoclips(seg_clips, method="compose")

    print(f"  Writing output to {output_path} ...")
    final.write_videofile(
        output_path,
        fps=fps,
        codec=video_codec,
        audio_codec=audio_codec,
        logger="bar",
    )
    print(f"[done] {output_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    load_dotenv()

    # Import moviepy after dotenv
    global mpe
    mpe = _require("moviepy", "pip install moviepy pillow")
    import moviepy as mpe_module
    mpe = mpe_module

    # Also ensure PIL is available
    _require("PIL", "pip install pillow")

    parser = argparse.ArgumentParser(description="JSON-driven video render engine")
    parser.add_argument("--project", required=True, help="Path to project JSON file")
    parser.add_argument("--output", default=None, help="Output video file path (default: <project_name>.mp4)")
    parser.add_argument("--base-dir", default=None,
                        help="Base directory for resolving relative file paths (default: project file directory)")
    args = parser.parse_args()

    project_path = os.path.abspath(args.project)
    if not os.path.isfile(project_path):
        print(f"[error] Project file not found: {project_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = args.output
    else:
        # derive output name from project
        with open(project_path, encoding="utf-8") as f:
            proj = json.load(f)
        name = proj.get("project_name", "output").replace(" ", "_")
        output_path = os.path.join(os.path.dirname(project_path), f"{name}.mp4")

    base_dir = args.base_dir or os.path.dirname(project_path)

    print(f"[render] Project: {project_path}")
    print(f"[render] Base dir: {base_dir}")
    print(f"[render] Output: {output_path}")

    render(project_path, output_path, base_dir)


if __name__ == "__main__":
    main()
