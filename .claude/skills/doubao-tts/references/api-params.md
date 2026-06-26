# Doubao TTS API Parameter Reference

## API Endpoints

| Endpoint | URL |
|----------|-----|
| Voice Clone Training | `POST https://openspeech.bytedance.com/api/v3/tts/voice_clone` |
| Voice Status Query | `POST https://openspeech.bytedance.com/api/v3/tts/get_voice` |
| TTS Task Submit | `POST https://openspeech.bytedance.com/api/v3/tts/submit` |
| TTS Task Query | `POST https://openspeech.bytedance.com/api/v3/tts/query` |

---

## Authentication Methods

### New Console (Recommended)
```
X-Api-Key: your-api-key
```

### Legacy Console - Cloning Endpoint
```
X-Api-App-Key: your-app-key
X-Api-Access-Key: your-access-key
```

### Legacy Console - TTS Endpoint
```
X-Api-App-Id: your-app-id
X-Api-Access-Key: your-access-key
X-Api-Resource-Id: seed-tts-1.0
```

---

## Resource IDs (X-Api-Resource-Id)

| Resource ID | Description | Billing |
|-------------|-------------|---------|
| `seed-tts-1.0` | Doubao Speech Synthesis 1.0 | Speech Synthesis Large Model |
| `seed-tts-2.0` | Doubao Speech Synthesis 2.0 | Speech Synthesis Large Model |
| `seed-icl-1.0` | Voice Cloning ICL 1.0 character-based | Voice Cloning Large Model |
| `seed-icl-1.0-concurr` | Voice Cloning ICL 1.0 concurrency-based | Voice Cloning Large Model |
| `seed-icl-2.0` | Voice Cloning ICL 2.0 character-based | Voice Cloning Large Model |
| `volc.service_type.10029` | Equivalent to seed-tts-1.0 | Speech Synthesis Large Model |

---

## TTS Main Parameters

### req_params

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes* | Text to synthesize (use either text or ssml) |
| `speaker` | string | Yes | Voice ID |
| `audio_params` | object | Yes | Audio parameters |
| `additions` | jsonstring | No | Extension parameters |

### audio_params

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | string | `mp3` | mp3 / ogg_opus / pcm / wav |
| `sample_rate` | int | `24000` | 8000/16000/22050/24000/32000/44100/48000 |
| `speech_rate` | int | `0` | Speech rate [-50, 100], 100=2x speed |
| `loudness_rate` | int | `0` | Volume [-50, 100] |
| `emotion` | string | - | Emotion value (requires voice support) |
| `emotion_scale` | int | `4` | Emotion intensity [1, 5] |
| `enable_timestamp` | bool | `false` | Return subtitle timestamps |

### additions (JSON string)

| Parameter | Type | Description |
|-----------|------|-------------|
| `explicit_language` | string | Explicit language (zh-cn/en/crosslingual/es-mx/id/pt-br, etc.) |
| `disable_markdown_filter` | bool | true=parse and filter Markdown |
| `silence_duration` | int | End-of-sentence silence duration (ms, 0~30000) |
| `enable_language_detector` | bool | Auto-detect language |
| `aigc_watermark` | bool | Append audio rhythm watermark at the end |
| `post_process.pitch` | int | Pitch [-12, 12] |

---

## Emotion Values (emotion)

Voices that support emotions can accept the following values (different voices support different emotions):

| Value | Meaning |
|-------|---------|
| `happy` | Happy |
| `sad` | Sad |
| `angry` | Angry |
| `fearful` | Fearful |
| `disgusted` | Disgusted |
| `surprised` | Surprised |
| `calm` | Calm |

---

## Languages (explicit_language)

| Value | Description |
|-------|-------------|
| `zh-cn` | Primarily Chinese, supports Chinese-English mixed |
| `en` | English only |
| `crosslingual` | Multilingual (includes zh/en/es-mx/id/pt-br) |
| `es-mx` | Mexican Spanish only |
| `id` | Indonesian only |
| `pt-br` | Brazilian Portuguese only |
| `de` | German only (DIT voices) |
| `fr` | French only (DIT voices) |

