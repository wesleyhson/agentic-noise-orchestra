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

# EXPANDED VOCALIZATIONS
PHONEMES = [
    "o", "a", "i", "u", "e",
    "ah", "oh", "ee", "oo", "eh",
    "la", "na", "ma", "ra", "da",
    "lo", "no", "mo", "ro", "do",
    "li", "ni", "mi", "ri", "di",
    "hum", "hmm", "ahh", "ooo", "eee",
    "wow", "yay", "oof", "bah", "doh"
]

# SOUND PARAMETERS (modified by voting)
SOUND_PARAMS = {
    "volume_boost": 0.5,      # Overall mix volume
    "complexity": 6,          # How many agents can sing at once
    "pitch_shift": 0,         # Global pitch adjustment in Hz
    "decay": 0.0,             # Fade out effect (0 = none, 1 = strong)
}

# VOTING OPTIONS for sound parameters
VOTE_OPTIONS = {
    "LOUDER": {"param": "volume_boost", "change": +0.1, "desc": "increase volume"},
    "QUIETER": {"param": "volume_boost", "change": -0.1, "desc": "decrease volume"},
    "MORE_COMPLEX": {"param": "complexity", "change": +1, "desc": "add more voices"},
    "SIMPLER": {"param": "complexity", "change": -1, "desc": "fewer voices"},
    "PITCH_UP": {"param": "pitch_shift", "change": +20, "desc": "raise pitch"},
    "PITCH_DOWN": {"param": "pitch_shift", "change": -20, "desc": "lower pitch"},
    "ADD_DECAY": {"param": "decay", "change": +0.15, "desc": "add fade effect"},
    "LESS_DECAY": {"param": "decay", "change": -0.15, "desc": "reduce fade"},
}

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
        lines = f.readlines()[-100:]
    return "".join(f"<div class='logline'>{line.rstrip()}</div>" for line in lines)

def generate_waveform(waveform_type, freq, t):
    """Generate soft, hypnotic waveforms"""
    # Primarily use sine waves for smoothness
    base = np.sin(2 * np.pi * freq * t)
    
    if waveform_type == "dreamy":
        # Add gentle vibrato for hypnotic effect
        vibrato = np.sin(2 * np.pi * 2.5 * t) * 0.08
        return np.sin(2 * np.pi * freq * t * (1 + vibrato))
    elif waveform_type == "soft":
        # Soft sine with subtle phase modulation
        phase_mod = np.sin(2 * np.pi * 0.5 * t) * 0.1
        return np.sin(2 * np.pi * freq * t + phase_mod)
    elif waveform_type == "ambient":
        # Multiple soft harmonics for depth
        return (np.sin(2 * np.pi * freq * t) + 
                np.sin(2 * np.pi * freq * 0.5 * t) * 0.3 +
                np.sin(2 * np.pi * freq * 1.5 * t) * 0.2)
    else:  # "gentle"
        # Gentle tremolo effect
        tremolo = 0.8 + 0.2 * np.sin(2 * np.pi * 3 * t)
        return np.sin(2 * np.pi * freq * t) * tremolo

