# Text-to-Voice

Convert text files to speech audio using macOS built-in voices for dialogues between speakers.

## Features
- High-quality macOS voices for natural speech
- Speaker differentiation (physiotherapist vs. patient)
- Parallel processing for faster conversion
- Single MP3 file output

## Installation
Requires Python 3.9+ and Poetry.

```bash
git clone https://github.com/yourusername/text-to-voice-python.git
cd text-to-voice-python
poetry install
```

## Usage
Input requires lines with "Physiotherapist:" or "Patient:" prefixes.

```bash
poetry run text-to-voice input_file.txt
```

### Options
```
text-to-voice [-h] [--output OUTPUT] [--physio-voice VOICE]
              [--patient-voice VOICE] [--workers N] [--list-voices]
              input_file
```

List available voices:
```bash
poetry run text-to-voice --list-voices
```

## Example Input
```
Physiotherapist: Hello, how are you feeling today?
Patient: My shoulder has been bothering me lately.
```

## Requirements
- macOS (uses built-in `say` command)
- Python 3.9+
- Poetry
- ffmpeg (for audio processing)

## License
MIT 
