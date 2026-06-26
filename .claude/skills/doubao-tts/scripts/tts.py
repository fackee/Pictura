#!/usr/bin/env python3
"""
Text-to-speech script: submit a TTS task, poll for results, and download the audio.

Usage (new console authentication):
  python3 tts.py --api-key YOUR_KEY --app-id APP_ID --access-key ACCESS_KEY \
    --speaker zh_female_shuangkuaisisi_moon_bigtts --text "Hello world" --output hello.mp3

Usage (cloned voice):
  python3 tts.py --api-key YOUR_KEY --app-id APP_ID --access-key ACCESS_KEY \
    --speaker S_xxxxxxx --resource-id seed-icl-2.0 --text "Cloned voice synthesis" --output out.mp3

Usage (read long text from file):
  python3 tts.py --api-key YOUR_KEY --app-id APP_ID --access-key ACCESS_KEY \
    --speaker zh_female_shuangkuaisisi_moon_bigtts --text-file article.txt --output article.mp3

Dependencies: pip install requests
"""

import argparse
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
SUBMIT_PATH = "/api/v3/tts/submit"
QUERY_PATH = "/api/v3/tts/query"

VALID_FORMATS = {"mp3", "ogg_opus", "pcm", "wav"}
VALID_SAMPLE_RATES = {8000, 16000, 22050, 24000, 32000, 44100, 48000}
VALID_RESOURCE_IDS = {"seed-tts-1.0", "seed-tts-2.0", "seed-icl-1.0", "seed-icl-2.0",
                      "volc.service_type.10029", "seed-icl-1.0-concurr"}

TASK_STATUS_MAP = {
    1: "Running (synthesizing)",
    2: "Success (synthesis complete)",
    3: "Failure (synthesis failed)",
}


def build_tts_headers(resource_id, api_key=None, app_id=None, access_key=None):
    """TTS submit/query endpoints use X-Api-App-Id + X-Api-Access-Key authentication (legacy).
    The new console recommends using X-Api-Key, but App-Id and Access-Key are still needed for Resource authentication."""
    headers = {
        "Content-Type": "application/json",
        "X-Api-Request-Id": str(uuid.uuid4()),
        "X-Api-Resource-Id": resource_id,
    }
    # TTS API authentication: the new console's api_key does not directly replace App-Id/Access-Key
    # Per documentation, TTS submit/query uses X-Api-App-Id + X-Api-Access-Key
    if app_id and access_key:
        headers["X-Api-App-Id"] = app_id
        headers["X-Api-Access-Key"] = access_key
    elif api_key:
        # New console: use X-Api-Key header
        headers["X-Api-Key"] = api_key
    else:
        print("Error: (--app-id + --access-key) or --api-key is required", file=sys.stderr)
        sys.exit(1)
    return headers


def read_text(args):
    if args.text:
        return args.text
    if args.text_file:
        if not os.path.isfile(args.text_file):
            print(f"Error: Text file not found: {args.text_file}", file=sys.stderr)
            sys.exit(1)
        with open(args.text_file, encoding="utf-8") as f:
            text = f.read()
        if len(text) > 100000:
            print(f"Error: Text exceeds the 100,000 character limit (current: {len(text)} characters)", file=sys.stderr)
            sys.exit(1)
        return text
    print("Error: --text or --text-file is required", file=sys.stderr)
    sys.exit(1)


def submit_task(text, args):
    headers = build_tts_headers(
        args.resource_id,
        api_key=args.api_key,
        app_id=args.app_id,
        access_key=args.access_key,
    )

    audio_params = {
        "format": args.format,
        "sample_rate": args.sample_rate,
        "speech_rate": args.speech_rate,
        "loudness_rate": args.loudness,
    }
    if args.emotion:
        audio_params["emotion"] = args.emotion
    if args.timestamps:
        audio_params["enable_timestamp"] = True

    additions = {}
    if args.language:
        additions["explicit_language"] = args.language
    if args.disable_markdown_filter:
        additions["disable_markdown_filter"] = True

    req_params = {
        "text": text,
        "speaker": args.speaker,
        "audio_params": audio_params,
    }
    if additions:
        req_params["additions"] = json.dumps(additions)

    body = {
        "user": {"uid": "skill-user"},
        "unique_id": str(uuid.uuid4()).replace("-", "")[:32],
        "req_params": req_params,
    }

    print(f"Submitting TTS task...")
    print(f"  Voice: {args.speaker}")
    print(f"  Resource: {args.resource_id}")
    print(f"  Format: {args.format} {args.sample_rate}Hz")
    print(f"  Text length: {len(text)} characters")

    resp = requests.post(BASE_URL + SUBMIT_PATH, headers=headers, json=body, timeout=30)

    if resp.status_code != 200:
        try:
            err = resp.json()
            print(f"Error: HTTP {resp.status_code} - code={err.get('code')} {err.get('message')}", file=sys.stderr)
        except Exception:
            print(f"Error: HTTP {resp.status_code}\n{resp.text}", file=sys.stderr)
        sys.exit(1)

    result = resp.json()
    if result.get("code") != 20000000:
        print(f"Error: Submission failed, code={result.get('code')} {result.get('message')}", file=sys.stderr)
        sys.exit(1)

    task_id = result["data"]["task_id"]
    print(f"Task submitted, task_id: {task_id}")
    return task_id, headers


