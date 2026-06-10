import requests
import base64
import time
import sys
import os

def transcribe_audio(file_path, api_key):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    with open(file_path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    mime_map = {'ogg': 'audio/ogg', 'wav': 'audio/wav', 'mp3': 'audio/mpeg', 'm4a': 'audio/mp4'}
    mime_type = mime_map.get(ext, 'audio/ogg')
    data_url = f"data:{mime_type};base64,{audio_b64}"

    url = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    payload = {"model": "paraformer-v2", "input": {"file_urls": [data_url]}}

    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        task_id = resp.json()["output"]["task_id"]
        print(f"Task submitted: {task_id}", file=sys.stderr)
    except Exception as e:
        return f"Submission failed: {e}"

    task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    for _ in range(30):
        time.sleep(2)
        try:
            status_resp = requests.get(task_url, headers={"Authorization": f"Bearer {api_key}"})
            status_resp.raise_for_status()
            output = status_resp.json()["output"]
            status = output["task_status"]
            if status == "SUCCEEDED":
                trans_url = output["results"][0]["transcription_url"]
                result = requests.get(trans_url).json()
                return result["transcripts"][0]["text"]
            elif status in ["FAILED", "CANCELED"]:
                return f"Task failed: {output.get('message', 'Unknown error')}"
        except Exception:
            continue

    return "Timeout waiting for transcription."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file_path>")
        sys.exit(1)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("Error: DASHSCOPE_API_KEY not set.")
        sys.exit(1)

    print(transcribe_audio(sys.argv[1], api_key))
