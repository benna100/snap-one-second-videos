#!/usr/bin/env python3
"""
Video compilation script for Snapchat memories.
Takes 1.6 seconds from each video clip, one per day, in chronological order.
Uses ffmpeg for video processing.
"""

import os
import re
import random
import subprocess
import tempfile
from datetime import datetime
from collections import defaultdict
from pathlib import Path

def parse_date_from_filename(filename):
    """Extract date from filename format: YYYY-MM-DD_uuid-main.mp4"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})_.*\.mp4$', filename)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d')
    return None

def get_video_files(video_dir):
    """Get all video files from the directory"""
    video_dir = Path(video_dir)
    return [f for f in video_dir.iterdir() if f.suffix.lower() == '.mp4']

def group_by_date(video_files):
    """Group video files by date, return dict of date -> list of files"""
    grouped = defaultdict(list)
    
    for video_file in video_files:
        date = parse_date_from_filename(video_file.name)
        if date:
            grouped[date].append(video_file)
    
    return grouped

def select_one_per_day(grouped_videos):
    """Select one random video per day"""
    selected = {}
    
    for date, videos in grouped_videos.items():
        if videos:
            selected[date] = random.choice(videos)
    
    return selected

def get_video_duration(video_path):
    """Get video duration using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
    except (subprocess.CalledProcessError, KeyError, ValueError):
        print(f"Warning: Could not get duration for {video_path}")
        return 10.0  # Default fallback

def validate_clip(clip_path):
    """Validate that a clip is properly encoded and has both video and audio"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_streams', '-show_format', str(clip_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        
        # Check if we have both video and audio streams
        has_video = False
        has_audio = False
        duration = None
        
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                has_video = True
            elif stream.get('codec_type') == 'audio':
                has_audio = True
        
        # Get duration
        if 'format' in data and 'duration' in data['format']:
            duration = float(data['format']['duration'])
        
        # Validate clip
        if not has_video:
            print(f"Warning: {clip_path} has no video stream")
            return False
        if not has_audio:
            print(f"Warning: {clip_path} has no audio stream")
            return False
        if duration is None or duration < 0.5:  # Should be ~1.6 seconds
            print(f"Warning: {clip_path} has invalid duration: {duration}")
            return False
            
        return True
        
    except (subprocess.CalledProcessError, KeyError, ValueError, json.JSONDecodeError):
        print(f"Warning: Could not validate {clip_path}")
        return False

def extract_clip(input_path, output_path, duration=1.6, start_time=0):
    """Extract a clip from video using ffmpeg with consistent encoding parameters"""
    cmd = [
        'ffmpeg', 
        '-i', str(input_path),
        '-ss', str(start_time),
        '-t', str(duration),
        # Video encoding with consistent parameters for smooth playback
        '-c:v', 'libx264',
        '-preset', 'slow',      # Better quality encoding
        '-crf', '20',           # Higher quality (lower CRF)
        '-pix_fmt', 'yuv420p',  # Consistent pixel format
        '-r', '30',             # Force consistent 30 fps
        '-g', '30',             # GOP size = frame rate (keyframe every second)
        '-keyint_min', '30',    # Minimum keyframe interval
        '-sc_threshold', '0',   # Disable scene change detection
        '-vf', 'scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2:black,fps=30',
        # Audio encoding with strict consistency
        '-c:a', 'aac',
        '-ar', '44100',         # Consistent sample rate
        '-ac', '2',             # Force stereo
        '-b:a', '192k',         # Higher audio quality
        '-profile:a', 'aac_low', # AAC-LC profile for compatibility
        # Timing and sync fixes
        '-avoid_negative_ts', 'make_zero',
        '-fflags', '+genpts',   # Generate presentation timestamps
        '-vsync', 'cfr',        # Constant frame rate
        '-async', '1',          # Audio sync method
        '-shortest',            # End when shortest stream ends
        '-y',
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting clip from {input_path}: {e}")
        print(f"STDERR: {e.stderr}")
        return False

def create_concat_file(clip_paths, concat_file_path):
    """Create a text file for ffmpeg concat demuxer"""
    with open(concat_file_path, 'w') as f:
        for clip_path in clip_paths:
            f.write(f"file '{clip_path}'\n")

def concatenate_videos(clip_paths, output_path):
    """Concatenate video clips using ffmpeg with proper sync"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as concat_file:
        create_concat_file(clip_paths, concat_file.name)
        concat_file_path = concat_file.name
    
    try:
        # Use filter_complex for better control over concatenation
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_file_path,
            # Video settings for smooth playback
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',           # Very high quality
            '-pix_fmt', 'yuv420p',
            '-r', '30',
            '-g', '30',             # GOP size
            '-keyint_min', '30',
            '-x264-params', 'keyint=30:min-keyint=30:scenecut=0',
            # Audio settings
            '-c:a', 'aac',
            '-ar', '44100',
            '-ac', '2',
            '-b:a', '192k',
            '-profile:a', 'aac_low',
            # Sync and timing
            '-avoid_negative_ts', 'make_zero',
            '-fflags', '+genpts',
            '-vsync', 'cfr',
            '-async', '1',
            '-max_muxing_queue_size', '1024',  # Prevent buffer issues
            '-y',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error concatenating videos: {e}")
        print(f"STDERR: {e.stderr}")
        return False
    
    finally:
        # Clean up concat file
        os.unlink(concat_file_path)

