# Release Notes - v0.4.0

## What's New

### 🎬 YouTube Transcription Feature

The headline feature of this release! Transcribe YouTube videos to text using local Whisper AI for privacy-first video analysis.

#### New Commands

```bash
# Transcribe a YouTube video
nexus transcribe url "https://www.youtube.com/watch?v=VIDEO_ID"

# Use a specific Whisper model size
nexus transcribe url VIDEO_URL --model-size small

# Save to custom directory
nexus transcribe url VIDEO_URL --output-dir ~/my-transcriptions

# List all transcriptions
nexus transcribe list

# List with detailed information
nexus transcribe list --verbose
```

#### Features

- **🔒 Privacy-First**: All transcription happens locally using Whisper AI - no data sent to cloud services
- **📊 Progress Indicators**: Rich progress bars and status updates during transcription
- **🎯 Multiple Model Sizes**: Choose from 5 Whisper models (tiny/base/small/medium/large) to balance accuracy and speed
- **📝 Metadata Preservation**: Video title, uploader, duration, and upload date saved with transcript
- **📂 Organized Output**: Transcriptions saved with video ID and timestamp for easy reference
- **🔍 List History**: View all transcriptions with details
- **⚙️ Configurable**: Set default model size and output directory in config

#### Whisper Model Sizes

| Model  | RAM Required | Speed    | Accuracy | Use Case                    |
|--------|-------------|----------|----------|-----------------------------|
| tiny   | ~1 GB       | Fastest  | Basic    | Quick transcriptions, testing |
| base   | ~1 GB       | Fast     | Good     | **Default**, best balance   |
| small  | ~2 GB       | Medium   | Better   | Higher quality transcriptions |
| medium | ~5 GB       | Slower   | High     | Professional use            |
| large  | ~10 GB      | Slowest  | Best     | Maximum accuracy needed     |

#### Output Format

Transcriptions are saved as text files with comprehensive metadata headers:

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

[Full transcript text here...]
```

#### Configuration

Add to `~/.config/nexus/config.yaml`:

```yaml
transcription:
  output_dir: ./transcriptions  # Where to save transcriptions
  default_model_size: base      # Default Whisper model
```

#### Requirements

**New Dependencies:**
- `yt-dlp` - YouTube video downloading
- `openai-whisper` - Speech-to-text transcription
- `ffmpeg-python` - Audio processing
- `ffmpeg` system package (must be installed separately)

**Install ffmpeg:**
```bash
sudo apt update
sudo apt install -y ffmpeg
```

#### Use Cases

Perfect for:
- Creating searchable transcripts of technical videos
- Analyzing tutorial content with AI
- Extracting information from conference talks
- Documenting video content
- Processing educational materials
- Accessibility improvements

#### Technical Details

- **Automatic Cleanup**: Temporary audio files are automatically cleaned up after transcription
- **Error Handling**: Comprehensive error messages for common issues (missing dependencies, invalid URLs, etc.)
- **Consistent Formatting**: Uses existing Nexus formatter for beautiful, consistent output
- **Non-Invasive**: Completely separate module - doesn't affect existing commands

## Installation

### Update from v0.3.0

```bash
cd nexus-cli-assistant
git pull
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Reinstall package
pip install -e .

# Install ffmpeg (if not already installed)
sudo apt install -y ffmpeg
```

### Fresh Install

```bash
git clone https://github.com/nexus-mike/Nexus-CLI-Assistant.git
cd nexus-cli-assistant
./scripts/install.sh

# Install ffmpeg
sudo apt install -y ffmpeg
```

## Example Usage

```bash
# Transcribe a tutorial video
nexus transcribe url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Use higher quality model for important content
nexus transcribe url "https://youtube.com/watch?v=CONF_TALK" --model-size medium

# List all your transcriptions
nexus transcribe list --verbose
```

## Breaking Changes

None - this is a backward-compatible update. All existing commands (ask, workflow, script, etc.) continue to work as before.

## Performance Notes

- **First Run**: First transcription will download the selected Whisper model (~100MB - 3GB depending on size)
- **Subsequent Runs**: Model is cached locally for instant reuse
- **Processing Time**: Varies by model size and video length. Typical 1-minute video:
  - tiny/base: ~30-60 seconds
  - small: ~1-2 minutes
  - medium/large: ~3-5 minutes

## What's Next

Future enhancements being considered:
- Batch transcription of multiple videos
- Speaker diarization (identify different speakers)
- Timestamp markers in transcript
- Integration with `nexus ask` for querying transcript content
- Support for other video platforms
- Automatic summarization of transcripts

## Contributors

- Maikel van den Brink

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

---

**Note**: This release maintains all features from v0.3.0 (workflow automation) and v0.2.0 (multiple AI providers, caching, rate limiting, etc.).
