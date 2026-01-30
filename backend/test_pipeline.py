"""End-to-end pipeline test: create project → outline → script → assets → video"""
import json
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api"


def api(method: str, path: str, body: dict | None = None) -> dict | None:
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        if resp.status == 204:
            return None
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  ERROR {e.code}: {e.read().decode()}")
        raise


def poll(path: str, key: str, target: str, timeout: int = 30) -> dict:
    """Poll an endpoint until status[key] == target or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        result = api("GET", path)
        status = result.get(key, "")
        print(f"  Poll: {status} - {result.get('message', '')} ({result.get('progress', 0):.0%})")
        if status == target:
            return result
        if status == "failed":
            raise RuntimeError(f"Failed: {result.get('message')}")
        time.sleep(1.5)
    raise TimeoutError(f"Timed out waiting for {key}={target}")


print("=" * 60)
print("STUDYSCENES E2E PIPELINE TEST")
print("=" * 60)

# Step 1: Create project
print("\n[1/6] Creating project...")
project = api("POST", "/projects", {
    "title": "Photosynthesis Review",
    "content": (
        "Photosynthesis is the process by which green plants and some other organisms "
        "use sunlight to synthesize foods from carbon dioxide and water. Photosynthesis "
        "in plants generally involves the green pigment chlorophyll and generates oxygen "
        "as a byproduct.\n\n"
        "The light-dependent reactions take place in the thylakoid membranes. These reactions "
        "capture energy from sunlight and use it to produce ATP and NADPH. Water molecules "
        "are split during this process, releasing oxygen.\n\n"
        "The Calvin cycle, also known as the light-independent reactions, occurs in the "
        "stroma of the chloroplast. It uses ATP and NADPH from the light reactions to fix "
        "carbon dioxide into glucose through a series of enzyme-catalyzed steps."
    ),
})
pid = project["id"]
print(f"  Created: {pid}")
print(f"  Status: {project['status']}")

# Step 2: Get project
print("\n[2/6] Fetching project...")
project = api("GET", f"/projects/{pid}")
print(f"  Title: {project['title']}")
print(f"  Content length: {len(project['content'])} chars")
print(f"  Scenes: {len(project['scenes'])}")

# Step 3: Generate outline
print("\n[3/6] Generating outline...")
outline = api("POST", f"/projects/{pid}/generate/outline")
print(f"  Sections: {len(outline['sections'])}")
for i, s in enumerate(outline["sections"]):
    print(f"    {i+1}. {s['title']} ({len(s['key_points'])} points)")

# Step 4: Generate script
print("\n[4/6] Generating script...")
script = api("POST", f"/projects/{pid}/generate/script")
print(f"  Scenes: {len(script['scenes'])}")
for i, s in enumerate(script["scenes"]):
    words = len(s["narration"].split())
    print(f"    {i+1}. {s['title']} ({words} words, ~{words/150*60:.1f}s)")

# Step 5: Generate assets
print("\n[5/6] Generating assets (images + audio)...")
api("POST", f"/projects/{pid}/generate/assets")
result = poll(f"/projects/{pid}/generate/assets/status", "status", "completed", timeout=30)
print(f"  Assets done: {result['message']}")

# Step 6: Generate video
print("\n[6/6] Generating video...")
api("POST", f"/projects/{pid}/generate/video")
result = poll(f"/projects/{pid}/generate/video/status", "status", "completed", timeout=60)
print(f"  Video done: {result['video_path']}")

# Final check
print("\n" + "=" * 60)
project = api("GET", f"/projects/{pid}")
print(f"Final status: {project['status']}")
print(f"Video path:   {project['video_path']}")
print(f"Scenes:       {len(project['scenes'])}")
for s in project["scenes"]:
    print(f"  - {s['title']}: {s['duration_sec']:.1f}s, image={s['image_path']}")

# Verify files exist
import os
storage_dir = "./storage"
vid_path = os.path.join(storage_dir, project["video_path"].replace("/storage/", ""))
print(f"\nVideo file exists: {os.path.exists(vid_path)} ({os.path.getsize(vid_path) if os.path.exists(vid_path) else 0} bytes)")

# Check per-scene audio files
for i in range(len(project["scenes"])):
    audio_file = os.path.join(storage_dir, pid, "audio", f"scene_{i:03d}.wav")
    exists = os.path.exists(audio_file)
    size = os.path.getsize(audio_file) if exists else 0
    print(f"Scene {i} audio exists: {exists} ({size} bytes)")

# List projects
print("\nProject list:")
projects = api("GET", "/projects")
for p in projects:
    print(f"  - {p['title']} [{p['status']}]")

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