---

## Voice Cloning Parameters

### Training Endpoint (/api/v3/tts/voice_clone)

| Parameter | Required | Description |
|-----------|----------|-------------|
| `speaker_id` | Yes | Prepaid voice ID; or the fixed value `"custom_speaker_id"` |
| `custom_speaker_id` | No | Postpaid custom voice name (first character must be a letter, 8~256 characters) |
| `audio.data` | Yes | Base64-encoded audio |
| `audio.format` | Partially required | Required for pcm/m4a; optional for others |
| `language` | Recommended | 0=Chinese 1=English 2=Japanese 3=Spanish 4=Indonesian 5=Portuguese 8=Korean |
| `extra_params.demo_text` | No | Demo text for preview (4~300 characters) |
| `extra_params.enable_audio_denoise` | No | Enable denoising |
| `extra_params.voice_clone_enable_mss` | No | Enable source separation to remove background audio |
| `extra_params.enable_crop_by_asr` | No | ASR cropping to avoid cutting off words |

### Training Status Codes

| status | Meaning |
|--------|---------|
| 0 | NotFound |
| 1 | Training (in progress) |
| 2 | Success (available for synthesis) |
| 3 | Failed (failed) |
| 4 | Active (activated, available for synthesis) |

### model_type Meanings

| model_type | Meaning |
|------------|---------|
| 1 | Voice Cloning ICL V1 |
| 2 | Voice Cloning DiT Standard (timbre only, no style replication) |
| 3 | Voice Cloning DiT Full (timbre + accent + speech rate style) |
| 4 | Voice Cloning ICL V2 |
| 5 | Voice Cloning ICL V3 |

---

## TTS Task Status Codes

| task_status | Meaning |
|-------------|---------|
| 1 | Running (synthesizing) |
| 2 | Success (synthesis complete) |
| 3 | Failure (synthesis failed) |

---

## Common Public Voice Examples

| speaker ID | Description |
|------------|-------------|
| `zh_female_shuangkuaisisi_moon_bigtts` | Chinese female - Shuangkuaisisi |
| `zh_male_rapgod_mars_bigtts` | Chinese male - Rap voice |
| `BV120_streaming` | Chinese female - General purpose |
| `en_female_sharonrothstein_mars_bigtts` | English female |

For the complete voice list, refer to the Volcano Engine console or official documentation:
https://www.volcengine.com/docs/6561/1257544

---

## Error Codes

### TTS Endpoint

| code | Description |
|------|-------------|
| `20000000` | Success |
| `40000000` | Invalid request parameters |
| `40000001` | Task not found or expired |
| `40000002` | Duplicate reqid |
| `45000000` | Voice authentication failed or concurrency limit exceeded |
| `55000000` | Server error |

### Cloning Endpoint

| code | Description |
|------|-------------|
| `45001001` | Invalid parameters |
| `45001101` | Audio upload failed |
| `45001104` | Voiceprint detection not passed |
| `45001107` | speaker_id not found |
| `45001108` | Audio transcoding failed |
| `45001109` | WER detection error (audio does not match text) |
| `45001114` | Poor audio quality |
| `45001122` | ASR detected no human voice |
| `45001123` | Training limit reached |
| `45001126` | demo_text length error |
| `55001307` | Voice cloning failed (server exception) |

---

## Audio Format Notes

| Format | Description |
|--------|-------------|
| `mp3` | General purpose, default, suitable for most scenarios |
| `ogg_opus` | High compression ratio, suitable for network transmission |
| `pcm` | Raw PCM, suitable for real-time processing |
| `wav` | Lossless, larger file size (includes header) |

Note: For streaming scenarios, pcm is recommended over wav (to avoid multiple wav headers in responses).
