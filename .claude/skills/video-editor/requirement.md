# template

```
{
  "project_name": "AI-History-Development-Timeline",
  "version": "2.0.0",
  "output_settings": {
    "resolution": { "width": 1080, "height": 1920 },
    "aspect_ratio": "9:16",
    "fps": 30,
    "video_codec": "libx264",
    "audio_codec": "aac",
    "global_font": "assets/fonts/SourceHanSans-Bold.ttf"
  },
  "segments": [
    {
      "segment_id": "seg_001",
      "title": "Opening-Multi-Image-Collage-with-Effects",
      "duration": 15.0,
      "visual_track": [
        {
          "id": "bg_layer",
          "type": "image",
          "file_path": "20260607-AI历史发展脉络/images/001-bg-gradient.png",
          "z_index": 1,
          "start_time": 0.0,
          "end_time": 15.0,
          "layout": { "x": 0, "y": 0, "width": 1080, "height": 1920 },
          "fx": { "type": "static" }
        },
        {
          "id": "pic_top_left",
          "type": "image",
          "file_path": "20260607-AI历史发展脉络/images/001-voice-assistant.png",
          "z_index": 2,
          "start_time": 0.5,
          "end_time": 15.0,
          "layout": { "x": 50, "y": 200, "width": 460, "height": 600 },
          "fx": {
            "in": { "type": "slide_in", "direction": "left", "duration": 0.5 },
            "loop": { "type": "ken_burns", "scale_start": 1.0, "scale_end": 1.05 }
          }
        },
        {
          "id": "pic_top_right",
          "type": "image",
          "file_path": "20260607-AI历史发展脉络/images/001-autonomous-driving.png",
          "z_index": 2,
          "start_time": 1.0,
          "end_time": 15.0,
          "layout": { "x": 570, "y": 200, "width": 460, "height": 600 },
          "fx": {
            "in": { "type": "slide_in", "direction": "right", "duration": 0.5 },
            "loop": { "type": "pan", "direction": "up_to_down", "speed": 1.02 }
          }
        },
        {
          "id": "video_center_lens",
          "type": "video",
          "file_path": "20260607-AI历史发展脉络/videos/001-neural-network-mesh.mp4",
          "z_index": 3,
          "start_time": 3.0,
          "end_time": 15.0,
          "source_trim": { "start": 0.0, "end": 12.0 },
          "layout": { "x": 290, "y": 610, "width": 500, "height": 500 },
          "volume": 0.0,
          "border": { "width": 4, "color": "#00FFFF", "radius": 250 },
          "fx": {
            "in": { "type": "zoom_in", "duration": 0.6 },
            "loop": { "type": "fade_in_out_pulse", "period": 3.0 }
          }
        }
      ],
      "audio_track": {
        "narration": [
          {
            "id": "narr_1",
            "file_path": "20260607-AI历史发展脉络/audios/001-narration-full.mp3",
            "source_trim": { "start": 0.0, "end": 4.0 },
            "start_time": 0.0,
            "volume": 1.0,
            "subtitle": {
              "text": "Smartphones, autonomous driving, AI writing...",
              "style_override": { "font_size": 48, "color": "#FFFF00" }
            }
          },
          {
            "id": "narr_2",
            "file_path": "20260607-AI历史发展脉络/audios/001-narration-full.mp3",
            "source_trim": { "start": 4.0, "end": 8.0 },
            "start_time": 4.0,
            "volume": 1.0,
            "subtitle": {
              "text": "AI has penetrated every corner of our lives."
            }
          }
        ],
        "bgm": [
          {
            "id": "bgm_1",
            "file_path": "20260607-AI历史发展脉络/bgms/001-tech-bgm.mp3",
            "source_trim": { "start": 0.0, "end": 15.0 },
            "start_time": 0.0,
            "volume": 0.15,
            "fx": { "fade_in": 1.0, "fade_out": 0.5 }
          }
        ],
        "sfx": [
          { "id": "sfx_w1", "file_path": "20260607-AI历史发展脉络/sfx/whoosh.mp3", "start_time": 0.5, "volume": 0.7 },
          { "id": "sfx_w2", "file_path": "20260607-AI历史发展脉络/sfx/whoosh.mp3", "start_time": 1.0, "volume": 0.7 },
          { "id": "sfx_p1", "file_path": "20260607-AI历史发展脉络/sfx/pop.mp3", "start_time": 3.0, "volume": 0.9 }
        ]
      }
    },
    {
      "segment_id": "seg_002",
      "title": "Origins-PIP-Deep-Switch",
      "duration": 15.0,
      "visual_track": [
        {
          "id": "turing_lab_base",
          "type": "image",
          "file_path": "20260607-AI历史发展脉络/images/002-turing-lab-1950s.png",
          "z_index": 1,
          "start_time": 0.0,
          "end_time": 15.0,
          "layout": { "x": 0, "y": 0, "width": 1080, "height": 1920 },
          "fx": {
            "loop": { "type": "ken_burns", "scale_start": 1.0, "scale_end": 1.08 }
          }
        },
        {
          "id": "turing_test_pip",
          "type": "image",
          "file_path": "20260607-AI历史发展脉络/images/003-turing-test-concept.png",
          "z_index": 2,
          "start_time": 6.0,
          "end_time": 15.0,
          "layout": { "x": 90, "y": 300, "width": 900, "height": 700 },
          "border": { "width": 6, "color": "#FFD700", "radius": 20 },
          "fx": {
            "in": { "type": "slide_in", "direction": "bottom", "duration": 0.6 },
            "out": { "type": "fade_out", "duration": 0.4 }
          }
        }
      ],
      "audio_track": {
        "narration": [
          {
            "id": "narr_3",
            "file_path": "20260607-AI历史发展脉络/audios/001-narration-full.mp3",
            "source_trim": { "start": 15.0, "end": 19.0 },
            "start_time": 0.0,
            "volume": 1.0,
            "subtitle": { "text": "The story begins in 1950." }
          }
        ],
        "bgm": [
          {
            "id": "bgm_1_cont",
            "file_path": "20260607-AI历史发展脉络/bgms/001-tech-bgm.mp3",
            "source_trim": { "start": 15.0, "end": 30.0 },
            "start_time": 0.0,
            "volume": 0.15
          }
        ],
        "sfx": []
      }
    }
  ]
}
```

