---
name: video-editor
description: JSON template-driven video rendering engine with multi-layer compositing (z_index stacking), entrance/exit effects (slide_in/zoom_in/fade), continuous animations (ken_burns/pan/pulse), three-track audio (narration/BGM/SFX), deep subtitle binding and style overrides. Use this skill when rendering a JSON project template into a video.
compatibility: Requires Python 3.9+, install dependencies: pip install moviepy pillow; system needs FFmpeg
metadata:
  author: SkillDeveloper
  version: "2.0"
allowed-tools: Bash(python3:*) Bash(pip:*) Bash(ffmpeg:*)
---

# Video Rendering Engine (JSON Template-Driven)

Describe the entire video structure through a JSON project file and render with a single command:

```bash
python3 scripts/render.py --project project.json --output output.mp4
```

## Install Dependencies

```bash
pip install moviepy pillow
# macOS install FFmpeg
brew install ffmpeg
# Ubuntu
sudo apt install ffmpeg
```

## Usage

```bash
python3 scripts/render.py \
  --project /path/to/project.json \
  --output  /path/to/output.mp4 \
  --base-dir /path/to/assets   # optional, defaults to project.json directory
```

| Parameter | Description |
|-----------|-------------|
| `--project` | JSON project file path (required) |
| `--output` | Output video path (default: project_name.mp4 in the project file directory) |
| `--base-dir` | Asset root directory, all `file_path` values are resolved relative to this |

---

## JSON Project Template Structure

For the complete schema and field descriptions, see [references/template-schema.md](references/template-schema.md).

### Top-Level Structure

```json
{
  "project_name": "my-video",
  "version": "2.0.0",
  "output_settings": { ... },
  "segments": [ ... ]
}
```

### output_settings

```json
{
  "resolution": { "width": 1080, "height": 1920 },
  "fps": 30,
  "video_codec": "libx264",
  "audio_codec": "aac",
  "global_font": "assets/fonts/SourceHanSans-Bold.ttf"
}
```

- `global_font`: Global subtitle font path (relative to base-dir). **Optional**: When omitted or the file doesn't exist, the renderer automatically scans system fonts and infers the theme from the project name/segment titles (tech/literature/vlog, etc.), selecting the best matching font (e.g., tech → sans-serif/heiti, literature → serif/songti).

### segments Array

Each segment is an independent time block; internal times are **offsets relative to the segment start** (0 ~ duration).

```json
{
  "segment_id": "seg_001",
  "title": "Opening",
  "duration": 15.0,
  "visual_track": [ ... ],
  "audio_track": { "narration": [...], "bgm": [...], "sfx": [...] }
}
```

---

## visual_track (Visual Layers)

Layers are stacked by `z_index` from low to high (lower values are at the bottom).

```json
{
  "id": "layer_id",
  "type": "image",          // "image" or "video"
  "file_path": "images/bg.png",
  "z_index": 1,
  "start_time": 0.0,        // relative to segment start (seconds)
  "end_time": 15.0,
  "layout": { "x": 0, "y": 0, "width": 1080, "height": 1920 },
  "volume": 0.0,            // only for video, 0 = mute
  "border": { "width": 4, "color": "#00FFFF", "radius": 250 },
  "source_trim": { "start": 0.0, "end": 12.0 },  // video only
  "fx": {
    "in":   { "type": "slide_in", "direction": "left", "duration": 0.5 },
    "out":  { "type": "fade_out", "duration": 0.4 },
    "loop": { "type": "ken_burns", "scale_start": 1.0, "scale_end": 1.05 }
  }
}
```

### FX Effects List

