import os
import subprocess
from pathlib import Path
from typing import Optional
from loguru import logger
from labelu.internal.common.config import settings


class VideoStreamer:
    """Utility class for converting videos to HLS streaming format"""

    @staticmethod
    def is_video_file(filename: str) -> bool:
        """Check if file is a video file"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v']
        return any(filename.lower().endswith(ext) for ext in video_extensions)

    @staticmethod
    def get_hls_path(original_path: str) -> str:
        """Get HLS playlist path for original video path"""
        path = Path(original_path)
        hls_dir = path.parent / f"{path.stem}_hls"
        return str(hls_dir / "playlist.m3u8")

    @staticmethod
    def get_hls_dir(original_path: str) -> Path:
        """Get HLS directory path for original video"""
        path = Path(original_path)
        return path.parent / f"{path.stem}_hls"

    @staticmethod
    async def convert_to_hls(input_path: str, force_reconvert: bool = False) -> Optional[str]:
        """
        Convert video to HLS format
        Returns the playlist path if successful, None if failed
        """
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                logger.error(f"Input video file not found: {input_path}")
                return None

            hls_dir = VideoStreamer.get_hls_dir(input_path)
            playlist_path = hls_dir / "playlist.m3u8"

            # Check if already converted and not forcing reconversion
            if not force_reconvert and playlist_path.exists():
                logger.info(f"HLS already exists for {input_path}")
                return str(playlist_path)

            # Create HLS directory
            hls_dir.mkdir(parents=True, exist_ok=True)

            # FFmpeg command for HLS conversion
            cmd = [
                "ffmpeg",
                "-i", str(input_file),
                "-codec:v", "libx264",
                "-codec:a", "aac",
                "-hls_time", "10",  # 10 second segments
                "-hls_playlist_type", "vod",
                "-hls_segment_filename", str(hls_dir / "segment%03d.ts"),
                "-start_number", "0",
                "-y",  # Overwrite output files
                str(playlist_path)
            ]

            logger.info(f"Converting video to HLS: {input_path}")

            # Run FFmpeg conversion
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if process.returncode == 0:
                logger.info(f"Successfully converted video to HLS: {playlist_path}")
                return str(playlist_path)
            else:
                logger.error(f"FFmpeg conversion failed: {process.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"Video conversion timeout for {input_path}")
            return None
        except Exception as e:
            logger.error(f"Error converting video to HLS: {str(e)}")
            return None

    @staticmethod
    def get_streaming_url(original_path: str, base_url: str) -> str:
        """Get streaming URL for video"""
        if VideoStreamer.is_video_file(original_path):
            hls_path = VideoStreamer.get_hls_path(original_path)
            # Convert absolute path to relative URL path
            relative_path = os.path.relpath(hls_path, settings.MEDIA_ROOT)
            return f"{base_url}/{relative_path.replace(os.sep, '/')}"
        return f"{base_url}/{original_path.replace(os.sep, '/')}"
