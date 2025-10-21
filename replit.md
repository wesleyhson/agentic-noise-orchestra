# Agentic Noise Orchestra

## Overview
An experimental generative audio web application that creates evolving 6-second audio loops. Six AI "agents" (Luna, Sol, Aurora, Nimbus, Echo, and Stella) randomly contribute vocal-like tones, creating an ever-changing soundscape.

**Current State**: Fully functional and running on Replit. The application generates real-time audio visualizations and logs agent activity.

**Last Updated**: October 21, 2025

## Recent Changes
- **October 21, 2025**: Redesigned voting to control sound parameters
  - Agents now vote on sound parameter changes (volume, complexity, pitch, decay) instead of who sings
  - Winning parameter changes affect the entire soundscape (e.g., louder, more complex, pitch up/down)
  - Terminal displays voting decisions and shows parameter value changes in real-time
  - Sound evolves organically based on collective agent decisions
- **October 21, 2025**: Enhanced with voting and expanded vocalizations
  - Expanded phoneme library from 5 to 30+ vocalizations including syllables like "la", "hmm", "wow", etc.
  - Terminal now displays complete voting process with emoji indicators
  - Voting results stored in votes.jsonl for tracking
- **October 21, 2025**: Initial Replit setup
  - Installed Python 3.11 with Flask, gunicorn, numpy, and scipy
  - Fixed template folder path to use standard Flask structure
  - Configured Flask development workflow on port 5000
  - Set up deployment with gunicorn for autoscale
  - Created .gitignore for Python project

## Project Architecture

### Technology Stack
- **Backend**: Flask (Python 3.11)
- **Audio Processing**: NumPy and SciPy for waveform generation
- **Frontend**: Vanilla HTML/CSS/JavaScript with Canvas API for visualization
- **Deployment**: Gunicorn WSGI server

### File Structure
```
.
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend UI with audio player and visualizer
├── requirements.txt      # Python dependencies
├── sounds.jsonl          # Log of agent sounds (regenerated on start)
├── votes.jsonl           # Voting log (currently unused)
├── terminal_log.txt      # Application activity log
├── output.wav            # Generated audio file
└── replit.md            # This documentation file
```

### How It Works
1. **Initialization**: On startup, the app clears previous logs and generates initial sounds from 3 random agents using varied vocalizations
2. **Agentic Voting on Sound Parameters**: Every 6 seconds, all 6 agents vote on how to modify the soundscape:
   - **Volume Control**: LOUDER/QUIETER (adjusts overall mix volume 0.1-2.0)
   - **Complexity**: MORE_COMPLEX/SIMPLER (changes number of simultaneous voices 1-10)
   - **Pitch Shift**: PITCH_UP/PITCH_DOWN (global frequency adjustment -200 to +200 Hz)
   - **Decay Effect**: ADD_DECAY/LESS_DECAY (fade-out intensity 0.0-1.0)
3. **Parameter Application**: The winning parameter change is applied to the entire soundscape, affecting all agents
4. **Agent Performance**: After voting, a random agent is selected to add their voice to the mix
5. **Vocalization Selection**: The agent randomly chooses from 30+ phonemes and vocalizations, with 30% chance of repetition
6. **Audio Generation**: Sound is generated using current parameters (volume, complexity, pitch shift, decay) applied to all voices
7. **Frontend**: Displays audio player, real-time waveform visualization, and terminal logs showing voting decisions and parameter changes

### Agents & Instruments
- **Luna**: 220 Hz (gain 0.3)
- **Sol**: 110 Hz (gain 0.4)
- **Aurora**: 880 Hz (gain 0.3)
- **Nimbus**: 330 Hz (gain 0.4)
- **Echo**: 440 Hz (gain 0.3)
- **Stella**: 660 Hz (gain 0.3)

### Vocalizations
The agents can choose from 30+ phonemes and vocalizations:
- **Basic vowels**: o, a, i, u, e
- **Extended vowels**: ah, oh, ee, oo, eh
- **Syllables with 'a'**: la, na, ma, ra, da
- **Syllables with 'o'**: lo, no, mo, ro, do
- **Syllables with 'i'**: li, ni, mi, ri, di
- **Sustained sounds**: hum, hmm, ahh, ooo, eee
- **Expressive sounds**: wow, yay, oof, bah, doh

### Configuration
- **Port**: 5000 (Flask development server)
- **Max Tracks**: 6 concurrent sounds in the loop
- **Loop Duration**: 6 seconds
- **Sample Rate**: 44.1 kHz
- **Volume Boost**: 0.5
- **Voting Frequency**: Every 6 seconds (synchronized with loop duration)

## Development
- Run locally: The Flask App workflow is configured to run automatically
- Development server binds to 0.0.0.0:5000
- Logs are visible in the terminal and in the web UI

## Deployment
- Configured for Replit's autoscale deployment
- Uses gunicorn WSGI server for production
- Command: `gunicorn --bind=0.0.0.0:5000 --reuse-port app:app`

## Notes
- Audio files and logs are regenerated on each application restart
- The application uses a background thread for continuous audio generation
- No external APIs or database required - fully self-contained
