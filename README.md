# VoiceCraft

A complete PDF-to-audiobook converter with AI voice cloning capabilities. Transform any PDF document into a personalized audiobook using your own voice or high-quality TTS engines.

## Features

- **Multi-Engine TTS Support**: System TTS, pyttsx3, Microsoft Edge TTS, and Coqui TTS
- **Voice Cloning**: Clone any voice using 30+ seconds of sample audio
- **Smart PDF Processing**: Robust text extraction with automatic cleaning
- **Page-by-Page Output**: Individual audio files for easy navigation
- **User-Friendly GUI**: No command-line knowledge required
- **Cross-Platform**: Windows, macOS, and Linux support

## Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for voice cloning)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voicecraft.git
cd voicecraft
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run VoiceCraft:
```bash
python voicecraft.py
```

## Usage

### Basic Conversion
1. Launch the application
2. Select your PDF document
3. Choose a TTS engine (System TTS works immediately)
4. Click "START PDF TO AUDIOBOOK CONVERSION"

### Voice Cloning
1. Record 30-60 seconds of clear speech
2. Enable "Voice Cloning" in the interface
3. Upload your voice sample
4. Select "Coqui TTS" for best results
5. Start conversion

## Dependencies

### Core Requirements
```
PyPDF2>=3.0.0
pdfplumber>=0.7.0
```

### TTS Engines (Optional)
```
pyttsx3>=2.90          # Local Python TTS
edge-tts>=6.1.0        # Microsoft Edge TTS
TTS>=0.22.0            # Coqui TTS (voice cloning)
```

### Audio Processing
```
librosa>=0.10.0        # Audio analysis (optional)
soundfile>=0.12.0      # Audio file support
```

## Supported Formats

**Input**: PDF documents with extractable text
**Output**: WAV audio files (44.1kHz, 16-bit)
**Voice Samples**: WAV, MP3, FLAC, M4A

## Voice Sample Guidelines

For optimal voice cloning results:
- Duration: 30-60 seconds
- Quality: Clear recording, no background noise
- Content: Varied sentences and natural speech
- Format: WAV preferred, MP3 acceptable
- Single speaker only

## Project Structure

```
voicecraft/
├── voicecraft.py              # Main application
├── requirements.txt           # Dependencies
├── README.md                 # This file
├── examples/
│   ├── sample.pdf            # Test PDF
│   └── voice_sample.wav      # Example voice sample
└── docs/
    ├── installation.md       # Detailed setup guide
    └── troubleshooting.md    # Common issues
```

## Engine Comparison

| Engine | Quality | Speed | Voice Cloning | Requirements |
|--------|---------|--------|---------------|--------------|
| System TTS | Good | Fast | Basic | None |
| pyttsx3 | Fair | Medium | None | Minimal |
| Edge TTS | Excellent | Medium | Matching | Internet |
| Coqui TTS | Outstanding | Slow | Full | High |

## Configuration

The application automatically detects available TTS engines. Install additional engines as needed:

```bash
# For Edge TTS
pip install edge-tts

# For voice cloning
pip install TTS torch torchaudio
```

## Troubleshooting

**PDF text extraction fails**: Try with a different PDF or check if text is selectable in a PDF viewer.

**Voice cloning produces poor quality**: Ensure voice sample is clear, 30+ seconds, and single speaker only.

**TTS engine not available**: Install the required dependencies or use the built-in installer buttons.

**Memory issues**: Close other applications or use System TTS instead of Coqui TTS.

## Performance Tips

- Use GPU acceleration for Coqui TTS: `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118`
- Process smaller PDFs first to test your setup
- Close unnecessary applications during conversion
- Use SSD storage for faster file operations

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting pull requests.

### Areas for Contribution
- Additional TTS engine integrations
- Multi-language support
- Audio post-processing features
- UI/UX improvements
- Documentation and examples

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Coqui TTS](https://github.com/coqui-ai/TTS) for neural voice synthesis
- [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF text extraction
- [Microsoft Edge TTS](https://github.com/rany2/edge-tts) for high-quality voices

## Changelog

### v1.0.0
- Initial release with multi-engine TTS support
- Voice cloning integration
- Complete GUI interface
- Cross-platform compatibility

## Support

For questions or issues:
1. Check the troubleshooting guide
2. Search existing GitHub issues
3. Open a new issue with detailed information

---

**Note**: This software is intended for personal and educational use. Ensure you have appropriate rights to process any documents and respect voice cloning ethics.