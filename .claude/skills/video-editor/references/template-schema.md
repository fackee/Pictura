# JSON Project Template Complete Field Reference

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_name` | string | No | Project name, used for default output filename |
| `version` | string | No | Template version, recommended `"2.0.0"` |
| `output_settings` | object | Yes | Global export parameters |
| `segments` | array | Yes | Segment array, concatenated in order |

## output_settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `resolution.width` | int | 1080 | Canvas width (px) |
| `resolution.height` | int | 1920 | Canvas height (px) |
| `fps` | int | 30 | Frame rate |
| `video_codec` | string | `libx264` | Video encoder |
| `audio_codec` | string | `aac` | Audio encoder |
| `global_font` | string | - | Global subtitle font path, relative to base-dir |

## segment

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `segment_id` | string | No | Segment ID, for logging only |
| `title` | string | No | Segment title, for logging only |
| `duration` | float | Yes | Segment duration (seconds) |
| `visual_track` | array | No | Visual layer list |
| `audio_track` | object | No | Audio three-track object |

## visual_track Layer

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | No | Layer identifier |
| `type` | string | Yes | `"image"` or `"video"` |
| `file_path` | string | Yes | Media file path (relative to base-dir) |
| `z_index` | int | No (default 0) | Stacking order, higher = more foreground |
| `start_time` | float | No (default 0) | Layer appear time (relative seconds within segment) |
| `end_time` | float | No (default duration) | Layer disappear time (relative seconds within segment) |
| `layout.x` | int | No (default 0) | Layer top-left X coordinate (px) |
| `layout.y` | int | No (default 0) | Layer top-left Y coordinate (px) |
| `layout.width` | int | No (default canvas_w) | Layer render width (px) |
| `layout.height` | int | No (default canvas_h) | Layer render height (px) |
| `volume` | float | No (default 1.0) | Video original audio volume (0=mute) |
| `source_trim.start` | float | No (default 0) | Video source file trim start (seconds) |
| `source_trim.end` | float | No | Video source file trim end (seconds) |
| `border.width` | int | No | Border thickness (px) |
| `border.color` | string | No | Border color (hexadecimal, e.g., `#FFD700`) |
| `border.radius` | int | No | Border radius (px), equal to width/2 for circle |
| `fx.in` | object | No | Entrance animation (see table below) |
| `fx.out` | object | No | Exit animation (see table below) |
| `fx.loop` | object | No | Continuous animation (see table below) |
| `fx.type` | string | No | Set to `"static"` for no animation |

## fx Entrance/Exit Animations

### fx.in / fx.out

| type | Parameters | Description |
|------|------------|-------------|
| `slide_in` | `direction`: left/right/top/bottom, `duration` (seconds) | Slide in from specified direction |
| `zoom_in` | `duration` (seconds) | Scale from small to large entrance |
| `fade_in` | `duration` (seconds) | Fade in |
| `fade_out` | `duration` (seconds) | Fade out |

### fx.loop (continuous animations)

| type | Parameters | Description |
|------|------------|-------------|
| `ken_burns` | `scale_start` (default 1.0), `scale_end` (default 1.05) | Slow dolly zoom (Dolly effect) |
| `pan` | `direction`: up_to_down/down_to_up/left_to_right, `speed` (zoom ratio, default 1.02) | Image panning |
| `fade_in_out_pulse` | `period` (seconds, default 3.0) | Luminance breathing pulse effect |

## audio_track

### narration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | No | Identifier |
| `file_path` | string | Yes | Audio file path |
| `source_trim.start` | float | No | Source file trim start (seconds) |
| `source_trim.end` | float | No | Source file trim end (seconds) |
| `start_time` | float | No (default 0) | Start time within segment (seconds) |
| `end_time` | float | No (default segment end) | End time within segment (seconds); determines subtitle duration |
| `volume` | float | No (default 1.0) | Volume |
| `subtitle.text` | string | No | Subtitle text |
| `subtitle.style_override` | object | No | Subtitle style override (see table below) |

### Subtitle style_override Fields

| Field | Default | Description |
|-------|---------|-------------|
| `font_size` | 46 | Font size (px) |
| `color` | `#FFFFFF` | Text color |
| `stroke_color` | `#000000` | Stroke color |
| `stroke_width` | 3 | Stroke width (px), `0` = stroke disabled |
| `bottom_margin` | 120 | Distance from bottom of frame (px) |
| `font` | global_font | Font file path |

### bgm Fields

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | string | Audio file path |
| `source_trim` | object | Source file start/end seconds |
| `start_time` | float | Start time within segment |
| `volume` | float | Volume (0~1, recommended 0.1~0.3) |
| `fx.fade_in` | float | Fade-in duration (seconds) |
| `fx.fade_out` | float | Fade-out duration (seconds) |

### sfx Fields

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | string | Sound effect file path |
| `start_time` | float | Trigger time within segment (seconds) |
| `volume` | float | Volume |
