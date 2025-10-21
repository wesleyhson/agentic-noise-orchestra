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

VOTE_OPTIONS = ["louder", "softer", "higher", "lower", "slower", "faster"]

# STATE
volume_boost = 0
pitch_shift = 0
tempo_factor = 1.0
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
        phoneme = entry["phoneme"]
        agent = entry["agent"]
        base_freq = INSTRUMENTS[agent]["base_freq"]
        gain = INSTRUMENTS[agent]["gain"]
        position_ms = idx * 1000

        duration = min(2000, len(phoneme) * 200 + 600)
        freq = (base_freq + len(phoneme) * 20 + pitch_shift) * tempo_factor
        if "o" in phoneme: freq *= 1.5
        if "i" in phoneme: freq *= 2

        if agent == "Luna":
            sound = Triangle(freq).to_audio_segment(int(duration*tempo_factor)).low_pass_filter(800).apply_gain(gain).fade_in(200).fade_out(300)
        elif agent == "Sol":
            sound = Sine(freq * 0.5).to_audio_segment(int(duration*tempo_factor)).low_pass_filter(200).apply_gain(gain).fade_in(100)
        elif agent == "Aurora":
            sound = Sine(freq * 2).to_audio_segment(1600).apply_gain(gain).fade_out(800)
        elif agent == "Nimbus":
            chord = sum(Sine(f).to_audio_segment(int(duration*tempo_factor)).apply_gain(gain-3) for f in [freq, freq*1.25, freq*1.5])
            sound = chord.low_pass_filter(1200).fade_in(300).fade_out(400)
        elif agent == "Echo":
            sound = Sawtooth(freq).to_audio_segment(int(duration*tempo_factor)).low_pass_filter(1500).apply_gain(gain).fade_in(200).fade_out(500)
        elif agent == "Stella":
            sound = Sine(freq * 3).to_audio_segment(2000).apply_gain(gain).fade_out(1000)
        else:
            continue

        sound = sound.apply_gain(volume_boost)
        mix = mix.overlay(sound, position_ms)

    try:
        mix = mix.apply_gain(4)
        mix.export(OUTPUT_MP3, format="mp3")
        last_update = time.time()
        log(f"EXPORTED 6s loop ({os.path.getsize(OUTPUT_MP3)} bytes)")
    except Exception as e:
        log(f"EXPORT FAILED: {e}")

def auto_cycle():
    log("AUTO CYCLE STARTED")
    while True:
        time.sleep(6)
        agent = random.choice(list(INSTRUMENTS.keys()))
        phoneme = random.choice(["o", "a", "i", "u", "e", "m", "n", "s"]) * random.randint(1, 4)
        entry = {"phoneme": phoneme, "agent": agent, "ts": time.time()}
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
        phoneme = random.choice(["o", "a", "i", "u", "e", "m", "n", "s"]) * random.randint(1, 4)
        entry = {"phoneme": phoneme, "agent": agent, "ts": time.time()}
        with open(SOUND_LOG, "a") as f:
            json.dump(entry, f)
            f.write("\n")
        log(f"{agent} sings \"{phoneme}\"")
        time.sleep(0.5)
    generate_audio()
    threading.Thread(target=auto_cycle, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