def generate_audio():
    global last_update
    log("GENERATING 6-SECOND LOOP")
    recent = []
    if os.path.exists(SOUND_LOG):
        with open(SOUND_LOG) as f:
            # Use complexity parameter to limit voices
            max_voices = max(1, min(10, int(SOUND_PARAMS["complexity"])))
            recent = [json.loads(l) for l in f.readlines()[-max_voices:]]

    duration_seconds = 6
    t = np.linspace(0, duration_seconds, int(SAMPLE_RATE * duration_seconds), endpoint=False)
    mix = np.zeros(len(t))

    # Spread sounds across the full 6 seconds with overlap for continuous sound
    num_voices = len(recent)
    if num_voices > 0:
        # Ensure sounds always fill the full 6 seconds - adjust duration based on voice count
        if num_voices == 1:
            sound_duration = 6.0  # Single voice fills entire loop
            time_spacing = 0
        else:
            sound_duration = max(4.0, 6.0 / num_voices + 2.0)  # Overlap to ensure no gaps
            time_spacing = 6.0 / num_voices  # Evenly spread across 6 seconds
        
        # Soft, hypnotic waveform types
        waveforms = ["dreamy", "soft", "ambient", "gentle"]
        
        for idx, entry in enumerate(recent):
            agent = entry["agent"]
            phoneme = entry["phoneme"]
            
            # Lower frequencies for softer, deeper, more hypnotic sound
            base_freq = (INSTRUMENTS[agent]["freq"] * 0.5 + len(phoneme) * 3 + SOUND_PARAMS["pitch_shift"])
            base_freq = max(55, min(440, base_freq))  # Keep in comfortable range (55-440 Hz)
            
            # Softer volume for gentle ambient sound
            gain = INSTRUMENTS[agent]["gain"] * SOUND_PARAMS["volume_boost"] * 0.35
            
            # Start time spread across 6 seconds
            start_time = idx * time_spacing
            end_time = min(start_time + sound_duration, duration_seconds)
            mask = (t >= start_time) & (t < end_time)
            
            # Choose waveform based on phoneme for variety
            waveform_idx = hash(phoneme) % len(waveforms)
            waveform_type = waveforms[waveform_idx]
            
            # Generate soft, hypnotic base wave
            wave = generate_waveform(waveform_type, base_freq, t[mask] - start_time)
            
            # Add subtle lower octave for depth and warmth
            sub_harmonic = np.sin(2 * np.pi * base_freq * 0.5 * (t[mask] - start_time)) * 0.25
            # Add gentle higher harmonics for shimmer
            upper_harmonic = np.sin(2 * np.pi * base_freq * 2 * (t[mask] - start_time)) * 0.15
            wave = wave + sub_harmonic + upper_harmonic
            
            # Apply long, smooth fade in/out envelope for dreamy effect
            envelope = np.ones(len(t[mask]))
            fade_samples = int(SAMPLE_RATE * 0.5)  # 500ms fade for smoothness
            if len(envelope) > fade_samples * 2:
                envelope[:fade_samples] = np.linspace(0, 1, fade_samples) ** 2  # Gentle curve
                envelope[-fade_samples:] = (np.linspace(1, 0, fade_samples)) ** 2
            wave = wave * envelope
            
            # Apply reverb-like decay effect if enabled
            if SOUND_PARAMS["decay"] > 0:
                decay_envelope = np.linspace(1.0, 1.0 - SOUND_PARAMS["decay"], len(t[mask])) ** 1.5
                wave = wave * decay_envelope
            
            mix[mask] += gain * wave

    # Normalize to prevent clipping
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val * 0.8
    
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
        
        # VOTING: Each agent votes on how to modify sound parameters
        all_agents = list(INSTRUMENTS.keys())
        votes = {}
        option_names = list(VOTE_OPTIONS.keys())
        
        for voter in all_agents:
            choice = random.choice(option_names)
            votes[voter] = choice
            log(f"🗳️  {voter} votes to {VOTE_OPTIONS[choice]['desc']}")
        
        # Count votes
        vote_counts = {}
        for option in votes.values():
            vote_counts[option] = vote_counts.get(option, 0) + 1
        
        # Find winner (most votes, random if tie)
        if vote_counts:
            max_votes = max(vote_counts.values())
            winners = [opt for opt, count in vote_counts.items() if count == max_votes]
            winning_option = random.choice(winners)
            winner_votes = vote_counts[winning_option]
        else:
            # Fallback
            winning_option = random.choice(option_names)
            winner_votes = 0
        
        # Apply the winning sound parameter change with proper bounds
        param_info = VOTE_OPTIONS[winning_option]
        param_name = param_info["param"]
        change = param_info["change"]
        old_value = SOUND_PARAMS[param_name]
        new_value = SOUND_PARAMS[param_name] + change
        
        # Apply parameter-specific bounds
        if param_name == "volume_boost":
            new_value = max(0.1, min(2.0, new_value))  # 0.1 to 2.0
        elif param_name == "complexity":
            new_value = max(1, min(10, int(new_value)))  # 1 to 10 voices
        elif param_name == "pitch_shift":
            new_value = max(-200, min(200, new_value))  # -200 to +200 Hz
        elif param_name == "decay":
            new_value = max(0.0, min(1.0, new_value))  # 0 to 1 (no decay to full fade)
        
        SOUND_PARAMS[param_name] = new_value
        
        # Log voting result
        vote_entry = {
            "votes": votes,
            "winner": winning_option,
            "vote_count": winner_votes,
            "param": param_name,
            "old_value": old_value,
            "new_value": SOUND_PARAMS[param_name],
            "ts": time.time()
        }
        with open(VOTE_LOG, "a") as f:
            json.dump(vote_entry, f)
            f.write("\n")
        
        log(f"✨ DECISION: {param_info['desc'].upper()} ({winner_votes} votes)")
        log(f"   {param_name}: {old_value:.2f} → {SOUND_PARAMS[param_name]:.2f}")
        
        # Now pick a random agent to sing
        agent = random.choice(all_agents)
        phoneme = random.choice(PHONEMES)
        if random.random() > 0.7:  # 30% chance of repeating
            phoneme = phoneme * random.randint(2, 4)
        
        entry = {"agent": agent, "phoneme": phoneme, "ts": time.time()}
        with open(SOUND_LOG, "a") as f:
            json.dump(entry, f)
            f.write("\n")
        log(f"🎵 {agent} sings \"{phoneme}\"")
        generate_audio()

def initialize_app():
    """Initialize the app - runs both in development and production"""
    for f in [SOUND_LOG, VOTE_LOG, LOG_FILE]:
        if os.path.exists(f): os.remove(f)
        open(f, "a").close()
    log("AGENTIC NOISE ORCHESTRA — INITIALIZING")
    for _ in range(3):
        agent = random.choice(list(INSTRUMENTS.keys()))
        phoneme = random.choice(PHONEMES)
        if random.random() > 0.7:
            phoneme = phoneme * random.randint(2, 3)
        entry = {"agent": agent, "phoneme": phoneme, "ts": time.time()}
        with open(SOUND_LOG, "a") as f:
            json.dump(entry, f)
            f.write("\n")
        log(f"🎵 {agent} sings \"{phoneme}\"")
        time.sleep(0.5)
    generate_audio()
    threading.Thread(target=auto_cycle, daemon=True).start()

# Initialize app when module is loaded (works for both dev and production)
initialize_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
