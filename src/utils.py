"""
Shared utility functions for Voice AI Agent.
"""

import re
from typing import List


def normalize_text(text: str) -> str:
    """Clean and normalize text string for TTS or processing.

    Args:
        text: Input text string

    Returns:
        Normalized text string
    """
    if not text:
        return ""
    # Strip whitespace
    text = text.strip()
    # Replace multiple whitespace characters with a single space
    text = re.sub(r'\s+', ' ', text)
    return text


def chunk_text(text: str, max_chars: int = 300) -> List[str]:
    """Split text into smaller chunks for processing (e.g. TTS).

    Args:
        text: Input text to split
        max_chars: Maximum character length per chunk

    Returns:
        List of text chunks
    """
    normalized = normalize_text(text)
    if not normalized:
        return []
    if len(normalized) <= max_chars:
        return [normalized]

    chunks = []
    # Split by sentence delimiters first
    sentences = re.split(r'(?<=[.!?])\s+', normalized)

    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If a single sentence exceeds max_chars, split hard
            if len(sentence) > max_chars:
                for i in range(0, len(sentence), max_chars):
                    chunks.append(sentence[i:i + max_chars])
                current_chunk = ""
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def convert_pcm_format(audio_data: bytes, source_sample_rate: int, target_sample_rate: int) -> bytes:
    """Basic sample rate conversion helper for PCM audio data.

    Args:
        audio_data: Raw audio bytes (int16 PCM)
        source_sample_rate: Current sample rate in Hz
        target_sample_rate: Desired sample rate in Hz

    Returns:
        Resampled raw audio bytes
    """
    if source_sample_rate == target_sample_rate or not audio_data:
        return audio_data

    # Perform linear interpolation ratio resampling if needed
    ratio = target_sample_rate / source_sample_rate
    num_samples = len(audio_data) // 2
    if num_samples == 0:
        return audio_data

    import array
    samples = array.array('h', audio_data)
    new_num_samples = int(num_samples * ratio)
    new_samples = array.array('h')

    for i in range(new_num_samples):
        old_idx = min(int(i / ratio), num_samples - 1)
        new_samples.append(samples[old_idx])

    return new_samples.tobytes()