| Category | type | Parameters |
|----------|------|------------|
| Entrance | `slide_in` | `direction`: left/right/top/bottom, `duration` (seconds) |
| Entrance | `zoom_in` | `duration` (seconds) |
| Entrance | `fade_in` | `duration` (seconds) |
| Exit | `fade_out` | `duration` (seconds) |
| Loop | `ken_burns` | `scale_start`, `scale_end` (slow dolly zoom) |
| Loop | `pan` | `direction`: up_to_down/down_to_up/left_to_right, `speed` (zoom factor, default 1.02) |
| Loop | `fade_in_out_pulse` | `period` (breathing pulse cycle, seconds) |
| Static | `static` | No parameters, displayed without animation |

### border (Rounded Border)

```json
{ "width": 4, "color": "#FFD700", "radius": 20 }
```

- Setting `radius` to half of width/height → circular clip (e.g., circular video avatar)

---

## audio_track (Three-Track Audio)

### narration (Narration Track)

```json
{
  "id": "narr_1",
  "file_path": "audios/narration.mp3",
  "source_trim": { "start": 0.0, "end": 4.0 },
  "start_time": 0.0,
  "volume": 1.0,
  "subtitle": {
    "text": "This is subtitle text",
    "style_override": { "font_size": 48, "color": "#FFFF00" }
  }
}
```

Subtitle lifecycle is fully synchronized with the narration clip. `style_override` supports:

| Field | Default | Description |
|-------|---------|-------------|
| `font_size` | 46 | Font size (px) |
| `color` | `#FFFFFF` | Text color |
| `stroke_color` | `#000000` | Stroke color |
| `stroke_width` | 3 | Stroke width (px), `0` disables stroke |
| `shadow_color` | `#000000` | Shadow color |
| `shadow_offset` | 2 | Shadow offset (px), `0` disables shadow |
| `bottom_margin` | 120 | Distance from bottom of frame (px) |
| `font` | global_font | Font file path |

### bgm (Background Music Track)

```json
{
  "id": "bgm_1",
  "file_path": "bgms/tech.mp3",
  "source_trim": { "start": 0.0, "end": 15.0 },
  "start_time": 0.0,
  "volume": 0.15,
  "fx": { "fade_in": 1.0, "fade_out": 0.5 }
}
```

### sfx (Sound Effects Track)

```json
{ "id": "sfx_1", "file_path": "sfx/whoosh.mp3", "start_time": 0.5, "volume": 0.7 }
```

---

## Typical Usage

### Minimal Project (Single Segment + Background Image + Narration + Subtitle)

```json
{
  "project_name": "hello",
  "version": "2.0.0",
  "output_settings": {
    "resolution": { "width": 1080, "height": 1920 },
    "fps": 30,
    "video_codec": "libx264",
    "audio_codec": "aac",
    "global_font": "assets/fonts/font.ttf"
  },
  "segments": [
    {
      "segment_id": "seg_001",
      "duration": 5.0,
      "visual_track": [
        {
          "id": "bg",
          "type": "image",
          "file_path": "images/bg.jpg",
          "z_index": 1,
          "start_time": 0.0,
          "end_time": 5.0,
          "layout": { "x": 0, "y": 0, "width": 1080, "height": 1920 },
          "fx": { "type": "static" }
        }
      ],
      "audio_track": {
        "narration": [
          {
            "id": "narr_1",
            "file_path": "audios/narration.mp3",
            "source_trim": { "start": 0.0, "end": 5.0 },
            "start_time": 0.0,
            "volume": 1.0,
            "subtitle": { "text": "Welcome!" }
          }
        ],
        "bgm": [],
        "sfx": []
      }
    }
  ]
}
```

```bash
python3 scripts/render.py --project hello.json --output hello.mp4
```

---

## Notes

- All `file_path` values are relative to `--base-dir` (defaults to the project JSON directory)
- `start_time` / `end_time` are **relative times within the segment**, not global timeline times
- Multiple segments are concatenated in array order; rearranging is done by moving objects in the JSON
- If a video layer's `source_trim` source duration < layer display duration, it will loop automatically
- Setting `border.radius` to `width/2` or `height/2` produces a circular effect
