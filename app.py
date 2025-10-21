from flask import Flask, send_file, render_template
import os
import json
import time
import random
import threading
import numpy as np
from scipy.io import wavfile
from io import BytesIO

app = Flask(__name__, template_folder='templates')

# CONFIG
SOUND_LOG   = "sounds.jsonl"
OUTPUT_MP3  = "output.wav"
VOTE_LOG    = "votes.jsonl"  # ← THIS WAS MISSING
LOG_FILE    = "terminal_log.txt"
MAX_TRACKS  = 6
BASE_DURATION_MS = 6000
SAMPLE_RATE = 44100

# 6 AGENTS
INSTRUMENTS = {
    "Luna":     {"freq": 220, "gain": 0.3},
    "Sol":      {"freq": 110, "gain": 0.4},
    "Aurora":   {"freq": 880, "gain": 0.3},
    "Nimbus":   {"freq": 330, "gain": 0.4},
    "Echo":     {"freq": 440, "gain": 0.3},
    "Stella":   {"freq": 660, "gain": 0.3},
}

volume_boost = 0.5
last_update = 0

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    if not os.path.exists(OUTPUT_MP3):
        return "", 404
    return send_file(OUTPUT_MP3, mimetype="audio/wav")

@app.route("/log")
def get_log():
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE) as f:
        lines = f.readlines()[-30:]
    return "".join(f"<div class='logline'>{line.rstrip()}</div>" for line in lines)

def generate_audio():
    global last_update
    log("GENERATING 6-SECOND LOOP")
    recent = []
    if os.path.exists(SOUND_LOG):
        with open(SOUND_LOG) as f:
            recent = [json.loads(l) for l in f.readlines()[-MAX_TRACKS:]]

    duration_seconds = 6
    t = np.linspace(0, duration_seconds, int(SAMPLE_RATE * duration_seconds), endpoint=False)
    mix = np.zeros(len(t))

    for idx, entry in enumerate(recent):
        agent = entry["agent"]
        phoneme = entry["phoneme"]
        freq = INSTRUMENTS[agent]["freq"] + len(phoneme) * 10
        gain = INSTRUMENTS[agent]["gain"] * volume_boost
        start_time = idx * 1.0
        end_time = start_time + 1.0
        mask = (t >= start_time) & (t < end_time)
        wave = np.sin(2 * np.pi * freq * t[mask])
        mix[mask] += gain * wave

    mix = (mix * 32767).astype(np.int16)
    wav_io = BytesIO()
    wavfile.write(wav_io, SAMPLE_RATE, mix)
    wav_io.seek(0)
    with open(OUTPUT_MP3, 'wb') as f:
        f.write(wav_io.getvalue())
    last_update = time.time()
    log(f"EXPORTED 6s loop")

def auto_cycle():
    log("AUTO CYCLE STARTED")
    while True:
        time.sleep(6)
        agent = random.choice(list(INSTRUMENTS.keys()))
        phoneme = random.choice(["o", "a", "i", "u", "e"]) * random.randint(1, 4)
        entry = {"agent": agent, "phoneme": phoneme, "ts": time.time()}
        with open(SOUND_LOG, "a") as f:
            json.dump(entry, f)
            f.write("\n")
        log(f"{agent} sings \"{phoneme}\"")
        generate_audio()

if __name__ == "__main__":
    for f in [SOUND_LOG, VOTE_LOG, LOG_FILE]:
        if os.path.exists(f): os.remove(f)
        open(f, "a").close()
    log("AGENTIC NOISE ORCHESTRA — INITIALIZING")
    for _ in range(3):
        agent = random.choice(list(INSTRUMENTS.keys()))
        phoneme = random.choice(["o", "a", "i", "u", "e"]) * random.randint(1, 4)
        entry = {"agent": agent, "phoneme": phoneme, "ts": time.time()}
        with open(SOUND_LOG, "a") as f:
            json.dump(entry, f)
            f.write("\n")
        log(f"{agent} sings \"{phoneme}\"")
        time.sleep(0.5)
    generate_audio()
    threading.Thread(target=auto_cycle, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
