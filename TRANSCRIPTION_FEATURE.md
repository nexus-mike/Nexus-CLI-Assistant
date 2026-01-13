# YouTube Transcription Feature

## Overview
Added YouTube video transcription capability to Nexus CLI Assistant using local Whisper AI for privacy-first video analysis.

## Implementation Summary

### Files Created/Modified

1. **nexus_qa/transcriber.py** (NEW)
   - `YouTubeTranscriber` class for handling video transcription
   - Uses yt-dlp for video download
   - Uses OpenAI Whisper for transcription
   - Includes progress indicators with Rich library
   - Automatic cleanup of temporary files

2. **nexus_qa/main.py** (MODIFIED)
   - Added `transcribe` command group
   - Added `transcribe url` subcommand for transcribing videos
   - Added `transcribe list` subcommand for listing transcriptions
   - Full integration with existing formatter and error handling

3. **requirements.txt** (MODIFIED)
   - Added yt-dlp>=2024.0.0
   - Added openai-whisper>=20231117
   - Added ffmpeg-python>=0.2.0

4. **config/config.yaml.example** (MODIFIED)
   - Added transcription configuration section
   - Options for output directory and default model size

5. **README.md** (MODIFIED)
   - Added feature to features list
   - Added complete usage documentation
   - Added model size comparison table
   - Added ffmpeg installation instructions

6. **.gitignore** (ALREADY PRESENT)
   - Already includes transcriptions/ directory

## Usage

### Basic Transcription
```bash
nexus transcribe url "https://www.youtube.com/watch?v=VIDEO_ID"
```

### With Custom Model
```bash
nexus transcribe url VIDEO_URL --model-size small
```

### Custom Output Directory
```bash
nexus transcribe url VIDEO_URL -o ~/my-transcriptions
```

### List Transcriptions
```bash
nexus transcribe list
nexus transcribe list --verbose
```

## Model Sizes

| Model  | RAM Required | Speed    | Accuracy | Use Case                    |
|--------|-------------|----------|----------|-----------------------------|
| tiny   | ~1 GB       | Fastest  | Basic    | Quick transcriptions        |
| base   | ~1 GB       | Fast     | Good     | Default, best balance       |
| small  | ~2 GB       | Medium   | Better   | Higher quality              |
| medium | ~5 GB       | Slower   | High     | Professional use            |
| large  | ~10 GB      | Slowest  | Best     | Maximum accuracy            |

## Requirements

- Python dependencies: Installed via pip
- System dependency: ffmpeg (must be installed separately)
  ```bash
  sudo apt install -y ffmpeg
  ```

## Output Format

Transcriptions are saved as text files with metadata:
- **Location**: `./transcriptions/` (configurable)
- **Filename**: `{video_id}_{timestamp}.txt`
- **Content**: Metadata header + full transcript

Example header:
```
================================================================================
YOUTUBE VIDEO TRANSCRIPTION
================================================================================
Video ID:     ABC123XYZ
Title:        Example Video Title
Uploader:     Channel Name
Upload Date:  20240113
Duration:     1234 seconds
Transcribed:  2026-01-13 15:45:30
================================================================================

[transcript text here]
```

## Configuration

Add to `~/.config/nexus/config.yaml`:

```yaml
transcription:
  output_dir: ./transcriptions
  default_model_size: base
```

## Features

✅ Local AI processing (privacy-first)
✅ Progress indicators during transcription
✅ Metadata preservation (title, uploader, duration)
✅ Multiple model sizes for accuracy/performance trade-off
✅ Automatic temp file cleanup
✅ List all transcriptions with details
✅ Configurable output directory
✅ Integration with existing Nexus formatter

## Testing Status

- ✅ Dependencies installed successfully
- ✅ Commands registered in CLI
- ✅ Help text displays correctly
- ✅ List command works (shows empty state)
- ✅ No linter errors
- ⏳ Ready for real YouTube video testing

## Next Steps

To test with a real video:
```bash
nexus transcribe url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---
**Date**: 2026-01-13
**Version**: Added to Nexus CLI Assistant v0.3.0
