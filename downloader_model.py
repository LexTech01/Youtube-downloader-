import os
import yt_dlp


class VideoModel:
    """Model: Handles data and business logic"""
    
    def __init__(self):
        self.video_info = None
        self.formats = []
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.is_downloading = False
        
    def sanitize_url(self, url):
        """Clean and format YouTube URL."""
        url = url.strip()
        if "youtu.be/" in url:
            vid_id = url.split("youtu.be/")[-1].split("?")[0]
            url = f"https://www.youtube.com/watch?v={vid_id}"
        if not url.startswith("http"):
            url = "https://" + url
        return url
    
    def fetch_video_info(self, url):
        """Fetch video information using yt-dlp."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self.video_info = ydl.extract_info(url, download=False)
        
        return self.video_info
    
    def process_formats(self):
        """Process and filter available formats."""
        self.formats = []
        seen_resolutions = set()
        
        for f in self.video_info.get('formats', []):
            # Get formats with both video and audio
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                height = f.get('height', 0)
                if height and height not in seen_resolutions:
                    seen_resolutions.add(height)
                    
                    # Get file size
                    filesize = f.get('filesize', 0) or f.get('filesize_approx', 0)
                    filesize_mb = filesize / (1024 * 1024) if filesize else 0
                    
                    format_info = {
                        'format_id': f.get('format_id'),
                        'height': height,
                        'ext': f.get('ext', 'mp4'),
                        'vcodec': f.get('vcodec', 'unknown'),
                        'acodec': f.get('acodec', 'unknown'),
                        'filesize_mb': filesize_mb,
                        'fps': f.get('fps', 0),
                        'tbr': f.get('tbr', 0)
                    }
                    self.formats.append(format_info)
        
        # Sort by height (resolution)
        self.formats.sort(key=lambda x: x['height'], reverse=True)
        
        # If no combined formats, get best video
        if not self.formats:
            best_video = max(
                [f for f in self.video_info.get('formats', []) if f.get('vcodec') != 'none'],
                key=lambda x: x.get('height', 0),
                default=None
            )
            if best_video:
                height = best_video.get('height', 0)
                filesize = best_video.get('filesize', 0) or best_video.get('filesize_approx', 0)
                filesize_mb = filesize / (1024 * 1024) if filesize else 0
                
                self.formats.append({
                    'format_id': 'best',
                    'height': height,
                    'ext': best_video.get('ext', 'mp4'),
                    'vcodec': best_video.get('vcodec', 'unknown'),
                    'acodec': 'separate audio',
                    'filesize_mb': filesize_mb,
                    'fps': best_video.get('fps', 0),
                    'tbr': best_video.get('tbr', 0)
                })
        
        return self.formats
    
    def get_format_by_resolution(self, resolution):
        """Get format info by resolution height."""
        return next((f for f in self.formats if f['height'] == resolution), None)
    
    def get_thumbnail_url(self):
        """Get video thumbnail URL."""
        return self.video_info.get('thumbnail') if self.video_info else None
    
    def get_video_metadata(self):
        """Get video metadata (title, author, duration)."""
        if not self.video_info:
            return None
        
        duration = self.video_info.get('duration', 0)
        duration_min = duration // 60
        duration_sec = duration % 60
        
        return {
            'title': self.video_info.get('title', 'Unknown'),
            'uploader': self.video_info.get('uploader', 'Unknown'),
            'duration': f"{duration_min}:{duration_sec:02d}",
            'url': self.video_info.get('webpage_url', '')
        }
    
    def download_video(self, resolution, progress_callback):
        """Download video with specified resolution."""
        fmt = self.get_format_by_resolution(resolution)
        if not fmt:
            raise ValueError("Format not found")
        
        ydl_opts = {
            'format': f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]",
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_callback],
            'merge_output_format': fmt['ext'],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.video_info['webpage_url']])
