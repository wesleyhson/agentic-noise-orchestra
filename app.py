# PATCH PYDUB FIRST
exec(open('pydub_patch.py').read())

from flask import Flask, send_file, render_template
import os
import json
import time
import random
import threading
from pydub import AudioSegment
from pydub.generators import Sine, Triangle, Sawtooth

app = Flask(__name__, template_folder='.')

# CONFIG
SOUND_LOG   = "sounds.jsonl"
OUTPUT_MP3  = "output.mp3"
VOTE_LOG    = "votes.jsonl"
LOG_FILE    = "terminal_log.txt"
MAX_TRACKS  = 6
BASE_DURATION_MS = 6000

# 6 AGENTS
INSTRUMENTS = {
    "Luna":     {"base_freq": 220, "gain": -14},
    "Sol":      {"base_freq": 110, "gain": -10},
    "Aurora":   {"base_freq": 880, "gain": -8},
    "Nimbus":   {"base_freq": 330, "gain": -12},
    "Echo":     {"base_freq": 440, "gain": -11},
    "Stella":   {"base_freq": 660, "gain": -9},
}

volume_boost = 0
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
    return send_file(OUTPUT_MP3, mimetype="audio/mpeg")

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

    mix = AudioSegment.silent(duration=BASE_DURATION_MS)

    for idx, entry in enumerate(recent):
        agent = entry["agent"]
        phoneme = entry["phoneme"]
        base_freq = INSTRUMENTS[agent]["base_freq"]
        gain = INSTRUMENTS[agent]["gain"]
        position_ms = idx * 1000
        duration = 1500
        freq = base_freq + len(phoneme) * 20

        if agent == "Luna":
            sound = Triangle(freq).to_audio_segment(duration).apply_gain(gain)
        elif agent == "Sol":
            sound = Sine(freq * 0.5).to_audio_segment(duration).apply_gain(gain)
        elif agent == "Aurora":
            sound = Sine(freq * 2).to_audio_segment(duration).apply_gain(gain)
        elif agent == "Nimbus":
            sound = Sine(freq).to_audio_segment(duration).apply_gain(gain-3)
        elif agent == "Echo":
            sound = Sawtooth(freq).to_audio_segment(duration).apply_gain(gain)
        elif agent == "Stella":
            sound = Sine(freq * 3).to_audio_segment(duration).apply_gain(gain)
        else:
            continue

        sound = sound.apply_gain(volume_boost)
        mix = mix.overlay(sound, position_ms)

    mix = mix.apply_gain(4)
    mix.export(OUTPUT_MP3, format="mp3")
    last_update = time.time()
    log("AUDIO EXPORTED")

def auto_cycle():
    log("AUTO CYCLE STARTED")
    while True:
        time.sleep(6)
        agent = random.choice(list(INSTRUMENTS.keys()))
        phoneme = random.choice(["o", "a", "i", "u", "e"]) * 3
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

    log("ORCHESTRA STARTING")
    for _ in range(3):
        agent = random.choice(list(INSTRUMENTS.keys()))
        phoneme = random.choice(["o", "a", "i", "u", "e"]) * 3
        entry = {"agent": agent, "phoneme": phoneme, "ts": time.time()}
        with open(SOUND_LOG, "a") as f:
            json.dump(entry, f)
            f.write("\n")
        log(f"{agent} sings \"{phoneme}\"")
        time.sleep(0.5)

    generate_audio()
    threading.Thread(target=auto_cycle, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
