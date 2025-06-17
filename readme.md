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

- **🌍 Multi-language Support:** Instantly translate subtitles into 15+ languages.
- **🗂️ Batch Processing:** Translate a single file or an entire folder at once.
- **🔄 Format Conversion:** Convert `.ass` and plain `.txt` files to `.srt` with translation.
- **🖱️ Simple GUI:** User-friendly interface powered by PyQt5.
- **💾 Organized Output:** Saves translated files in neatly named folders.
- **⚡ Fast & Automated:** No manual copy-pasting or web tools needed.

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

- **Choose** to process a single file or an entire folder.
- **Select** – your subtitle files (.srt, .ass, .txt).
- **Wait** – For Translations To Complete. Output appears in a New Folder in the selected Direcotry.

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

- **YouTube Creators:** Instantly Provide Subtitles in Multiple Languages.
- **Educators:** Translate Lecture Subtitles for International Students.
- **Film Distributors** – Localize Content For Global Audiences.

---

### 📂 Project Structure

```bash
srt_maker/
├── main.py
├── requirements.txt
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