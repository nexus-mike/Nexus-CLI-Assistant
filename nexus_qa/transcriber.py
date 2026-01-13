"""YouTube video transcription using yt-dlp and Whisper."""

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.console import Console

console = Console()


class TranscriptionError(Exception):
    """Custom exception for transcription errors."""
    pass


class YouTubeTranscriber:
    """Transcribes YouTube videos to text using yt-dlp and Whisper."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize YouTubeTranscriber.
        
        Args:
            output_dir: Directory to save transcriptions. Defaults to ./transcriptions
        """
        if output_dir is None:
            # Default to transcriptions/ in current working directory
            output_dir = Path.cwd() / "transcriptions"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = self.output_dir / ".temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required dependencies are installed."""
        # Check yt-dlp
        try:
            import yt_dlp
        except ImportError:
            raise TranscriptionError(
                "yt-dlp is not installed. Install with: pip install yt-dlp"
            )
        
        # Check Whisper
        try:
            import whisper
        except ImportError:
            raise TranscriptionError(
                "openai-whisper is not installed. Install with: pip install openai-whisper"
            )
        
        # Check ffmpeg
        if not shutil.which("ffmpeg"):
            raise TranscriptionError(
                "ffmpeg is not installed. Install with: sudo apt install ffmpeg"
            )
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise TranscriptionError(f"Could not extract video ID from URL: {url}")
    
    def get_video_info(self, url: str) -> Dict:
        """Get video metadata using yt-dlp."""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                }
        except Exception as e:
            raise TranscriptionError(f"Failed to get video info: {e}")
    
    def download_audio(self, url: str, video_id: str) -> Path:
        """Download audio from YouTube video."""
        try:
            import yt_dlp
            
            audio_path = self.temp_dir / f"{video_id}.mp3"
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(self.temp_dir / f"{video_id}.%(ext)s"),
                'quiet': True,
                'no_warnings': True,
            }
            
            console.print("[cyan]📥 Downloading audio...[/cyan]")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if not audio_path.exists():
                raise TranscriptionError("Audio download failed")
            
            return audio_path
            
        except Exception as e:
            raise TranscriptionError(f"Failed to download audio: {e}")
    
    def transcribe_audio(self, audio_path: Path, model_size: str = "base") -> str:
        """Transcribe audio using Whisper."""
        try:
            import whisper
            
            console.print(f"[cyan]🎤 Loading Whisper model ({model_size})...[/cyan]")
            model = whisper.load_model(model_size)
            
            console.print("[cyan]✍️  Transcribing audio...[/cyan]")
            result = model.transcribe(str(audio_path), verbose=False)
            
            return result["text"].strip()
            
        except Exception as e:
            raise TranscriptionError(f"Failed to transcribe audio: {e}")
    
    def save_transcription(
        self, 
        text: str, 
        metadata: Dict, 
        video_id: str
    ) -> Path:
        """Save transcription to file with metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{video_id}_{timestamp}.txt"
        output_path = self.output_dir / filename
        
        # Format metadata header
        header = "=" * 80 + "\n"
        header += "YOUTUBE VIDEO TRANSCRIPTION\n"
        header += "=" * 80 + "\n"
        header += f"Video ID:     {metadata.get('id', 'N/A')}\n"
        header += f"Title:        {metadata.get('title', 'N/A')}\n"
        header += f"Uploader:     {metadata.get('uploader', 'N/A')}\n"
        header += f"Upload Date:  {metadata.get('upload_date', 'N/A')}\n"
        header += f"Duration:     {metadata.get('duration', 'N/A')} seconds\n"
        header += f"Transcribed:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += "=" * 80 + "\n\n"
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            f.write(text)
        
        return output_path
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(exist_ok=True)
    
    def transcribe(
        self, 
        url: str, 
        model_size: str = "base"
    ) -> Tuple[Path, Dict]:
        """Complete transcription workflow.
        
        Args:
            url: YouTube video URL
            model_size: Whisper model size (tiny, base, small, medium, large)
        
        Returns:
            Tuple of (transcription_file_path, metadata)
        """
        try:
            console.print(f"[bold cyan]🎬 Starting transcription for:[/bold cyan] {url}")
            
            # Get video info
            console.print("[cyan]📋 Fetching video info...[/cyan]")
            metadata = self.get_video_info(url)
            video_id = metadata['id']
            
            console.print(f"[green]✓[/green] Video: [bold]{metadata['title']}[/bold]")
            
            # Download audio
            audio_path = self.download_audio(url, video_id)
            console.print(f"[green]✓[/green] Audio downloaded")
            
            # Transcribe
            text = self.transcribe_audio(audio_path, model_size)
            console.print(f"[green]✓[/green] Transcription complete ({len(text)} chars)")
            
            # Save
            output_path = self.save_transcription(text, metadata, video_id)
            console.print(f"[green]✓[/green] Saved to: [bold]{output_path}[/bold]")
            
            # Cleanup
            self.cleanup()
            
            return output_path, metadata
            
        except TranscriptionError:
            self.cleanup()
            raise
        except Exception as e:
            self.cleanup()
            raise TranscriptionError(f"Transcription failed: {e}")
    
    def list_transcriptions(self) -> List[Dict]:
        """List all transcriptions with metadata."""
        transcriptions = []
        
        if not self.output_dir.exists():
            return transcriptions
        
        for file_path in sorted(self.output_dir.glob("*.txt"), reverse=True):
            try:
                # Read metadata from file header
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract metadata
                metadata = {
                    'file': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                }
                
                # Parse header for video info
                lines = content.split('\n')
                for line in lines[:10]:  # Check first 10 lines
                    if line.startswith('Video ID:'):
                        metadata['video_id'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Title:'):
                        metadata['title'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Duration:'):
                        metadata['duration'] = line.split(':', 1)[1].strip()
                
                transcriptions.append(metadata)
                
            except Exception:
                # Skip files that can't be read
                continue
        
        return transcriptions
