# Video Translation Setup Guide

Complete guide to set up your movie translation system for English ↔ Burmese/Myanmar/Thai

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (8GB+ recommended)
- FFmpeg installed

### Installation

```bash
# 1. Install Python packages
pip install openai-whisper anthropic

# 2. Install FFmpeg
# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html

# 3. Download the video translator
# (You already have video_translator.py)

# 4. Set up API key (for high-quality translation)
export ANTHROPIC_API_KEY="your-api-key-here"
# Or create a .env file with: ANTHROPIC_API_KEY=your-api-key-here
```

### First Translation

```bash
# Transcribe English video and translate to Burmese
python video_translator.py your_movie.mp4 --source en --targets my

# Translate to both Burmese and Thai
python video_translator.py your_movie.mp4 --source en --targets my th

# Just create English subtitles (no translation)
python video_translator.py your_movie.mp4 --source en
```

---

## Setup Options

### Option 1: FREE (Local Only) - No API Key Needed

**What you get:**
- ✅ Free transcription with Whisper
- ⚠️ Basic translation (lower quality for Burmese/Thai)
- ✅ Free video encoding

**Setup:**
```bash
pip install openai-whisper argostranslate
python video_translator.py movie.mp4 --source en --targets my --local
```

**Cost:** $0
**Quality:** Medium (transcription excellent, translation basic)

---

### Option 2: RECOMMENDED (Whisper + Claude API)

**What you get:**
- ✅ Free transcription with Whisper
- ✅ Excellent translation with Claude
- ✅ Free video encoding

**Setup:**
```bash
pip install openai-whisper anthropic

# Get API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-..."

python video_translator.py movie.mp4 --source en --targets my th
```

**Cost:** ~$0.20-0.50 per 2-hour movie
**Quality:** Excellent (especially for Burmese/Thai)

---

### Option 3: CLOUD TRANSCRIPTION (All APIs)

**What you get:**
- ✅ Fast cloud transcription
- ✅ Excellent translation
- ✅ No local GPU needed

**Setup:**
```bash
pip install anthropic assemblyai

export ANTHROPIC_API_KEY="sk-ant-..."
export ASSEMBLYAI_API_KEY="your-key"

# Modify script to use AssemblyAI (see advanced usage)
```

**Cost:** ~$1-3 per movie
**Quality:** Excellent
**Speed:** Fastest

---

## Whisper Model Sizes

Choose based on your computer and accuracy needs:

| Model  | Size  | RAM  | Speed    | Accuracy |
|--------|-------|------|----------|----------|
| tiny   | 39MB  | 1GB  | Very Fast| Good     |
| base   | 74MB  | 1GB  | Fast     | Better   |
| small  | 244MB | 2GB  | Medium   | Great    |
| medium | 769MB | 5GB  | Slow     | Excellent|
| large  | 1550MB| 10GB | Very Slow| Best     |

**Recommendation:**
- **Fast computer/GPU:** Use `medium` or `large`
- **Average computer:** Use `base` or `small`
- **Slow/old computer:** Use `tiny`

```bash
# Use tiny model (fastest)
python video_translator.py movie.mp4 --source en --targets my --model tiny

# Use large model (best quality)
python video_translator.py movie.mp4 --source en --targets my --model large
```

---

## Usage Examples

### Basic Usage

```bash
# English to Burmese
python video_translator.py movie.mp4 --source en --targets my

# English to Thai
python video_translator.py movie.mp4 --source en --targets th

# English to both Burmese and Thai
python video_translator.py movie.mp4 --source en --targets my th

# Burmese to English
python video_translator.py movie.mp4 --source my --targets en

# Just create English subtitles (no translation)
python video_translator.py movie.mp4 --source en
```

### Advanced Usage

```bash
# Specify output directory
python video_translator.py movie.mp4 --source en --targets my --output ./translated/

# Use specific Whisper model
python video_translator.py movie.mp4 --source en --targets my --model medium

# Use local translation (free but lower quality)
python video_translator.py movie.mp4 --source en --targets my --local

# Provide API key directly (instead of environment variable)
python video_translator.py movie.mp4 --source en --targets my --api-key sk-ant-xxx
```

### Batch Processing

```bash
# Process multiple movies
for movie in *.mp4; do
    python video_translator.py "$movie" --source en --targets my th
done

# Or create a batch script (see batch_translator.py)
```

---

## Output Files

After processing `movie.mp4`, you'll get:

```
movie_en.srt          # English subtitles (original transcription)
movie_my.srt          # Burmese subtitles
movie_my.mp4          # Video with embedded Burmese subtitles
movie_th.srt          # Thai subtitles
movie_th.mp4          # Video with embedded Thai subtitles
```

---

## Cost Calculator

### Per Movie (2 hours):

**FREE Option (Local):**
- Transcription: $0 (Whisper local)
- Translation: $0 (Local models)
- Encoding: $0 (FFmpeg)
- **Total: $0**

**RECOMMENDED Option (Whisper + Claude):**
- Transcription: $0 (Whisper local)
- Translation: ~$0.30 (Claude API, ~15k tokens)
- Encoding: $0 (FFmpeg)
- **Total: ~$0.30**

**CLOUD Option (All APIs):**
- Transcription: ~$1.20 (AssemblyAI, 120 minutes)
- Translation: ~$0.30 (Claude API)
- Encoding: $0 (FFmpeg)
- **Total: ~$1.50**

### Monthly (10 movies):
- FREE: $0
- RECOMMENDED: ~$3
- CLOUD: ~$15

---

## Troubleshooting

### "FFmpeg not found"
```bash
# Install FFmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

### "Whisper not installed"
```bash
pip install openai-whisper
# If GPU issues, also install: pip install torch torchvision torchaudio
```

### "Out of memory"
```bash
# Use smaller Whisper model
python video_translator.py movie.mp4 --source en --targets my --model tiny
```

### "Translation quality is poor"
```bash
# Make sure you're using Claude API (not --local)
# Check API key is set: echo $ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY="sk-ant-..."
```

### GPU Not Detected (Slow transcription)
```bash
# Install CUDA-enabled PyTorch (for NVIDIA GPUs)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## Performance Tips

1. **Use GPU:** Whisper runs 10-20x faster with GPU
2. **Batch translation:** Script automatically batches for efficiency
3. **Smaller models:** Use `tiny` or `base` for quick previews
4. **Parallel processing:** Run multiple videos simultaneously

---

## API Keys

### Get Anthropic API Key:
1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Go to API Keys section
4. Create new key
5. Copy and save it

### Set API Key:
```bash
# Option 1: Environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Option 3: Command line
python video_translator.py movie.mp4 --api-key sk-ant-...
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Get API key (if using Claude translation)
3. ✅ Test with a short video
4. ✅ Process your movie library
5. 📚 Check batch_translator.py for automation

---

## Need Help?

- **Whisper Issues:** https://github.com/openai/whisper
- **FFmpeg Issues:** https://ffmpeg.org/
- **Claude API:** https://docs.anthropic.com/
