# 🎬 SRT Maker – Effortless Subtitle Translation & Conversion

> **Translate and convert subtitle files into multiple languages with a single click!**

---

## 📚 Table of Contents

- [🚀 Project Purpose](#-project-purpose)
- [📦 Features & Screenshots](#-features--screenshots)
- [🛠️ Tech Stack](#️-tech-stack)
- [🧑‍💻 Installation & Usage](#-installation--usage)
- [✅ Examples & Output](#-examples--output)
- [📂 Project Structure](#-project-structure)
- [👥 Contribution Guidelines](#-contribution-guidelines)
- [🧪 Tests](#-tests)
- [📄 License & Attribution](#-license--attribution)
- [🏷️ Badges](#-badges)

---

## 🚀 Project Purpose

**What It Does:**  
SRT Maker is a desktop tool that batch-translates and converts subtitle files (`.srt`, `.ass`, `.txt`) into multiple languages using Google Translate, saving the results in organized folders.

**Why It Matters:**  
Subtitle translation is tedious and repetitive. SRT Maker automates this process, making multilingual content creation fast and accessible for creators, educators, and translators.

---

## 📦 Features & Screenshots

- **🌍 Multi-language Support:** Instantly translate subtitles into 100+ languages from Google Translate.
- **🗂️ Batch Processing:** Translate a single file or an entire folder at once.
- **🔄 Format Conversion:** Convert `.ass` and plain `.txt` files to `.srt` with translation.
- **🖱️ Modern UI:** User-friendly tabbed interface with dark mode.
- **💾 Organized Output:** Customizable output organization with folder options.
- **⚡ Fast & Automated:** Translation caching for improved performance.
- **⚙️ Customizable Settings:** Configure languages, output options, and more.
- **📊 Detailed Progress:** Multi-level progress tracking for files, languages, and subtitles.

### Screenshots

> _Add your screenshots or GIFs here!_

![SRT Maker GUI Example](https://placehold.co/600x400?text=GUI+Screenshot)
![Batch Processing Output](https://placehold.co/600x400?text=Batch+Processing)

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/python-3.11-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.11-green)
![deep-translator](https://img.shields.io/badge/deep--translator-1.11.4-yellow)
![pysrt](https://img.shields.io/badge/pysrt-1.1.2-orange)

- **Python 3.11**
- **PyQt5** – GUI framework
- **pysrt** – SRT file handling
- **ass** – ASS subtitle parsing
- **deep-translator** – Google Translate API

---

## 🧑‍💻 Installation & Usage

### 1. Clone the Repository

```sh
git clone https://github.com/Anas-KhanWP/srt_maker.git
cd srt_maker
```

---

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

---

### 3. Run The App

```sh
python main.py
```

---

### 4. Using The Tool

#### Main Tab
- **Select Files:** Choose a single file or an entire folder of subtitle files.
- **View Languages:** See all configured languages as tags that will be processed.
- **Start Translation:** Click the Start button to begin the translation process.
- **Monitor Progress:** Track file, language, and subtitle progress in real-time.

#### Settings Tab
- **Configure Languages:** Select from 100+ languages supported by Google Translate.
- **Output Options:** Choose how files are organized and handled.
- **Translation Settings:** Configure batch size and retry options.
- **Cache Management:** Enable/disable caching and clear the cache when needed.

#### About Tab
- View application information, features, and credits.

---

### ✅ Examples & Output

**Original SRT**

```sh
1
00:00:01,000 --> 00:00:03,000
Hello, world!
```

Sample Output:
**Spanish Translation**

```sh
1
00:00:01,000 --> 00:00:03,000
¡Hola, mundo!
```

### Use Cases

- **YouTube Creators:** Instantly provide subtitles in multiple languages.
- **Educators:** Translate lecture subtitles for international students.
- **Film Distributors:** Localize content for global audiences.
- **Content Creators:** Make videos accessible to wider audiences.

---

### 📂 Project Structure

```bash
srt_maker/
├── main.py           # Main application code
├── settings.json     # User settings and preferences
├── requirements.txt  # Dependencies
└── .gitignore
```

---

### 👥 Contribution Guidelines

1. Fork the repo and create your branch: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -am 'Add new feature'`
3. Push to the branch: `git push origin feature/your-feature`
4. Open a Pull Request.


### Code Style:

- Follow PEP8 for Python Code.
- Write Clear Commit Messages

---

### 🧪 Tests

No automated tests yet.
To test manually, run the app and try translating various subtitle files.
PRs with test coverage are welcome!

---

### 📄 License & Attribution

- **License:** MIT License

### Credits:

1. PyQt5
2. pysrt
3. deep-translator
4. ass
5. Google Translate

### 🏷️ Badges
<img alt="Build" src="https://img.shields.io/badge/build-passing-brightgreen">
<img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
<img alt="Last Commit" src="https://img.shields.io/github/last-commit/Anas-KhanWP/srt_maker">
<img alt="Issues" src="https://img.shields.io/github/issues/Anas-KhanWP/srt_maker">
<img alt="PRs" src="https://img.shields.io/github/issues-pr/Anas-KhanWP/srt_maker">