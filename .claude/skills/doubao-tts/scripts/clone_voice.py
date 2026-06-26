#!/usr/bin/env python3
"""
Voice cloning script: upload an audio sample to train a cloned voice, and query training status.

Usage (new console, recommended):
  python3 clone_voice.py --api-key YOUR_KEY --speaker-id S_xxx --audio sample.wav --poll

Usage (postpaid custom voice):
  python3 clone_voice.py --api-key YOUR_KEY --custom-speaker-id custom_zh_myvoice --audio sample.wav --poll

Usage (legacy console):
  python3 clone_voice.py --app-key APP_KEY --access-key ACCESS_KEY --speaker-id S_xxx --audio sample.wav

Dependencies: pip install requests
"""

import argparse
import base64
import json
import os
import sys
import time
import uuid


def load_dotenv():
    """Load environment variables from a .env file (script directory first, then parent directory). Does not overwrite existing environment variables."""
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

try:
    import requests
except ImportError:
    print("Error: requests is not installed. Please run: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://openspeech.bytedance.com"
CLONE_PATH = "/api/v3/tts/voice_clone"
GET_VOICE_PATH = "/api/v3/tts/get_voice"

LANGUAGE_MAP = {
    0: "Chinese", 1: "English", 2: "Japanese", 3: "Spanish",
    4: "Indonesian", 5: "Portuguese", 6: "German", 7: "French", 8: "Korean",
}

STATUS_MAP = {
    0: "NotFound (not found)",
    1: "Training (in progress)",
    2: "Success (training complete, available for synthesis)",
    3: "Failed (training failed)",
    4: "Active (activated, available for synthesis)",
}


def build_headers(api_key=None, app_key=None, access_key=None):
    headers = {
        "Content-Type": "application/json",
        "X-Api-Request-Id": str(uuid.uuid4()),
    }
    if api_key:
        headers["X-Api-Key"] = api_key
    elif app_key and access_key:
        headers["X-Api-App-Key"] = app_key
        headers["X-Api-Access-Key"] = access_key
    else:
        print("Error: --api-key or (--app-key + --access-key) is required", file=sys.stderr)
        sys.exit(1)
    return headers


def read_audio_base64(file_path):
    if not os.path.isfile(file_path):
        print(f"Error: Audio file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    size = os.path.getsize(file_path)
    if size > 10 * 1024 * 1024:
        print(f"Error: Audio file exceeds the 10MB limit (current: {size / 1024 / 1024:.1f}MB)", file=sys.stderr)
        sys.exit(1)
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_audio_format(file_path):
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    format_map = {"wav": "wav", "mp3": "mp3", "ogg": "ogg",
                  "m4a": "m4a", "aac": "aac", "pcm": "pcm"}
    return format_map.get(ext, "")


def clone_voice(args):
    headers = build_headers(args.api_key, args.app_key, args.access_key)

    audio_data = read_audio_base64(args.audio)
    audio_format = get_audio_format(args.audio)

    # Build request body
    body = {
        "audio": {
            "data": audio_data,
        },
        "language": args.language,
    }
    if audio_format in ("pcm", "m4a"):
        body["audio"]["format"] = audio_format
    elif audio_format:
        body["audio"]["format"] = audio_format

    # Voice ID
    if args.custom_speaker_id:
        body["speaker_id"] = "custom_speaker_id"
        body["custom_speaker_id"] = args.custom_speaker_id
        print(f"Postpaid custom voice: {args.custom_speaker_id}")
        print("Note: The first TTS synthesis call incurs a voice slot fee. Please preview the result first!")
    else:
        body["speaker_id"] = args.speaker_id
        print(f"Prepaid voice: {args.speaker_id}")

    # extra_params
    extra_params = {}
    if args.denoise:
        extra_params["enable_audio_denoise"] = True
    if args.demo_text:
        if not (4 <= len(args.demo_text) <= 300):
            print("Error: --demo-text length must be between 4 and 300 characters", file=sys.stderr)
            sys.exit(1)
        extra_params["demo_text"] = args.demo_text
    if extra_params:
        body["extra_params"] = extra_params

    print(f"\nSubmitting voice cloning training (language: {LANGUAGE_MAP.get(args.language, args.language)})...")
    resp = requests.post(BASE_URL + CLONE_PATH, headers=headers, json=body, timeout=60)

    if resp.status_code != 200:
        try:
            err = resp.json()
            print(f"Error: HTTP {resp.status_code} - code={err.get('code')} message={err.get('message')}", file=sys.stderr)
        except Exception:
            print(f"Error: HTTP {resp.status_code}\n{resp.text}", file=sys.stderr)
        sys.exit(1)

    result = resp.json()
    _print_voice_status(result)

    status = result.get("status", 0)
    if args.poll and status not in (2, 4):
        _poll_voice_status(args, headers)
    elif status in (2, 4):
        print("\nThe voice is available. You can use this speaker_id for TTS synthesis.")


def _poll_voice_status(args, headers):
    speaker_id = args.custom_speaker_id or args.speaker_id
    body = {"speaker_id": "custom_speaker_id", "custom_speaker_id": speaker_id} \
        if args.custom_speaker_id else {"speaker_id": speaker_id}

    print(f"\nStarting to poll training status (interval: {args.poll_interval}s)...")
    while True:
        time.sleep(args.poll_interval)
        headers["X-Api-Request-Id"] = str(uuid.uuid4())
        resp = requests.post(BASE_URL + GET_VOICE_PATH, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            print(f"Query failed: HTTP {resp.status_code}, retrying...")
            continue
        result = resp.json()
        status = result.get("status", 0)
        print(f"Current status: {STATUS_MAP.get(status, status)}")
        if status == 2:
            print("\nTraining successful!")
            _print_voice_status(result)
            print("\nThe voice is available. You can use this speaker_id for TTS synthesis.")
            break
        elif status == 4:
            print("\nThe voice is activated and available for synthesis.")
            _print_voice_status(result)
            break
        elif status == 3:
            print("\nTraining failed. Please check audio quality or resubmit.", file=sys.stderr)
            sys.exit(1)


def _print_voice_status(result):
    print("\n--- Voice Training Result ---")
    print(f"speaker_id:          {result.get('speaker_id', 'N/A')}")
    print(f"status:              {STATUS_MAP.get(result.get('status'), result.get('status'))}")
    print(f"language:            {LANGUAGE_MAP.get(result.get('language'), result.get('language'))}")
    print(f"available_training_times: {result.get('available_training_times', 'N/A')}")
    speaker_status = result.get("speaker_status", [])
    for ss in speaker_status:
        model_type = ss.get("model_type", "?")
        demo_audio = ss.get("demo_audio", "")
        print(f"model_type={model_type}: demo_audio={demo_audio or '(none)'}")


def query_voice(args):
    headers = build_headers(args.api_key, args.app_key, args.access_key)
    if args.custom_speaker_id:
        body = {"speaker_id": "custom_speaker_id", "custom_speaker_id": args.custom_speaker_id}
    else:
        body = {"speaker_id": args.speaker_id}

    resp = requests.post(BASE_URL + GET_VOICE_PATH, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        print(f"Error: HTTP {resp.status_code}\n{resp.text}", file=sys.stderr)
        sys.exit(1)
    _print_voice_status(resp.json())


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Voice cloning: train a cloned voice and query status")

    # Authentication (CLI arguments take priority, then environment variables/.env)
    auth = parser.add_argument_group("Authentication (choose one: new or legacy console; can also be configured via .env or environment variables)")
    auth.add_argument("--api-key", default=os.environ.get("DOUBAO_API_KEY"),
                      help="New console API Key (recommended; can also set DOUBAO_API_KEY)")
    auth.add_argument("--app-key", default=os.environ.get("DOUBAO_APP_KEY"),
                      help="Legacy console App Key (can also set DOUBAO_APP_KEY)")
    auth.add_argument("--access-key", default=os.environ.get("DOUBAO_ACCESS_KEY"),
                      help="Legacy console Access Key (can also set DOUBAO_ACCESS_KEY)")

    # Voice ID
    sid = parser.add_mutually_exclusive_group()
    sid.add_argument("--speaker-id", help="Prepaid voice ID (e.g. S_xxxxxxx)")
    sid.add_argument("--custom-speaker-id",
                     help="Postpaid custom voice ID (first character must be a letter; allows letters/numbers/-/_; length 8~256)")

    # Operation mode
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--audio", help="Audio file path (training mode)")
    mode.add_argument("--query-only", action="store_true", help="Only query existing voice status (no audio upload)")

    # Training parameters
    parser.add_argument("--language", type=int, default=0,
                        help="Language: 0=Chinese(default) 1=English 2=Japanese 3=Spanish 4=Indonesian 5=Portuguese 8=Korean")
    parser.add_argument("--denoise", action="store_true", help="Enable denoising (recommended when audio has significant noise)")
    parser.add_argument("--demo-text", help="Demo text for preview (4~300 characters, optional)")

    # Polling
    parser.add_argument("--poll", action="store_true", help="Continuously poll until training is complete")
    parser.add_argument("--poll-interval", type=int, default=10, help="Polling interval in seconds (default: 10)")

    args = parser.parse_args()

    # Validate authentication
    if not args.api_key and not (args.app_key and args.access_key):
        print("Error: --api-key or (--app-key + --access-key) is required", file=sys.stderr)
        sys.exit(1)

    if args.query_only:
        if not args.speaker_id and not args.custom_speaker_id:
            print("Error: --query-only mode requires --speaker-id or --custom-speaker-id", file=sys.stderr)
            sys.exit(1)
        query_voice(args)
    else:
        if not args.audio:
            print("Error: Training mode requires --audio", file=sys.stderr)
            sys.exit(1)
        if not args.speaker_id and not args.custom_speaker_id:
            print("Error: --speaker-id or --custom-speaker-id is required", file=sys.stderr)
            sys.exit(1)
        clone_voice(args)


if __name__ == "__main__":
    main()
