# ContentCreator / AI 自动化内容创作 Agent

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## Overview

**ContentCreator** is an AI-powered automated video production agent. Given a content topic, it orchestrates the entire pipeline — from requirement gathering, script writing, and asset generation to final video rendering — delivering a polished, ready-to-publish video product.

Built on [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with a modular skill architecture, ContentCreator coordinates 5 specialized skills to handle images, video, narration, music, and compositing. No manual editing required.

## Features

- **End-to-end automation** — From a one-line topic to a finished video, fully automated
- **Two production modes** — Cost-first (static images) for quick turnaround; Quality-first (AI-generated video) for richer visuals
- **Multi-modal asset generation** — AI-generated illustrations, voiceover, background music, and optional video clips
- **JSON-driven compositing** — Timeline, layers, transitions, and audio all defined in a single `project.json`
- **Frame-accurate timing** — TTS durations measured with `ffprobe`, never estimated
- **Bilingual support** — Narration and subtitles in English, Chinese, and more

## Architecture

```
User Request
    │
    ▼
┌─────────────────────────────────┐
│         CLAUDE.md (Orchestrator) │   ← Production pipeline & rules
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
  ┌─────────┐   ┌──────────┐
  │ Images  │   │  Videos  │    Visual assets
  └────┬────┘   └────┬─────┘
       │              │
  ┌────┴────┐   ┌────┴─────┐
  │  TTS    │   │   BGM    │    Audio assets
  └────┬────┘   └────┬─────┘
       │              │
       └──────┬───────┘
              ▼
       ┌─────────────┐
       │ Video Editor │    Compositing & rendering
       └──────┬──────┘
              ▼
         output.mp4
```

## Skills

| Skill | Service | Description |
|-------|---------|-------------|
| **nanobanana-image** | [Google Gemini](https://ai.google.dev/) | Text-to-image generation & editing (Nano Banana models). Supports multi-image composition, style transfer, web search generation, and up to 4K output. |
| **seedance2-gen-video** | [Volcengine Doubao Seedance 2.0](https://www.volcengine.com/) | AI video generation — text-to-video, image-to-video, video editing, and extension. |
| **doubao-tts** | [Volcano Engine Doubao TTS](https://www.volcengine.com/product/speech) | English/Chinese/multilingual speech synthesis and voice cloning from audio samples. |
| **doubao-genbgm** | [Volcano Engine Doubao Music](https://www.volcengine.com/product/music-generation) | Instrumental BGM and vocal song generation with genre, mood, tempo, and instrument control. |
| **video-editor** | moviepy + FFmpeg | JSON template-driven rendering engine with multi-layer compositing, entrance/exit/loop animations, three-track audio, and deep subtitle binding. |

## Production Pipeline

### Step 1 — Requirement Clarification

Do **not** rush into production. Communicate with the user to confirm:

- Video aspect ratio / resolution
- Visual style (realistic, cartoon, tech, cinematic...)
- Content tone and language
- Target duration or platform

Output: `{date}-{topic}/requirement.md`

### Step 2 — Choose Production Mode

| Mode | Description |
|------|-------------|
| **Quality-first** | AI-generated video assets via `seedance2-gen-video` — richer, more dynamic visuals |
| **Cost-first** | Static images via `nanobanana-image` — faster and cheaper |

### Step 3 — Script Breakdown & `project.json`

1. Write a narration script, split into sentence-level segments
2. For each segment, define: start time, duration, visual asset, subtitle text
3. Determine BGM segments with fade-in/fade-out points
4. Output `project.json` following the video-editor template schema

**Key rule**: Narration timing must be derived from actual TTS audio durations — never guess.

### Step 4 — Asset Generation

Generate all assets in parallel where possible:

| Asset | Skill | Notes |
|-------|-------|-------|
| Images | `nanobanana-image` | Follow `guide/nano-banana-guide.md` |
| Videos | `seedance2-gen-video` | Follow `guide/generate-video-guide.md` |
| Narration | `doubao-tts` | One TTS clip per sentence |
| BGM | `doubao-genbgm` | Generate in BGM mode, trim via `source_trim` |

After generating all TTS clips, measure each file's actual duration with `ffprobe` and update `project.json` timings.

### Step 5 — Video Rendering

```bash
python3 scripts/render.py \
  --project project.json \
  --output output.mp4 \
  --base-dir /path/to/project
```

## Project Structure

Every production run creates a dated subfolder:

```
ContentCeator/
├── CLAUDE.md                           # Agent instructions & pipeline rules
├── README.md                           # This file
├── guide/                              # Prompting guides
│   ├── nano-banana-guide.md            #   Image generation guide
│   └── generate-video-guide.md         #   Video generation guide
├── .claude/
│   └── skills/                         # Modular skill definitions
│       ├── nanobanana-image/            #   Image generation & editing
│       ├── seedance2-gen-video/         #   AI video generation
│       ├── doubao-tts/                  #   Speech synthesis & cloning
│       ├── doubao-genbgm/               #   Music generation
│       └── video-editor/               #   Video rendering engine
├── 2026-06-26-static-friction/         # Example project: physics concept
│   ├── requirement.md
│   ├── project.json
│   ├── images/
│   ├── audios/
│   ├── bgms/
│   └── static-friction.mp4
└── 2026-06-26-ai-history/              # Example project: AI history
    ├── requirement.md
    ├── project.json
    ├── images/
    ├── audios/
    ├── bgms/
    └── output.mp4
```

Each video project follows the same convention:

```
{date}-{topic}/
├── requirement.md      # Requirement specification
├── project.json        # Composition timeline
├── images/             # *.png
├── videos/             # *.mp4 (Quality-first mode)
├── audios/             # *.mp3 (narration clips)
├── bgms/               # *.mp3
├── subtitles/          # *.srt
└── output.mp4          # Final rendered video
```

## Getting Started

### Prerequisites

- **Python 3.9+**
- **FFmpeg** (installed and in PATH)
- **[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)**

### API Keys

Configure API keys in the `.env` file inside each skill directory:

| Skill | Variable | Service |
|-------|----------|---------|
| `nanobanana-image` | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `seedance2-gen-video` | `ARK_API_KEY` | [Volcengine Console](https://console.volcengine.com/ark) |
| `doubao-tts` | `DOUBAO_API_KEY` or `DOUBAO_APP_ID` + `DOUBAO_ACCESS_KEY` | [Volcano Engine Console](https://console.volcengine.com/speech) |
| `doubao-genbgm` | `VOLC_ACCESSKEY` + `VOLC_SECRETKEY` | [Volcano Engine Console](https://console.volcengine.com/iam/keymanage/) |

### Install Dependencies

```bash
pip install requests moviepy pillow google-genai
```

### Run

```bash
# Launch Claude Code in the project directory
cd ContentCeator
claude

# Then describe your video topic, e.g.:
> Generate a 2-minute video about the solar system, cartoon style, English narration
```

## Examples

| Project | Topic | Duration | Mode | Style |
|---------|-------|----------|------|-------|
| `2026-06-26-ai-history` | History of Artificial Intelligence | ~108s | Cost-first | Cartoon illustrations |

## License

MIT

---

<a id="中文"></a>

## 项目简介

**ContentCreator** 是一个 AI 驱动的自动化视频制作 Agent。只需给出内容主题，它就能自动完成从需求沟通、脚本编写、素材生成到最终渲染的全流程，直接交付可发布的成品视频。

基于 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 构建并采用模块化 Skill 架构，ContentCreator 协调 5 个专业化的 Skill 来处理图片、视频、配音、配乐和合成，无需手动剪辑。

## 核心特性

- **全流程自动化** — 从一行主题描述到成品视频，全程无需人工干预
- **两种制作模式** — 成本优先（静态图片）快速出片；质量优先（AI 生成视频）视觉更丰富
- **多模态素材生成** — AI 生成插画、配音、背景音乐，可选 AI 视频片段
- **JSON 驱动合成** — 时间线、图层、转场、音轨全部定义在 `project.json` 中
- **帧级精确对齐** — TTS 时长通过 `ffprobe` 实测，绝不估算
- **多语言支持** — 配音和字幕支持英语、中文等多种语言

## 架构

```
用户请求
    │
    ▼
┌─────────────────────────────────┐
│        CLAUDE.md（编排器）         │   ← 制作流程与规则
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
  ┌─────────┐   ┌──────────┐
  │   图片   │   │   视频   │     视觉素材
  └────┬────┘   └────┬─────┘
       │              │
  ┌────┴────┐   ┌────┴─────┐
  │  TTS    │   │   BGM    │     音频素材
  └────┬────┘   └────┬─────┘
       │              │
       └──────┬───────┘
              ▼
       ┌─────────────┐
       │  视频编辑器  │     合成与渲染
       └──────┬──────┘
              ▼
         output.mp4
```

## Skill 模块

| Skill | 服务 | 说明 |
|-------|------|------|
| **nanobanana-image** | [Google Gemini](https://ai.google.dev/) | 文生图与图片编辑（Nano Banana 模型），支持多图合成、风格迁移、搜索生成，最高 4K 输出 |
| **seedance2-gen-video** | [火山引擎豆包 Seedance 2.0](https://www.volcengine.com/) | AI 视频生成 — 文生视频、图生视频、视频编辑与续写 |
| **doubao-tts** | [火山引擎豆包语音合成](https://www.volcengine.com/product/speech) | 英语/中文/多语种语音合成与声音克隆 |
| **doubao-genbgm** | [火山引擎豆包音乐生成](https://www.volcengine.com/product/music-generation) | 纯音乐 BGM 与人声歌曲生成，支持风格、情绪、节奏、乐器控制 |
| **video-editor** | moviepy + FFmpeg | JSON 模板驱动的渲染引擎，支持多层合成、入场/出场/循环动画、三轨音频与字幕绑定 |

## 制作流程

### 第一步 — 需求确认

**绝不跳过此步。** 与用户确认：

- 视频宽高比 / 分辨率
- 视觉风格（写实、卡通、科技、电影感……）
- 内容基调与语言
- 目标时长或平台

输出：`{日期}-{主题}/requirement.md`

### 第二步 — 选择制作模式

| 模式 | 说明 |
|------|------|
| **质量优先** | 通过 `seedance2-gen-video` 生成视频素材，视觉更丰富动态 |
| **成本优先** | 通过 `nanobanana-image` 生成静态图片，更快更省 |

### 第三步 — 脚本拆解与 `project.json`

1. 编写旁白脚本，按句子拆分为独立片段
2. 为每个片段定义：起始时间、时长、对应视觉素材、字幕文本
3. 确定 BGM 片段及淡入淡出点
4. 按 video-editor 模板规范输出 `project.json`

**关键规则**：旁白时长必须从实际 TTS 音频时长推导，绝不估算。

### 第四步 — 素材生成

尽可能并行生成所有素材：

| 素材 | Skill | 说明 |
|------|-------|------|
| 图片 | `nanobanana-image` | 遵循 `guide/nano-banana-guide.md` |
| 视频 | `seedance2-gen-video` | 遵循 `guide/generate-video-guide.md` |
| 配音 | `doubao-tts` | 每句一个 TTS 片段 |
| 配乐 | `doubao-genbgm` | BGM 模式生成，通过 `source_trim` 裁剪 |

生成所有 TTS 后，使用 `ffprobe` 测量实际时长并更新 `project.json`。

### 第五步 — 视频渲染

```bash
python3 scripts/render.py \
  --project project.json \
  --output output.mp4 \
  --base-dir /path/to/project
```

## 项目结构

每次制作产出以日期命名的子目录：

```
ContentCeator/
├── CLAUDE.md                           # Agent 指令与流程规则
├── README.md                           # 本文件
├── guide/                              # 提示词指南
│   ├── nano-banana-guide.md            #   图片生成指南
│   └── generate-video-guide.md         #   视频生成指南
├── .claude/
│   └── skills/                         # 模块化 Skill 定义
│       ├── nanobanana-image/            #   图片生成与编辑
│       ├── seedance2-gen-video/         #   AI 视频生成
│       ├── doubao-tts/                  #   语音合成与克隆
│       ├── doubao-genbgm/               #   音乐生成
│       └── video-editor/               #   视频渲染引擎
├── 2026-06-26-static-friction/         # 示例项目：物理概念
│   ├── requirement.md
│   ├── project.json
│   ├── images/
│   ├── audios/
│   ├── bgms/
│   └── static-friction.mp4
└── 2026-06-26-ai-history/              # 示例项目：AI 发展史
    ├── requirement.md
    ├── project.json
    ├── images/
    ├── audios/
    ├── bgms/
    └── output.mp4
```

每个视频项目遵循统一规范：

```
{日期}-{主题}/
├── requirement.md      # 需求规格文档
├── project.json        # 合成时间线
├── images/             # *.png
├── videos/             # *.mp4（质量优先模式）
├── audios/             # *.mp3（配音片段）
├── bgms/               # *.mp3
├── subtitles/          # *.srt
└── output.mp4          # 最终渲染视频
```

## 快速开始

### 环境依赖

- **Python 3.9+**
- **FFmpeg**（已安装并在 PATH 中）
- **[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)**

### API 密钥配置

在各 Skill 目录的 `.env` 文件中配置 API 密钥：

| Skill | 变量 | 服务 |
|-------|------|------|
| `nanobanana-image` | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `seedance2-gen-video` | `ARK_API_KEY` | [火山引擎控制台](https://console.volcengine.com/ark) |
| `doubao-tts` | `DOUBAO_API_KEY` 或 `DOUBAO_APP_ID` + `DOUBAO_ACCESS_KEY` | [火山引擎控制台](https://console.volcengine.com/speech) |
| `doubao-genbgm` | `VOLC_ACCESSKEY` + `VOLC_SECRETKEY` | [火山引擎控制台](https://console.volcengine.com/iam/keymanage/) |

### 安装依赖

```bash
pip install requests moviepy pillow google-genai
```

### 运行

```bash
# 在项目目录中启动 Claude Code
cd ContentCeator
claude

# 描述你的视频主题，例如：
> 生成一个2分钟关于太阳系的视频，卡通风格，英文配音
```

## 示例项目

| 项目 | 主题 | 时长 | 模式 | 风格 |
|------|------|------|------|------|
| `2026-06-26-static-friction` | 静摩擦力（物理） | ~18s | 成本优先 | 写实示意图 |
| `2026-06-26-ai-history` | 人工智能发展史 | ~108s | 成本优先 | 卡通插画 |

## License

MIT
