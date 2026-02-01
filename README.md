# 🎬 AI Video Translator

Complete solution for translating movies and videos with AI-powered transcription and translation.

**Languages Supported:** English ↔ Burmese/Myanmar ↔ Thai

---

## 📦 What's Included

```
video-translation-toolkit/
├── video_translator.py       # Main translation script
├── batch_translator.py       # Batch processing for multiple videos
├── web_interface.html        # Simple web UI (demonstration)
├── config_template.yaml      # Configuration template
├── SETUP_GUIDE.md           # Detailed setup instructions
└── README.md                # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install openai-whisper anthropic

# Install FFmpeg
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### 2. Get API Key (Optional but Recommended)

For best translation quality (especially Burmese/Thai):
1. Go to https://console.anthropic.com/
2. Create an account and get your API key
3. Set it as environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 3. Translate Your First Video

```bash
# English to Burmese
python video_translator.py your_movie.mp4 --source en --targets my

# English to Thai
python video_translator.py your_movie.mp4 --source en --targets th

# English to both Burmese and Thai
python video_translator.py your_movie.mp4 --source en --targets my th
```

---

## 💡 Usage Examples

### Single Video Translation

```bash
# Basic usage
python video_translator.py movie.mp4 --source en --targets my

# With specific output directory
python video_translator.py movie.mp4 --source en --targets my --output ./translated/

# Use better Whisper model for higher quality
python video_translator.py movie.mp4 --source en --targets my --model medium

# Use local translation (free but lower quality)
python video_translator.py movie.mp4 --source en --targets my --local
```

### Batch Processing Multiple Videos

```bash
# Process all videos in a directory
python batch_translator.py ./movies --source en --targets my th

# Process recursively (including subdirectories)
python batch_translator.py ./movies --source en --targets my --recursive

# Skip videos that already have outputs
python batch_translator.py ./movies --source en --targets my --skip-existing
```

### Just Creating Subtitles (No Translation)

```bash
# Create English subtitles from English audio
python video_translator.py movie.mp4 --source en
```

---

## 📊 How It Works

```
INPUT: Movie file (MP4, MKV, AVI, MOV)
    ↓
STEP 1: Extract and transcribe audio with Whisper
    ↓
STEP 2: Translate subtitles with Claude API (or local models)
    ↓
STEP 3: Generate .srt subtitle files
    ↓
STEP 4: Embed subtitles into video with FFmpeg
    ↓
OUTPUT: Translated video + subtitle files
```

---

## 💰 Cost Analysis

### Option 1: FREE (100% Local)
- **Cost:** $0
- **Quality:** ⭐⭐⭐ (3/5)
- **Setup:** `pip install openai-whisper argostranslate`
- **Use:** `--local` flag

### Option 2: HYBRID (Recommended)
- **Cost:** ~$0.30 per 2-hour movie
- **Quality:** ⭐⭐⭐⭐⭐ (5/5)
- **Setup:** `pip install openai-whisper anthropic`
- **Best for:** Burmese/Thai translation

### Option 3: FULL CLOUD
- **Cost:** ~$1.50 per 2-hour movie
- **Quality:** ⭐⭐⭐⭐⭐ (5/5)
- **Speed:** Fastest
- **Best for:** No local GPU

---

## 🎯 Which Approach Should You Choose?

### Choose FREE if:
- ✅ You have zero budget
- ✅ You don't need perfect translation quality
- ✅ You're okay with slower processing
- ❌ Not recommended for Burmese/Thai (poor quality)

### Choose HYBRID (Recommended) if:
- ✅ You want best translation quality
- ✅ You're translating to/from Burmese or Thai
- ✅ You have ~$0.30/movie budget
- ✅ You have a decent computer

### Choose FULL CLOUD if:
- ✅ You need fastest processing
- ✅ You don't have a powerful computer
- ✅ Budget is not a concern (~$1.50/movie)

---

## ⚙️ Configuration Options

### Whisper Model Sizes

| Model  | Size  | Speed    | Quality   | RAM   |
|--------|-------|----------|-----------|-------|
| tiny   | 39MB  | Very Fast| Good      | 1GB   |
| base   | 74MB  | Fast     | Better    | 1GB   |
| small  | 244MB | Medium   | Great     | 2GB   |
| medium | 769MB | Slow     | Excellent | 5GB   |
| large  | 1.5GB | Very Slow| Best      | 10GB  |

**Recommendation:**
- Fast computer/GPU: `medium` or `large`
- Average computer: `base` or `small`
- Slow computer: `tiny`

### Language Codes

- `en` - English
- `my` - Burmese/Myanmar
- `th` - Thai

---

## 📁 Output Files

After processing `movie.mp4`, you'll get:

```
movie_en.srt          # English subtitles (transcription)
movie_my.srt          # Burmese subtitles
movie_my.mp4          # Video with Burmese subtitles embedded
movie_th.srt          # Thai subtitles
movie_th.mp4          # Video with Thai subtitles embedded
```

---

## 🔧 Advanced Features

### Using Claude in Claude (Artifacts)

You can also use this directly in Claude.ai:
1. Upload your video
2. Ask: "Translate this video from English to Burmese"
3. Claude will process it automatically

### API Integration

```python
from video_translator import VideoTranslator

