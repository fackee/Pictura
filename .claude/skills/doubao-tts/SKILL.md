---
name: doubao-tts
description: Call the Volcano Engine Doubao Large Model Speech Synthesis V3 API to perform text-to-speech (TTS) and voice cloning. Supports public/cloned voice synthesis, configurable speech rate/volume/emotion/language, and training cloned voices from audio samples. Use this skill when users need to convert text to speech, synthesize audio, clone voices, or replicate voice timbres.
compatibility: Requires Python 3.9+ and the requests library (pip install requests), a Volcano Engine account with Speech Synthesis service enabled
metadata:
  author: SkillDeveloper
  version: "1.0"
allowed-tools: Bash(python3:*) Bash(pip:*)
---

# Doubao TTS + Voice Cloning Skill

Based on the Volcano Engine Doubao Large Model Speech Synthesis V3 API, providing two scripts:
- `scripts/clone_voice.py`: Train a cloned voice from an audio sample
- `scripts/tts.py`: Synthesize text into an audio file

## Prerequisites

**1. Install Dependencies**
```bash
pip install requests
```

**2. Obtain Authentication Credentials**

Using the **new console** is recommended; it only requires one API Key:
- Visit the [Volcano Engine Console](https://console.volcengine.com/speech/new) -> API Key Management -> Create API Key

The legacy console requires App ID + Access Key (or App Key + Access Key).

```bash
export DOUBAO_API_KEY=$DOUBAO_API_KEY
```

**3. Enable Services**
- TTS public voices: Enable "Doubao Speech Synthesis Large Model"
- Voice cloning: Enable "Voice Cloning Large Model"

---

## 1. Voice Cloning (clone_voice.py)

Upload an audio sample to train a cloned voice. After successful training, you will receive a speaker_id that can be used for TTS synthesis.

### Audio Requirements
- Format: wav, mp3, ogg, m4a, aac (pcm only supports 24k mono)
- Size: <= 10MB
- Recommendation: Clear human voice, minimal background noise, duration 10~30 seconds

### Usage Examples

**Prepaid voice (requires purchasing a voice slot in the console first):**
```bash
# New console authentication (recommended)
python3 scripts/clone_voice.py \
  --api-key "your-api-key" \
  --speaker-id "S_xxxxxxx" \
  --audio "sample.wav" \
  --language 0

# Continuously poll until training is complete
python3 scripts/clone_voice.py \
  --api-key "your-api-key" \
  --speaker-id "S_xxxxxxx" \
  --audio "sample.wav" \
  --poll
```

**Postpaid voice (custom voice ID, first synthesis incurs a charge):**
```bash
python3 scripts/clone_voice.py \
  --api-key "your-api-key" \
  --custom-speaker-id "custom_zh_myvoice" \
  --audio "sample.wav" \
  --language 0 \
  --demo-text "Hello, this is my cloned voice." \
  --poll
```

**Enable denoising when audio has significant background noise:**
```bash
python3 scripts/clone_voice.py \
  --api-key "your-api-key" \
  --speaker-id "S_xxxxxxx" \
  --audio "noisy_sample.mp3" \
  --denoise \
  --poll
```

**Legacy console authentication:**
```bash
python3 scripts/clone_voice.py \
  --app-key "your-app-key" \
  --access-key "your-access-key" \
  --speaker-id "S_xxxxxxx" \
  --audio "sample.wav"
```

### Training Status Codes

| status | Meaning |
|--------|---------|
| 0 | NotFound (not found) |
| 1 | Training (in progress) |
| 2 | Success (training complete, available for synthesis) |
| 3 | Failed (training failed) |
| 4 | Active (activated, available for synthesis) |

When status is 2 or 4, the speaker_id can be used for TTS synthesis.

### Parameter Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--api-key` | New console API Key (recommended) | - |
| `--app-key` | Legacy console App Key | - |
| `--access-key` | Legacy console Access Key | - |
| `--speaker-id` | Prepaid voice ID (e.g. `S_xxxxxxx`) | - |
| `--custom-speaker-id` | Postpaid custom voice ID | - |
| `--audio` | Audio file path | Required |
| `--language` | Language: 0=Chinese 1=English 2=Japanese 3=Spanish 4=Indonesian 5=Portuguese 8=Korean | `0` |
| `--denoise` | Enable denoising | Off |
| `--demo-text` | Demo text for preview (4~300 characters) | None |
| `--poll` | Continuously poll until training is complete | Query once only |
| `--poll-interval` | Polling interval (seconds) | `10` |

---

## 2. Text-to-Speech (tts.py)

Synthesize text into an audio file, supporting public voices and cloned voices, with configurable speech rate/volume/emotion, etc.

### Usage Examples

**Basic synthesis (public voice):**
```bash
python3 scripts/tts.py \
  --api-key "your-api-key" \
  --app-id "your-app-id" \
  --access-key "your-access-key" \
  --speaker "zh_female_shuangkuaisisi_moon_bigtts" \
  --text "Hello, welcome to the Doubao speech synthesis service." \
  --output "hello.mp3"
```

**Using a cloned voice:**
```bash
python3 scripts/tts.py \
  --api-key "your-api-key" \
  --app-id "your-app-id" \
  --access-key "your-access-key" \
  --speaker "S_xxxxxxx" \
  --resource-id "seed-icl-2.0" \
  --text "This is audio synthesized using my cloned voice." \
  --output "cloned.mp3"
```

**Reading long text from a file:**
```bash
python3 scripts/tts.py \
  --api-key "your-api-key" \
  --app-id "your-app-id" \
  --access-key "your-access-key" \
  --speaker "zh_female_shuangkuaisisi_moon_bigtts" \
  --text-file "article.txt" \
  --output "article.mp3"
```

**Adjusting speech rate, volume, and emotion:**
```bash
python3 scripts/tts.py \
  --api-key "your-api-key" \
  --app-id "your-app-id" \
  --access-key "your-access-key" \
  --speaker "zh_female_shuangkuaisisi_moon_bigtts" \
  --text "I am so happy today!" \
  --speech-rate 20 \
  --loudness 10 \
  --emotion "happy" \
  --output "happy.mp3"
```

**Output WAV format + return timestamps:**
```bash
python3 scripts/tts.py \
  --api-key "your-api-key" \
  --app-id "your-app-id" \
  --access-key "your-access-key" \
  --speaker "zh_female_shuangkuaisisi_moon_bigtts" \
  --text "This passage will include subtitle timestamps." \
  --format "wav" \
  --sample-rate 44100 \
  --timestamps \
  --output "output.wav"
```

**Legacy console authentication:**
```bash
python3 scripts/tts.py \
  --app-id "your-app-id" \
  --access-key "your-access-key" \
  --speaker "zh_female_shuangkuaisisi_moon_bigtts" \
  --text "Hello world" \
  --output "hello.mp3"
```

### Parameter Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--api-key` | New console API Key (recommended) | - |
| `--app-id` | Legacy console App ID (for TTS authentication) | - |
| `--access-key` | Legacy console Access Key | - |
| `--speaker` | Voice ID (required) | Required |
| `--resource-id` | Resource ID | `seed-tts-1.0` |
| `--text` | Text to synthesize (up to 100,000 characters) | - |
| `--text-file` | Read text from file | - |
| `--format` | Audio format: mp3/ogg_opus/pcm/wav | `mp3` |
| `--sample-rate` | Sample rate | `24000` |
| `--speech-rate` | Speech rate [-50, 100], 100=2x speed | `0` |
| `--loudness` | Volume [-50, 100], 100=2x volume | `0` |
| `--emotion` | Emotion (e.g. happy/sad/angry, requires voice support) | None |
| `--language` | Explicit language (zh-cn/en/crosslingual, etc.) | None |
| `--timestamps` | Return subtitle timestamps | Off |
| `--output` | Output file path | `output.mp3` |
| `--poll-interval` | Polling interval (seconds) | `5` |

### Resource ID and Voice Correspondence

| Resource ID | Applicable Voices |
|-------------|-------------------|
| `seed-tts-1.0` | Doubao Speech Synthesis Model 1.0 public voices |
| `seed-tts-2.0` | Doubao Speech Synthesis Model 2.0 public voices |
| `seed-icl-1.0` | Voice Cloning 1.0 cloned voices |
| `seed-icl-2.0` | Voice Cloning 2.0 cloned voices |

---

## Typical Workflow

### Clone a Voice and Synthesize Audio

```bash
# Step 1: Train a cloned voice (wait for completion)
python3 scripts/clone_voice.py \
  --api-key "your-api-key" \
  --custom-speaker-id "custom_zh_myvoice01" \
  --audio "my_voice.wav" \
  --language 0 \
  --poll

# Step 2: Synthesize text using the cloned voice
python3 scripts/tts.py \
  --api-key "your-api-key" \
  --app-id "your-app-id" \
  --access-key "your-access-key" \
  --speaker "custom_zh_myvoice01" \
  --resource-id "seed-icl-2.0" \
  --text "This is audio generated with my cloned voice, does it sound like me?" \
  --output "my_cloned_voice.mp3"
```

---

## Notes

- **Audio URL expiration**: The download link for synthesized audio is valid for 1 hour only; the script will automatically download it locally.
- **Postpaid voices**: The first TTS synthesis call incurs a voice slot fee; be sure to preview the result first to confirm quality.
- **Text length**: Up to 100,000 characters per request; for longer texts, consider splitting into segments.
- **Shared concurrency between TTS and cloning APIs**: It is recommended to allocate 1 concurrency each for submit and query operations.
- **Voice selection**: See [references/api-params.md](references/api-params.md) for the list of public voices.
