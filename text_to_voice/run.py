#!/usr/bin/env python3
"""
Main module for converting text to speech.
"""

import argparse
import logging
import multiprocessing
import os
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from pydub import AudioSegment
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Define voice options for macOS
DEFAULT_PHYSIO_VOICE = "Daniel"  # A deeper voice for physiotherapist
DEFAULT_PATIENT_VOICE = "Samantha"  # A different voice for patient


def process_line(line_data):
    """Process a single line of text to speech using macOS 'say' command"""
    i, line, physio_voice, patient_voice = line_data

    # Skip empty lines
    if not line.strip():
        logging.info(f"Skipping empty line {i}")
        return i, None

    try:
        # Create a temporary file for the audio output
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as temp_file:
            temp_filename = temp_file.name

        if line.startswith("Physiotherapist:"):
            text = line.replace("Physiotherapist:", "").strip()
            voice = physio_voice
        else:
            text = line.replace("Patient:", "").strip()
            voice = patient_voice

        # Use macOS 'say' command to generate speech to a file
        subprocess.run(["say", "-v", voice, "-o", temp_filename, text], check=True)

        # Convert the AIFF file to MP3 using pydub
        segment = AudioSegment.from_file(temp_filename)

        # Clean up
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        return i, segment

    except Exception as e:
        logging.error(f"Error processing line {i}: {str(e)}")
        # Create a silent segment instead
        segment = AudioSegment.silent(duration=500)  # 500ms of silence

        # Clean up if the file exists
        if "temp_filename" in locals() and os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except:
                pass

        return i, segment


def main():
    """Main function to process text-to-speech conversion."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Convert text to speech using macOS voices"
    )
    parser.add_argument("input_file", type=str, nargs="?", help="Input text file path")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output.mp3",
        help="Output audio file path (default: output.mp3)",
    )
    parser.add_argument(
        "--physio-voice",
        type=str,
        default=DEFAULT_PHYSIO_VOICE,
        help=f"Voice for physiotherapist (default: {DEFAULT_PHYSIO_VOICE})",
    )
    parser.add_argument(
        "--patient-voice",
        type=str,
        default=DEFAULT_PATIENT_VOICE,
        help=f"Voice for patient (default: {DEFAULT_PATIENT_VOICE})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=min(10, multiprocessing.cpu_count()),
        help="Number of parallel workers (default: min(10, CPU_COUNT))",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available macOS voices and exit",
    )
    args = parser.parse_args()

    # List available voices if requested
    if args.list_voices:
        print("Available macOS voices:")
        subprocess.run(["say", "-v", "?"], check=True)
        return

    # Check if input file is provided
    if not args.input_file:
        parser.error("input_file is required unless --list-voices is specified")

    # Check if input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        logging.error(f"Input file not found: {args.input_file}")
        return

    logging.info(
        f"Using '{args.physio_voice}' voice for physiotherapist and '{args.patient_voice}' voice for patient"
    )

    # Read the labeled transcript
    logging.info(f"Reading transcript file: {args.input_file}")
    with open(args.input_file) as f:
        lines = f.readlines()
    logging.info(f"Found {len(lines)} lines in transcript")

    # Determine the number of workers
    num_workers = args.workers
    logging.info(f"Using {num_workers} parallel workers")

    # Process lines in parallel
    results = {}
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(
                process_line, (i, line, args.physio_voice, args.patient_voice)
            ): i
            for i, line in enumerate(lines)
        }

        # Show progress bar
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing lines"
        ):
            index, segment = future.result()
            if segment is not None:
                results[index] = segment

    # Sort segments by original line index
    audio_segments = [results[i] for i in sorted(results.keys()) if i in results]

    # Combine all segments
    if audio_segments:
        logging.info(f"Combining {len(audio_segments)} audio segments")
        final_audio = sum(audio_segments)
        logging.info(f"Exporting final audio file to {args.output}")
        final_audio.export(args.output, format="mp3")
        logging.info(f"Processing complete! Final audio saved as {args.output}")
    else:
        logging.error("No audio segments were created. Cannot generate output file.")


if __name__ == "__main__":
    main()