def poll_task(task_id, headers, args):
    query_body = {"task_id": task_id}
    # The query endpoint requires a new request-id
    print(f"\nPolling task status (interval: {args.poll_interval}s)...")

    while True:
        time.sleep(args.poll_interval)
        headers["X-Api-Request-Id"] = str(uuid.uuid4())
        resp = requests.post(BASE_URL + QUERY_PATH, headers=headers, json=query_body, timeout=30)

        if resp.status_code != 200:
            print(f"Query failed: HTTP {resp.status_code}, retrying...")
            continue

        result = resp.json()
        if result.get("code") != 20000000:
            print(f"Query error: code={result.get('code')} {result.get('message')}, retrying...")
            continue

        data = result.get("data", {})
        status = data.get("task_status", 1)
        print(f"Status: {TASK_STATUS_MAP.get(status, status)}")

        if status == 2:
            audio_url = data.get("audio_url", "")
            print(f"\nSynthesis successful!")
            print(f"Audio URL: {audio_url}")
            print(f"(URL is valid for 1 hour)")

            if args.timestamps and data.get("sentences"):
                print("\nSubtitle timestamps:")
                for sent in data["sentences"]:
                    print(f"  [{sent['startTime']:.3f}s - {sent['endTime']:.3f}s] {sent['text']}")

            return audio_url

        elif status == 3:
            print(f"Synthesis failed, task_id={task_id}", file=sys.stderr)
            sys.exit(1)


def download_audio(audio_url, output_path):
    print(f"\nDownloading audio to: {output_path}")
    resp = requests.get(audio_url, timeout=60, stream=True)
    if resp.status_code != 200:
        print(f"Error: Download failed, HTTP {resp.status_code}", file=sys.stderr)
        sys.exit(1)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    size = os.path.getsize(output_path)
    print(f"Download complete: {output_path} ({size / 1024:.1f} KB)")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Text-to-speech: submit a task, poll for results, and download audio")

    # Authentication (CLI arguments take priority, then environment variables/.env)
    auth = parser.add_argument_group("Authentication (can also be configured via .env or environment variables)")
    auth.add_argument("--api-key", default=os.environ.get("DOUBAO_API_KEY"),
                      help="New console API Key (can also set DOUBAO_API_KEY)")
    auth.add_argument("--app-id", default=os.environ.get("DOUBAO_APP_ID"),
                      help="Legacy console App ID (can also set DOUBAO_APP_ID)")
    auth.add_argument("--access-key", default=os.environ.get("DOUBAO_ACCESS_KEY"),
                      help="Legacy console Access Key (can also set DOUBAO_ACCESS_KEY)")

    # Synthesis parameters
    parser.add_argument("--speaker", required=True, help="Voice ID (required)")
    parser.add_argument("--resource-id", default="seed-tts-1.0",
                        help=f"Resource ID (default: seed-tts-1.0), options: {', '.join(sorted(VALID_RESOURCE_IDS))}")

    # Text input
    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", help="Text to synthesize (up to 100,000 characters)")
    text_group.add_argument("--text-file", help="Read synthesis text from file")

    # Audio parameters
    parser.add_argument("--format", default="mp3", choices=list(VALID_FORMATS),
                        help="Audio format (default: mp3)")
    parser.add_argument("--sample-rate", type=int, default=24000,
                        help=f"Sample rate (default: 24000), options: {sorted(VALID_SAMPLE_RATES)}")
    parser.add_argument("--speech-rate", type=int, default=0,
                        help="Speech rate [-50, 100], 100=2x speed (default: 0)")
    parser.add_argument("--loudness", type=int, default=0,
                        help="Volume [-50, 100], 100=2x volume (default: 0)")
    parser.add_argument("--emotion", default=None,
                        help="Emotion (e.g. happy/sad/angry, requires voice support)")
    parser.add_argument("--language", default=None,
                        help="Explicit language (zh-cn/en/crosslingual/es-mx/id/pt-br, etc.)")
    parser.add_argument("--timestamps", action="store_true",
                        help="Return subtitle timestamps")
    parser.add_argument("--disable-markdown-filter", action="store_true",
                        help="Parse and filter Markdown syntax")

    # Output
    parser.add_argument("--output", default="output.mp3", help="Output audio file path (default: output.mp3)")
    parser.add_argument("--poll-interval", type=int, default=5, help="Polling interval in seconds (default: 5)")

    args = parser.parse_args()

    # Parameter validation
    if not args.api_key and not (args.app_id and args.access_key):
        print("Error: --api-key or (--app-id + --access-key) is required", file=sys.stderr)
        sys.exit(1)

    if args.sample_rate not in VALID_SAMPLE_RATES:
        print(f"Error: --sample-rate must be one of {sorted(VALID_SAMPLE_RATES)}", file=sys.stderr)
        sys.exit(1)

    if not (-50 <= args.speech_rate <= 100):
        print("Error: --speech-rate must be in the range [-50, 100]", file=sys.stderr)
        sys.exit(1)

    if not (-50 <= args.loudness <= 100):
        print("Error: --loudness must be in the range [-50, 100]", file=sys.stderr)
        sys.exit(1)

    text = read_text(args)
    task_id, headers = submit_task(text, args)
    audio_url = poll_task(task_id, headers, args)
    download_audio(audio_url, args.output)


if __name__ == "__main__":
    main()
