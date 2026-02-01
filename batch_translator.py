#!/usr/bin/env python3
"""
Batch Video Translator
Process multiple videos automatically
"""

import os
import sys
from pathlib import Path
import argparse
import time
from typing import List
import json

# Import the main translator
sys.path.insert(0, os.path.dirname(__file__))
from video_translator import VideoTranslator


class BatchProcessor:
    """Process multiple videos in batch"""
    
    def __init__(self, translator: VideoTranslator, config: dict):
        self.translator = translator
        self.config = config
        self.stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }
    
    def find_videos(self, directory: str, extensions: List[str] = None) -> List[Path]:
        """Find all video files in directory"""
        if extensions is None:
            extensions = ['.mp4', '.mkv', '.avi', '.mov', '.m4v', '.webm']
        
        directory = Path(directory)
        videos = []
        
        for ext in extensions:
            videos.extend(directory.glob(f'**/*{ext}'))
        
        return sorted(videos)
    
    def should_process(self, video_path: Path, output_dir: Path, target_langs: List[str]) -> bool:
        """Check if video needs processing"""
        # Check if output files already exist
        for lang in target_langs:
            output_video = output_dir / f"{video_path.stem}_{lang}.mp4"
            if output_video.exists() and self.config.get('skip_existing', True):
                return False
        return True
    
    def process_directory(self, input_dir: str, output_dir: str = None,
                         source_lang: str = 'en', target_langs: List[str] = None,
                         recursive: bool = False):
        """Process all videos in a directory"""
        
        print("="*70)
        print("BATCH VIDEO TRANSLATION")
        print("="*70)
        print(f"Input directory: {input_dir}")
        print(f"Output directory: {output_dir or 'Same as input'}")
        print(f"Source language: {source_lang}")
        print(f"Target languages: {', '.join(target_langs or ['None (transcribe only)'])}")
        print(f"Recursive: {recursive}")
        print("="*70 + "\n")
        
        # Find videos
        input_path = Path(input_dir)
        videos = self.find_videos(input_path)
        
        if not videos:
            print(f"No videos found in {input_dir}")
            return
        
        print(f"Found {len(videos)} video(s)\n")
        
        # Setup output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path
        
        # Process each video
        self.stats['total'] = len(videos)
        self.stats['start_time'] = time.time()
        
        for i, video in enumerate(videos, 1):
            print(f"\n{'='*70}")
            print(f"Processing {i}/{len(videos)}: {video.name}")
            print(f"{'='*70}\n")
            
            # Check if should process
            if not self.should_process(video, output_path, target_langs or []):
                print(f"⏭️  Skipping (output already exists)")
                self.stats['skipped'] += 1
                continue
            
            try:
                # Process video
                self.translator.process_video(
                    video_path=str(video),
                    source_lang=source_lang,
                    target_langs=target_langs,
                    output_dir=str(output_path),
                    whisper_model=self.config.get('whisper_model', 'base')
                )
                self.stats['completed'] += 1
                
            except Exception as e:
                print(f"\n❌ ERROR processing {video.name}: {str(e)}\n")
                self.stats['failed'] += 1
                
                # Continue or stop on error?
                if not self.config.get('continue_on_error', True):
                    raise
        
        self.stats['end_time'] = time.time()
        self.print_summary()
    
    def print_summary(self):
        """Print batch processing summary"""
        duration = self.stats['end_time'] - self.stats['start_time']
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        print("\n" + "="*70)
        print("BATCH PROCESSING SUMMARY")
        print("="*70)
        print(f"Total videos:     {self.stats['total']}")
        print(f"✅ Completed:     {self.stats['completed']}")
        print(f"⏭️  Skipped:       {self.stats['skipped']}")
        print(f"❌ Failed:        {self.stats['failed']}")
        print(f"⏱️  Total time:    {hours}h {minutes}m {seconds}s")
        
        if self.stats['completed'] > 0:
            avg_time = duration / self.stats['completed']
            print(f"📊 Avg per video: {int(avg_time // 60)}m {int(avg_time % 60)}s")
        
        print("="*70 + "\n")


def main():
    """Command-line interface for batch processing"""
    parser = argparse.ArgumentParser(
        description='Batch translate multiple videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all videos in a directory
  python batch_translator.py ./movies --source en --targets my th
  
  # Process recursively with output directory
  python batch_translator.py ./movies --output ./translated --recursive
  
  # Use specific Whisper model for all videos
  python batch_translator.py ./movies --source en --targets my --model medium
  
  # Process but skip existing outputs
  python batch_translator.py ./movies --source en --targets my --skip-existing
  
  # Continue even if some videos fail
  python batch_translator.py ./movies --source en --targets my --continue-on-error
        """
    )
    
    parser.add_argument('directory', help='Directory containing videos')
    parser.add_argument('--source', default='en', choices=['en', 'my', 'th'],
                       help='Source language (default: en)')
    parser.add_argument('--targets', nargs='+', choices=['en', 'my', 'th'],
                       help='Target languages for translation')
    parser.add_argument('--output', help='Output directory (default: same as input)')
    parser.add_argument('--model', default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper model size (default: base)')
    parser.add_argument('--recursive', action='store_true',
                       help='Process subdirectories recursively')
    parser.add_argument('--api-key', help='Anthropic API key')
    parser.add_argument('--local', action='store_true',
                       help='Use local translation (lower quality)')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                       help='Skip videos that already have output files (default)')
    parser.add_argument('--no-skip-existing', action='store_false', dest='skip_existing',
                       help='Process all videos, overwrite existing')
    parser.add_argument('--continue-on-error', action='store_true', default=True,
                       help='Continue processing if a video fails (default)')
    parser.add_argument('--stop-on-error', action='store_false', dest='continue_on_error',
                       help='Stop batch if any video fails')
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        'whisper_model': args.model,
        'skip_existing': args.skip_existing,
        'continue_on_error': args.continue_on_error
    }
    
    # Create translator
    translator = VideoTranslator(
        api_key=args.api_key,
        use_local_translation=args.local
    )
    
    # Create batch processor
    processor = BatchProcessor(translator, config)
    
    # Process directory
    processor.process_directory(
        input_dir=args.directory,
        output_dir=args.output,
        source_lang=args.source,
        target_langs=args.targets,
        recursive=args.recursive
    )


if __name__ == '__main__':
    main()