def main():
    """Main function to process videos"""
    video_dir = 'videos'
    output_file = 'snap-one-second-videos.mp4'
    clip_duration = 1.4
    
    print("Starting Snapchat video compilation...")
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg and ffprobe are required but not found in PATH")
        print("Please install ffmpeg: https://ffmpeg.org/download.html")
        return
    
    # Get all video files
    print(f"Scanning {video_dir} for video files...")
    video_files = get_video_files(video_dir)
    print(f"Found {len(video_files)} video files")
    
    if not video_files:
        print("No video files found!")
        return
    
    # Group by date
    print("Grouping videos by date...")
    grouped_videos = group_by_date(video_files)
    print(f"Found videos spanning {len(grouped_videos)} different dates")
    
    # Select one video per day
    print("Selecting one video per day...")
    selected_videos = select_one_per_day(grouped_videos)
    
    # Sort by date
    sorted_dates = sorted(selected_videos.keys())
    print(f"Processing {len(sorted_dates)} videos in chronological order")
    
    # Create temporary directory for clips
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        clip_paths = []
        
        print("Extracting clips...")
        for i, date in enumerate(sorted_dates):
            video_path = selected_videos[date]
            clip_filename = f"clip_{i:04d}_{date.strftime('%Y%m%d')}.mp4"
            clip_path = temp_dir_path / clip_filename
            
            print(f"Processing {date.strftime('%Y-%m-%d')}: {video_path.name}")
            
            # Get video duration to avoid extracting beyond the end
            duration = get_video_duration(video_path)
            actual_clip_duration = min(clip_duration, duration)
            
            # Extract clip from the beginning of the video
            if extract_clip(video_path, clip_path, actual_clip_duration, 0):
                # Validate the extracted clip
                if validate_clip(clip_path):
                    clip_paths.append(str(clip_path))
                    print(f"✓ Successfully processed {video_path.name}")
                else:
                    print(f"✗ Validation failed for {video_path.name}, skipping")
            else:
                print(f"✗ Extraction failed for {video_path.name}, skipping")
        
        if not clip_paths:
            print("No clips were successfully extracted!")
            return
        
        print(f"Successfully extracted {len(clip_paths)} clips")
        print("Concatenating videos...")
        
        # Concatenate all clips
        if concatenate_videos(clip_paths, output_file):
            print(f"✅ Video compilation completed successfully!")
            print(f"📹 Output file: {output_file}")
            print(f"📊 Total clips: {len(clip_paths)}")
            print(f"⏱️  Estimated duration: {len(clip_paths) * clip_duration:.1f} seconds")
        else:
            print("❌ Failed to concatenate videos")

if __name__ == "__main__":
    main()
