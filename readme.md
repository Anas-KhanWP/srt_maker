# 🎬 SRT Maker – Professional Subtitle Translation Tool

> **Advanced subtitle translation with offline AI models, GPU acceleration, and intelligent caching**

---

## 📚 Table of Contents

- [🚀 Project Purpose](#-project-purpose)
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📦 Installation](#-installation)
- [🧑‍💻 Usage Guide](#-usage-guide)
- [⚙️ Configuration](#️-configuration)
- [🤖 AI Translation Models](#-ai-translation-models)
- [⌨️ Keyboard Shortcuts](#️-keyboard-shortcuts)
- [🌐 Multi-Language UI](#-multi-language-ui)
- [📂 Project Structure](#-project-structure)
- [🔧 Building from Source](#-building-from-source)
- [👥 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🚀 Project Purpose

**What It Does:**  
SRT Maker is a professional desktop application that translates subtitle files (`.srt`, `.ass`, `.txt`) into 100+ languages using both online APIs and offline AI models, with GPU acceleration, intelligent caching, and automated workflows.

**Why It Matters:**  
Creating multilingual content manually is time-consuming and expensive. SRT Maker automates subtitle translation with professional-grade features, making global content accessible for creators, educators, and media professionals.

---

## ✨ Key Features

### 🌍 **Translation Engine**
- **100+ Languages:** Support for all Google Translate languages
- **Intelligent Batching:** Optimized API usage with smart text grouping
- **Translation Caching:** Persistent cache system for improved performance
- **Error Recovery:** Automatic retry with exponential backoff
- **Split Mismatch Handling:** Advanced error detection and fallback mechanisms

### 🗂️ **File Management**
- **Multi-Format Support:** SRT, ASS, and plain text files
- **Drag & Drop Interface:** Intuitive file and folder selection
- **Batch Processing:** Process entire folders simultaneously
- **Custom Output Naming:** Template-based file naming with variables
- **Encoding Options:** Multiple text encoding support (UTF-8, UTF-16, ASCII, Latin-1)

### 👁️ **Folder Monitoring**
- **Multi-Folder Watchlist:** Monitor multiple directories simultaneously
- **Auto-Translation:** Automatic processing of new files
- **Queue Management:** Intelligent queuing system for concurrent file detection
- **Activity Logging:** Advanced color-coded activity tracking
- **Persistent Watchlist:** Saved monitoring configuration

### 🎯 **User Experience**
- **Translation Profiles:** Save and switch between language combinations
- **Recent Files:** Quick access to previously processed files
- **File Preview:** Built-in subtitle content preview
- **Multi-Language UI:** Interface available in 100+ languages with auto-translation
- **Layout Customization:** Resizable interface with state persistence
- **Keyboard Navigation:** Full accessibility support with shortcuts

### 📊 **Analytics & Monitoring**
- **Real-Time Statistics:** Track files, languages, and subtitles processed
- **Performance Metrics:** Cache hit ratios and processing speeds
- **Multi-Level Progress:** File, language, and subtitle-level progress tracking
- **Session Management:** Statistics reset and session tracking

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/python-3.11+-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.11-green)
![deep-translator](https://img.shields.io/badge/deep--translator-1.11.4-yellow)
![pysrt](https://img.shields.io/badge/pysrt-1.1.2-orange)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1.2-red)
![Transformers](https://img.shields.io/badge/Transformers-4.36.2-orange)

- **Python 3.11+** – Core application framework
- **PyQt5** – Professional GUI with dark theme
- **PyTorch** – GPU acceleration for offline models
- **Transformers** – Hugging Face AI translation models
- **deep-translator** – Google Translate API integration
- **pysrt** – Professional SRT file handling
- **matplotlib** – Performance analytics and charts

---

## 📦 Installation

### 🚀 **Option 1: Windows Installer (Recommended)**

1. Download `SRT_Maker_Installer.exe` from releases
2. Run installer as administrator
3. Choose to install PyTorch with CUDA for GPU acceleration
4. Launch from Start Menu or Desktop shortcut

### 🛠️ **Option 2: Manual Setup**

```bash
# Clone repository
git clone https://github.com/Anas-KhanWP/srt_maker.git
cd srt_maker

# Run setup script (installs Python if needed)
setup.bat

# Or install manually
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Run application
python main.py
```

## 🤖 AI Translation Models

### 🌐 **Google Translate (Recommended)**
- **Languages:** 100+ supported languages
- **Quality:** High accuracy for most language pairs
- **Speed:** Fast API-based translation
- **Requirements:** Internet connection
- **Cost:** Free with rate limits

### 🖥️ **Marian MT (Offline)**
- **Languages:** Common language pairs (en-es, en-fr, etc.)
- **Quality:** Good for supported pairs
- **Speed:** Fast with GPU acceleration
- **Requirements:** ~500MB per language pair
- **Cost:** Free, no internet needed

### ⚙️ **Opus-MT (Offline)**
- **Languages:** Alternative offline models
- **Quality:** Varies by language pair
- **Speed:** Moderate processing speed
- **Requirements:** Model downloads
- **Cost:** Free offline processing

---

## 🧑‍💻 Usage Guide

### 4. Quick Start Guide

#### **Main Tab - Translation**
1. **Select Files:** Use drag & drop or buttons to select subtitle files
2. **Review Languages:** View configured languages as visual tags
3. **Start Processing:** Click "Start Translation" or press F5
4. **Monitor Progress:** Track real-time progress across multiple levels

#### **Settings Tab - Configuration**
1. **Language Selection:** Choose from 100+ languages with search and filtering
2. **Translation Profiles:** Create and manage language combinations
3. **Output Settings:** Configure file organization and naming templates
4. **UI Language:** Switch interface language with auto-translation
5. **Advanced Options:** Batch size, retry count, encoding settings

#### **Watch Folder Tab - Automation**
1. **Add Folders:** Build a watchlist of directories to monitor
2. **Auto-Processing:** Enable automatic translation of new files
3. **Activity Monitoring:** View real-time file detection and processing logs
4. **Queue Management:** Handle multiple simultaneous file detections

#### **Preview Tab - File Inspection**
- Preview subtitle content before translation
- Quick file switching and content validation

#### **Statistics Tab - Analytics**
- View session statistics and performance metrics
- Monitor cache efficiency and processing speeds

---

## ⚙️ Advanced Configuration

### **Custom Output Naming Templates**
Use variables in your output file naming:
- `{filename}` - Original filename
- `{language}` - Target language name
- `{date}` - Current date (YYYYMMDD)
- `{time}` - Current time (HHMMSS)

**Example:** `{filename}_{language}_{date}` → `movie_Spanish_20241201.srt`

### **Translation Profiles**
Create reusable language combinations:
1. Configure desired languages in Settings
2. Click "Create Profile" in Profiles menu
3. Switch between profiles instantly

### **Folder Monitoring**
Set up automated translation workflows:
1. Add directories to watchlist
2. Enable auto-translation
3. New files are automatically processed

---

## ⌨️ Keyboard Shortcuts

### **File Operations**
- `Ctrl+O` - Open single file
- `Ctrl+Shift+O` - Open folder
- `Ctrl+S` / `F5` - Start translation
- `Escape` - Stop translation
- `Ctrl+Q` - Quit application

### **Navigation**
- `Ctrl+1-6` - Switch between tabs
- `Alt+F` - Focus file selection
- `Alt+L` - Focus language selection
- `Alt+P` - Focus progress log

---

## 🌐 Multi-Language UI

The application interface supports 100+ languages with automatic translation:

1. **Language Selection:** Go to Settings → UI Settings
2. **Choose Language:** Select from dropdown (e.g., "Arabic (ar)", "Chinese (zh-CN)")
3. **Instant Translation:** UI updates immediately
4. **Background Processing:** All languages pre-translated for instant switching

**Supported Languages:** All Google Translate supported languages including Arabic, Chinese, Spanish, French, German, Japanese, Korean, Russian, and many more.

---

## 📂 Project Structure

```
srt_maker/
├── main.py              # Main application with all features
├── settings.json        # Unified settings, profiles, and cache
├── requirements.txt     # Python dependencies
├── cache_*.json        # Translation cache files (auto-generated)
├── README.md           # This documentation
└── .gitignore         # Git ignore rules
```

---

## 🔧 Building from Source

### 📦 **Create Installer**
```bash
# Build Windows installer with NSIS
build_installer.bat

# Creates: SRT_Maker_Installer.exe
```

### 💾 **Create Portable Version**
```bash
# Build standalone executable
build.bat

# Creates: dist/SRT_Maker.exe
```

### 🛠️ **Development Setup**
```bash
# Install development dependencies
pip install pyinstaller
pip install auto-py-to-exe

# Run from source
python main.py
```

---

## 👥 Contributing

### **Getting Started**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### **Development Standards**
- Follow PEP8 for Python code formatting
- Add comprehensive docstrings for new functions
- Test new features across multiple languages
- Update README for significant feature additions

### **Feature Requests**
- Use GitHub Issues for feature requests
- Provide detailed use cases and examples
- Consider backward compatibility

---

## 📄 License

### **MIT License**
This project is licensed under the MIT License - see LICENSE file for details.

### **Dependencies**
- **Google Translate API** via deep-translator
- **Helsinki-NLP Models** for offline translation
- **PyQt5** for professional GUI framework
- **PyTorch** for GPU acceleration
- **Hugging Face Transformers** for AI models

### **Acknowledgments**
Thanks to the open-source AI and translation communities for making multilingual content accessible.

---

**Made with ❤️ for creators, educators, and the global community**