# Agentic Noise Orchestra

## Overview
An experimental generative audio web application that creates evolving 6-second audio loops. Six AI "agents" (Luna, Sol, Aurora, Nimbus, Echo, and Stella) randomly contribute vocal-like tones, creating an ever-changing soundscape.

**Current State**: Fully functional and running on Replit. The application generates real-time audio visualizations and logs agent activity.

**Last Updated**: October 21, 2025

## Recent Changes
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
1. **Initialization**: On startup, the app clears previous logs and generates initial sounds from 3 random agents
2. **Audio Generation**: Each agent has a unique base frequency. Phoneme length affects pitch variation
3. **Auto Cycle**: Every 6 seconds, a random agent "sings" a random phoneme (o, a, i, u, e), updating the audio loop
4. **Frontend**: Displays the audio player, real-time waveform visualization, and terminal logs of agent activity

### Agents & Instruments
- **Luna**: 220 Hz (gain 0.3)
- **Sol**: 110 Hz (gain 0.4)
- **Aurora**: 880 Hz (gain 0.3)
- **Nimbus**: 330 Hz (gain 0.4)
- **Echo**: 440 Hz (gain 0.3)
- **Stella**: 660 Hz (gain 0.3)

### Configuration
- **Port**: 5000 (Flask development server)
- **Max Tracks**: 6 concurrent sounds in the loop
- **Loop Duration**: 6 seconds
- **Sample Rate**: 44.1 kHz
- **Volume Boost**: 0.5

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
