#!/usr/bin/env python3
"""
Video Translation Tool
Supports: Transcription, Translation, Subtitle Generation, Video Encoding
Languages: English, Burmese/Myanmar, Thai
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict
import argparse

# Check and install required packages
def check_dependencies():
    """Check if required packages are installed"""
    required = {
        'whisper': 'openai-whisper',
        'anthropic': 'anthropic',
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    return True


class VideoTranslator:
    """Main video translation orchestrator"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'my': 'Burmese/Myanmar',
        'th': 'Thai'
    }

    NLLB_LANG_CODES = {
        'en': 'eng_Latn',
        'my': 'mya_Mymr',
        'th': 'tha_Thai',
    }
    
    def __init__(self, api_key: Optional[str] = None, use_local_translation: bool = False):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.use_local = use_local_translation
        
        if not use_local_translation and not self.api_key:
            print("WARNING: No API key provided. Will use local translation (lower quality)")
            self.use_local = True
    
    def transcribe_video(self, video_path: str, language: str = 'en', model: str = 'base') -> Dict:
        """
        Transcribe video audio using Whisper
        
        Args:
            video_path: Path to video file
            language: Source language code
            model: Whisper model size (tiny, base, small, medium, large)
        
        Returns:
            Dictionary with transcription and segments
        """
        print(f"🎤 Transcribing video with Whisper ({model} model)...")
        
        try:
            import whisper
        except ImportError:
            print("ERROR: Whisper not installed. Run: pip install openai-whisper")
            sys.exit(1)
        
        # Load model
        model_obj = whisper.load_model(model)
        
        # Transcribe
        result = model_obj.transcribe(
            video_path,
            language=language,
            verbose=False
        )
        
        print(f"✅ Transcription complete: {len(result['segments'])} segments")
        return result
    
    def _init_nllb_model(self):
        """Load NLLB-200 model and tokenizer (lazy-loaded, cached in memory)"""
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        model_name = "facebook/nllb-200-distilled-600M"
        print("Loading NLLB-200 translation model (first run downloads ~2.5GB)...")
        self.nllb_tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.nllb_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print("NLLB-200 model loaded.")

    def translate_with_nllb(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using NLLB-200 model locally

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Translated text
        """
        if not hasattr(self, 'nllb_model'):
            self._init_nllb_model()

        src_code = self.NLLB_LANG_CODES[source_lang]
        tgt_code = self.NLLB_LANG_CODES[target_lang]

        self.nllb_tokenizer.src_lang = src_code
        inputs = self.nllb_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        forced_bos_token_id = self.nllb_tokenizer.convert_tokens_to_ids(tgt_code)
        translated = self.nllb_model.generate(**inputs, forced_bos_token_id=forced_bos_token_id, max_length=512)
        return self.nllb_tokenizer.decode(translated[0], skip_special_tokens=True)

    def translate_with_claude(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using Claude API
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        if not self.api_key:
            raise ValueError("API key required for Claude translation")
        
        try:
            from anthropic import Anthropic
        except ImportError:
            print("ERROR: Anthropic package not installed. Run: pip install anthropic")
            sys.exit(1)
        
        client = Anthropic(api_key=self.api_key)
        
        source = self.SUPPORTED_LANGUAGES.get(source_lang, source_lang)
        target = self.SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        
        prompt = f"""Translate the following {source} text to {target}. 
Preserve the meaning, tone, and natural flow. For movie subtitles, keep translations concise and natural.

Text to translate:
{text}

Provide ONLY the translation, no explanations."""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
    
    def translate_segments(self, segments: List[Dict], source_lang: str, target_lang: str, 
                          batch_size: int = 10) -> List[Dict]:
        """
        Translate all segments with batching for efficiency
        
        Args:
            segments: List of segment dictionaries with 'text' key
            source_lang: Source language code
            target_lang: Target language code
            batch_size: Number of segments to translate together
        
        Returns:
            List of translated segments
        """
        print(f"🌐 Translating {len(segments)} segments ({source_lang} → {target_lang})...")
        
        translated_segments = []
        
        if self.use_local:
            print("Using NLLB-200 local translation...")
            for i, seg in enumerate(segments):
                translated_segments.append({
                    **seg,
                    'text': self.translate_with_nllb(seg['text'], source_lang, target_lang)
                })
                if (i + 1) % 10 == 0 or (i + 1) == len(segments):
                    print(f"  Translated {i + 1}/{len(segments)} segments")
            print("Translation complete")
            return translated_segments
        
        # Batch translation for efficiency
        for i in range(0, len(segments), batch_size):
            batch = segments[i:i+batch_size]
            
            # Combine batch texts
            combined = "\n".join([f"[{j}] {seg['text']}" for j, seg in enumerate(batch)])
            
            # Translate batch
            translated = self.translate_with_claude(combined, source_lang, target_lang)
            
            # Split back into segments
            translated_lines = translated.strip().split('\n')
            
            for j, seg in enumerate(batch):
                # Extract translation (handle different formats)
                trans_text = translated_lines[j] if j < len(translated_lines) else seg['text']
                # Remove numbering if present
                trans_text = trans_text.split('] ', 1)[-1] if ']' in trans_text else trans_text
                
                translated_segments.append({
                    **seg,
                    'text': trans_text.strip()
                })
            
            print(f"  Translated {min(i+batch_size, len(segments))}/{len(segments)} segments")
        
        print("✅ Translation complete")
        return translated_segments
    
    def generate_srt(self, segments: List[Dict], output_path: str):
        """
        Generate SRT subtitle file from segments
        
        Args:
            segments: List of segments with 'start', 'end', 'text'
            output_path: Output .srt file path
        """
        print(f"📝 Generating SRT file: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(segments, 1):
                # Format timestamps
                start = self._format_timestamp(seg['start'])
                end = self._format_timestamp(seg['end'])
                
                # Write SRT entry
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{seg['text']}\n")
                f.write("\n")
        
        print(f"✅ SRT file created: {output_path}")
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def embed_subtitles(self, video_path: str, srt_path: str, output_path: str, 
                       subtitle_lang: str = 'eng'):
        """
        Embed subtitles into video using FFmpeg
        
        Args:
            video_path: Input video path
            srt_path: Subtitle file path
            output_path: Output video path
            subtitle_lang: Subtitle language code
        """
        print(f"🎬 Embedding subtitles into video...")
        
        # Check FFmpeg
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: FFmpeg not installed. Install from https://ffmpeg.org/")
            sys.exit(1)
        
        # FFmpeg command to embed subtitles
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', srt_path,
            '-c', 'copy',
            '-c:s', 'mov_text',
            '-metadata:s:s:0', f'language={subtitle_lang}',
            output_path,
            '-y'  # Overwrite output
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Video with subtitles created: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: FFmpeg failed: {e.stderr.decode()}")
            sys.exit(1)
    
    def process_video(self, video_path: str, source_lang: str = 'en', 
                     target_langs: List[str] = None, output_dir: str = None,
                     whisper_model: str = 'base', keep_files: bool = True):
        """
        Complete video translation pipeline
        
        Args:
            video_path: Input video file
            source_lang: Source language code
            target_langs: List of target language codes (None = just transcribe)
            output_dir: Output directory (default: same as input)
            whisper_model: Whisper model size
            keep_files: Keep intermediate SRT files
        """
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"ERROR: Video file not found: {video_path}")
            sys.exit(1)
        
        # Setup output directory
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = video_path.parent
        
        # Step 1: Transcribe
        result = self.transcribe_video(str(video_path), source_lang, whisper_model)
        
        # Step 2: Save original transcription as SRT
        original_srt = output_dir / f"{video_path.stem}_{source_lang}.srt"
        self.generate_srt(result['segments'], str(original_srt))
        
        # Step 3: Translate to target languages
        if target_langs:
            for target_lang in target_langs:
                print(f"\n{'='*60}")
                print(f"Translating to {self.SUPPORTED_LANGUAGES.get(target_lang, target_lang)}")
                print(f"{'='*60}\n")
                
                # Translate segments
                translated = self.translate_segments(
                    result['segments'], 
                    source_lang, 
                    target_lang
                )
                
                # Generate translated SRT
                translated_srt = output_dir / f"{video_path.stem}_{target_lang}.srt"
                self.generate_srt(translated, str(translated_srt))
                
                # Embed subtitles into video
                output_video = output_dir / f"{video_path.stem}_{target_lang}.mp4"
                self.embed_subtitles(
                    str(video_path),
                    str(translated_srt),
                    str(output_video),
                    target_lang
                )
        
        print(f"\n{'='*60}")
        print("✅ ALL PROCESSING COMPLETE!")
        print(f"{'='*60}")
        print(f"Output directory: {output_dir}")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Translate video subtitles using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe English video and translate to Burmese and Thai
  python video_translator.py movie.mp4 --source en --targets my th
  
  # Just transcribe without translation
  python video_translator.py movie.mp4 --source en
  
  # Use smaller Whisper model for faster processing
  python video_translator.py movie.mp4 --source en --targets th --model tiny
  
  # Use local translation (free but lower quality)
  python video_translator.py movie.mp4 --source en --targets my --local
        """
    )
    
    parser.add_argument('video', help='Input video file')
    parser.add_argument('--source', default='en', choices=['en', 'my', 'th'],
                       help='Source language (default: en)')
    parser.add_argument('--targets', nargs='+', choices=['en', 'my', 'th'],
                       help='Target languages for translation')
    parser.add_argument('--output', help='Output directory (default: same as input)')
    parser.add_argument('--model', default='base', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper model size (default: base)')
    parser.add_argument('--api-key', help='Anthropic API key (or set ANTHROPIC_API_KEY env var)')
    parser.add_argument('--local', action='store_true',
                       help='Use local translation instead of Claude API (lower quality)')
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create translator
    translator = VideoTranslator(
        api_key=args.api_key,
        use_local_translation=args.local
    )
    
    # Process video
    translator.process_video(
        video_path=args.video,
        source_lang=args.source,
        target_langs=args.targets,
        output_dir=args.output,
        whisper_model=args.model
    )


if __name__ == '__main__':
    main()