# description

The entire template follows a top-down design philosophy where the timeline within each segment is relatively decoupled, ensuring efficient and error-resistant parsing by Python scripts.

## 2.1 Root Node & Global Configuration (output_settings)

Controls the overall export parameters for the video project. The Python script reads these parameters first when initializing the renderer.

- resolution: Defines the physical pixel width and height of the canvas. All layer coordinates (X, Y) and scaling are based on this.
- fps: Frame rate. Determines the step size for animation keyframe calculations (30 frames per second).
- global_font: Global default subtitle/text font path, preventing script errors when system fonts cannot be found.

## 2.2 Segment-Level Core (segments)

The video is divided into multiple independent blocks (segments).

Core logic: Each object in the segments array has an independent duration. All components within a segment use start_time and end_time as relative times from the segment start (0.0 ~ duration). Benefit: When looping through segments for concatenation in Python, you only need to maintain a global pointer: global_time += segment['duration']. If you want to adjust the video structure (e.g., move the second segment to the first position), simply swap the order in the JSON array—no need to rewrite any timestamps.

2.3 Visual Track Control (visual_track)

Supports multiple images or videos coexisting at the same time. The Python script should parse and map them as overlay layers in CompositeVideoClip.

- Component type (type): Supports "image" or "video".
  * If "video", adds source_trim (which seconds to extract from the source video) and volume control (whether to keep the original audio during mixing).
- Render layer (z_index): Integer value. Lower values are at the bottom (background), higher values are on top (foreground/PIP/stickers). The parsing script must sort by z_index in ascending order before compositing.
- Absolute layout coordinates (layout): x, y: Absolute pixel coordinates of the component's top-left corner on the 1080x1920 canvas. width, height: Target resolution the script forces the media to resize to during rendering.
- Border visual (border): Designed specifically for picture-in-picture (PIP) and multi-image collages. Supports border thickness, color, and rounded corners (radius). For circular avatars/bubble videos, set the radius to half of width or height.
- Effects animation engine (fx):
  * in / out: Entrance/exit animations. The script checks the type (e.g., slide_in, fade_in, zoom_in) to dynamically apply crossfade or position transforms for the first/last N seconds of the component.
  * loop: Periodic or continuous animations. E.g., ken_burns (slow dolly zoom), pan (horizontal/vertical panning), pulse (breathing scale), giving static images dynamic vitality.

- 2.4 Independent Three-Track Audio Bus (audio_track)

To prevent audio from overlapping, audio is split into three functionally distinct tracks. The script processes them independently, then mixes them together into the final video:
  1. Narration track (narration): The core backbone of the video. Usually sourced from a single TTS audio file sliced via source_trim.
  2. Background music track (bgm): Typically spans multiple segments, with its own fade_in / fade_out easing to avoid abrupt music cuts.
  3. Sound effects track (sfx): Short sound effects (e.g., pop, whoosh, explosion), precisely bound to the timestamps where images appear (start_time), greatly enhancing the video's dynamic feel.

- 2.5 Deep Subtitle Binding (subtitle)

Subtitles are not a separate top-level track; instead, they are deeply nested within the narration component.
  * Rationale: Since subtitles are "the visualization of human voice," wherever there is narration, there must be subtitles. The subtitle lifecycle (start and end) perfectly synchronizes with the narration component's start_time and duration.
  * Style override (style_override): Inherits global subtitle styles by default, but supports local overrides (e.g., highlighting the first sentence in yellow #FFFF00 or increasing font size) to achieve keyword emphasis effects in automated editing.