# Create translator
translator = VideoTranslator(api_key="your-key")

# Process video
translator.process_video(
    video_path="movie.mp4",
    source_lang="en",
    target_langs=["my", "th"],
    whisper_model="base"
)
```

### Custom Workflows

See `config_template.yaml` for all configuration options.

---

## 🐛 Troubleshooting

### "FFmpeg not found"
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

### "Out of memory"
```bash
# Use smaller Whisper model
python video_translator.py movie.mp4 --model tiny
```

### "Translation quality is poor"
```bash
# Make sure you're using Claude API (not --local)
export ANTHROPIC_API_KEY="your-key"
python video_translator.py movie.mp4 --source en --targets my
```

### "Slow transcription"
```bash
# Install GPU-enabled PyTorch for NVIDIA GPUs
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 📈 Performance Tips

1. **Use GPU:** 10-20x faster with NVIDIA GPU
2. **Batch processing:** Use `batch_translator.py` for multiple videos
3. **Smaller models:** Use `tiny` or `base` for quick previews
4. **Parallel processing:** Can run multiple videos simultaneously

---

## 🌟 Best Practices

### For Burmese/Myanmar Translation:
- ✅ **Always use Claude API** (not local translation)
- ✅ Use `base` or higher Whisper model
- ✅ Review first few minutes before processing full movie

### For Thai Translation:
- ✅ Claude API recommended (Google Translate acceptable)
- ✅ Use `base` or higher Whisper model

### For English Transcription:
- ✅ Whisper is excellent (use local, free)
- ✅ `base` model is usually sufficient

---

## 📚 Documentation

- **SETUP_GUIDE.md** - Detailed installation and setup
- **config_template.yaml** - All configuration options
- **web_interface.html** - Web UI demonstration

---

## 🎓 Tutorial: Complete Workflow

### Step-by-step for translating a movie:

1. **Install everything:**
```bash
pip install openai-whisper anthropic
sudo apt install ffmpeg
export ANTHROPIC_API_KEY="your-key"
```

2. **Process a single movie:**
```bash
python video_translator.py Avatar.mp4 --source en --targets my th
```

3. **Wait for processing** (15-30 minutes for 2-hour movie)

4. **Get your files:**
```
Avatar_my.mp4  # Burmese version
Avatar_th.mp4  # Thai version
Avatar_my.srt  # Burmese subtitles
Avatar_th.srt  # Thai subtitles
```

5. **For multiple movies:**
```bash
python batch_translator.py ./movies --source en --targets my th
```

---

## 💪 What Can You Build?

This toolkit enables you to:

- **Personal:** Translate foreign movies to watch
- **Business:** Localize video content for different markets
- **Education:** Create multilingual educational content
- **Archival:** Preserve and translate historical videos
- **Content Creation:** Add subtitles to YouTube videos

---

## 🤝 Support

For issues or questions:
1. Check **SETUP_GUIDE.md** for detailed troubleshooting
2. Review error messages carefully
3. Make sure all dependencies are installed
4. Verify API key is set correctly

---

## 📜 License

This toolkit uses:
- **Whisper** - MIT License (OpenAI)
- **FFmpeg** - LGPL/GPL
- **Claude API** - Anthropic Terms of Service

---

## 🎉 Quick Reference

```bash
# Basic translation
python video_translator.py movie.mp4 --source en --targets my

# Batch processing
python batch_translator.py ./movies --source en --targets my th

# Best quality
python video_translator.py movie.mp4 --source en --targets my --model large

# Fastest (lower quality)
python video_translator.py movie.mp4 --source en --targets my --model tiny --local

# Just subtitles
python video_translator.py movie.mp4 --source en
```

---

**Happy Translating! 🎬🌍**
