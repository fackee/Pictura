---
name: html-animate-mp4
description: Generate animated MP4 from HTML/JS animation code. Agent writes self-contained HTML animation, captures frames via Playwright, synthesizes MP4 with ffmpeg.
compatibility: python3.10+
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  tags: [animation, mp4, html, canvas, playwright, ffmpeg]
  version: "2.0.0"
---

# html-animate-mp4

Generate animated MP4 assets from self-contained HTML/JS animation code.

## Prerequisites

Install dependencies before first use:

```bash
pip install playwright && playwright install chromium
```

Also install ffmpeg:

```bash
brew install ffmpeg          # macOS
apt-get install ffmpeg       # Ubuntu/Debian
```

## Workflow

### Step 1: Understand Requirements

Clarify with the user:
- **Animation type**: text effect, particle, data visualization, background texture, logo, etc.
- **Visual style**: colors, mood, branding
- **Usage context**: video overlay, social media, presentation
- **Size**: default 1920x1080 if not specified
- **Duration**: default 3s if not specified
- **Background**: default #000000 (black) if not specified — MP4 does not support transparency

### Step 2: Choose Technology

| Technology | Best For | Complexity |
|------------|----------|------------|
| CSS Keyframes | Simple text effects, fades, slides | Low |
| CSS + JS | Text stagger, timed sequences | Medium |
| **Canvas API** | Particles, effects, data viz, complex animation | **Medium (Default)** |
| SVG + CSS/JS | Shape morph, path animation, icons | Medium |

**Default: Canvas API** — it provides the most control for frame-accurate capture.

### Step 3: Write HTML

Write a self-contained HTML file following the **mandatory template** below. Save to `/tmp/animate_<timestamp>.html`.

### Step 4: Export MP4

Run the export script:

```bash
python3 <skill-dir>/scripts/export_mp4.py --html <html-path> --output <output-path> [options]
```

### Step 5: Deliver

Report the MP4 file path, file size, and any notes about the animation.

## Mandatory HTML Template

All animation HTML files MUST follow this structure:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { width: {WIDTH}px; height: {HEIGHT}px; overflow: hidden; background: {BG_COLOR}; }
  canvas { display: block; }
</style>
</head>
<body>
<canvas id="canvas" width="{WIDTH}" height="{HEIGHT}"></canvas>
<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;

// --- Animation code here ---
// Use requestAnimationFrame loop
// Consult references/ for recipes and patterns

// IMPORTANT: Signal that first frame is rendered
// For Canvas animations, set after first draw:
function animate(timestamp) {
  // ... draw frame ...
  if (!window.animationReady) window.animationReady = true;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

// For CSS animations, set on load:
// window.addEventListener('load', () => {
//   requestAnimationFrame(() => { window.animationReady = true; });
// });
</script>
</body>
</html>
```

## HTML Coding Rules

1. **Self-contained** — no external dependencies, no CDN links, no images, no fonts
2. **Deterministic rendering** — use system fonts only (`sans-serif`, `monospace`, `serif`)
3. **Set `window.animationReady = true`** — the export script waits for this signal
4. **Explicit background** — always set `background` on body and canvas, never rely on default
5. **Fixed viewport** — match canvas size to body size, use pixel values
6. **Loop-friendly** — animations should loop seamlessly for video use (unless one-shot)
7. **No ES modules** — use plain `<script>` tags, no `import`/`export`
8. **No `alert`/`prompt`** — no browser dialogs
9. **Test values** — hardcode all values, no external config files
10. **Canvas for complex** — prefer Canvas over DOM manipulation for particle effects and complex animations

## export_mp4.py Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--html` | (required) | Path to HTML file |
| `--output` | `output.mp4` | Output MP4 path |
| `--width` | `1920` | Viewport width in pixels |
| `--height` | `1080` | Viewport height in pixels |
| `--fps` | `24` | Frames per second (1-60) |
| `--duration` | `3` | Capture duration in seconds |
| `--bg-color` | `#000000` | Background hex color (MP4 does not support transparency) |
| `--scale` | `1.0` | Output scale factor (e.g., 0.5 for half size) |
| `--crf` | `18` | ffmpeg CRF quality 0-51, lower=better (default: 18) |
| `--preset` | `medium` | ffmpeg encoding speed preset (ultrafast to veryslow) |
| `--wait` | `0.5` | Extra wait after animationReady (seconds) |

## Common Sizes

| Ratio | Resolution | Use Case |
|-------|-----------|----------|
| 16:9 | 1920x1080 | Video, presentation (default) |
| 16:9 | 1280x720 | 720p video |
| 9:16 | 1080x1920 | Mobile, stories, reels |
| 1:1 | 1080x1080 | Social media square |
| 4:3 | 1440x1080 | Classic video |
| 21:9 | 1920x823 | Cinematic |

## MP4 Notes & Tips

- **No transparency** — MP4 does not support alpha channels. Use `--bg-color` to specify a solid background color that matches your animation style (e.g., `#000000` for dark themes, `#ffffff` for light themes)
- **CRF quality** — Controls visual quality vs file size:
  - `18` — visually lossless (recommended default)
  - `23` — default x264 quality, good balance
  - `28` — smaller file, noticeable quality loss at close inspection
- **Preset** — Controls encoding speed vs compression efficiency:
  - `ultrafast` / `superfast` — fast encode, larger file
  - `medium` — balanced (default)
  - `slow` / `slower` / `veryslow` — slower encode, smaller file
- **Compatibility** — The script uses `yuv420p` pixel format and H.264 codec for maximum compatibility with browsers, QuickTime, and mobile devices
- **File size** — MP4 files are typically 5-10x smaller than equivalent GIFs with full color fidelity
- **FPS** — 24-30 FPS is sufficient for smooth video; higher FPS increases file size with diminishing returns
- **Fast start** — `movflags +faststart` moves metadata to the file header for streaming-friendly playback

## References

Consult these files for implementation guidance:
- `references/animation-recipes.md` — 15 ready-to-use animation code snippets (primary reference)
- `references/js-animation-patterns.md` — rAF loops, easing functions, color interpolation, math utils
- `references/canvas-api.md` — Canvas 2D API quick reference
- `references/css-animation.md` — CSS animation reference for simpler effects
