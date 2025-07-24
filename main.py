import os
import sys
import time
import hashlib
import json
import shutil
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QSize, QRect, QPoint
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Flow Layout for language tags
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        self.itemList = []
        self.margin = margin
        self.spacing = spacing
        
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.itemList.append(item)
    
    def count(self):
        return len(self.itemList)
    
    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None
    
    def expandingDirections(self):
        return QtCore.Qt.Orientations(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.margin, 2 * self.margin)
        return size
    
    def doLayout(self, rect, testOnly):
        x = rect.x() + self.margin
        y = rect.y() + self.margin
        lineHeight = 0
        
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing
            spaceY = self.spacing
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x() + self.margin
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        
        return y + lineHeight - rect.y() + self.margin
import pysrt
import ass
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES

# Default languages that are enabled
DEFAULT_LANGUAGES = {
    "Spanish": "es", "Dutch": "nl", "Russian": "ru", "German": "de",
    "Turkish": "tr", "Chinese": "zh-CN", "Japanese": "ja", "Persian": "fa",
    "Portuguese": "pt", "Arabic": "ar", "Tamil": "ta", "Telugu": "te",
    "Malayalam": "ml", "Bengali": "bn", "Indonesian": "id", "Filipino": "tl"
}

# Get all available languages from deep-translator
LANGUAGES = {name.title(): code for name, code in GOOGLE_LANGUAGES_TO_CODES.items()}

SUPPORTED_FORMATS = ('.srt', '.ass', '.txt')

DARK_STYLE = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QPushButton {
    background-color: #0d7377;
    border: 2px solid #14a085;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #14a085;
    border-color: #40e0d0;
}
QPushButton:pressed {
    background-color: #0a5d61;
}
QTextEdit {
    background-color: #2d2d2d;
    border: 2px solid #404040;
    border-radius: 8px;
    padding: 10px;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}
QProgressBar {
    border: 2px solid #404040;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d7377, stop:1 #14a085);
    border-radius: 6px;
}
QLabel {
    font-size: 12px;
    font-weight: bold;
}
QGroupBox {
    font-weight: bold;
    border: 2px solid #404040;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
}
QTabWidget::pane {
    border: 2px solid #404040;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #2d2d2d;
    border: 2px solid #404040;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #0d7377;
}
QLineEdit {
    background-color: #2d2d2d;
    border: 2px solid #404040;
    border-radius: 8px;
    padding: 8px;
}
QScrollArea, QListWidget, QTableWidget {
    border: 2px solid #404040;
    border-radius: 8px;
    background-color: #2d2d2d;
}
QListWidget::item {
    padding: 5px;
    border-bottom: 1px solid #404040;
}
QListWidget::item:selected {
    background-color: #0d7377;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
}
QSpinBox, QComboBox {
    background-color: #2d2d2d;
    border: 2px solid #404040;
    border-radius: 8px;
    padding: 5px;
    min-height: 20px;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QStatusBar {
    background-color: #2d2d2d;
    color: #cccccc;
    border-top: 1px solid #404040;
}
"""

class SubtitleTranslator:
    def __init__(self, dest_lang):
        self.translator = GoogleTranslator(source='auto', target=dest_lang)
        self.dest_lang = dest_lang
        self.cache = self._load_cache()
        self.batch_size = 50
    
    def _load_cache(self):
        cache_file = Path(f"./cache/cache_{self.dest_lang}.json")
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        try:
            with open(f"./cache/cache_{self.dest_lang}.json", 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving cache: {e}")
    
    def _get_cache_key(self, text):
        return hashlib.md5(text.encode()).hexdigest()
    
    def translate_batch(self, texts):
        results = [None] * len(texts)
        to_translate = []
        indices = []
        
        # Creative header for batch processing
        print(f"\n{'='*80}")
        print(f"🌐 TRANSLATION BATCH: {len(texts)} entries → {self.dest_lang}")
        print(f"{'='*80}")
        
        # Phase 1: Cache analysis
        print(f"\n📊 PHASE 1: CACHE ANALYSIS")
        print(f"{'─'*50}")
        
        cache_hits = 0
        for i, text in enumerate(texts):
            if not text.strip():
                print(f"⚠️  Empty subtitle at position {i} - skipping")
                results[i] = text
                continue
            
            clean_text = text.split(":")[-1] if ":" in text else text
            cache_key = self._get_cache_key(clean_text)
            
            if cache_key in self.cache:
                cache_hits += 1
                results[i] = self.cache[cache_key]
                if i % 20 == 0 or i < 3:  # Show first few and occasional others
                    print(f"💾 [{i:4d}] Cache hit: \"{clean_text[:30]}{'...' if len(clean_text) > 30 else ''}\"")
            else:
                to_translate.append(clean_text)
                indices.append(i)
        
        # Cache statistics
        if texts:
            cache_ratio = cache_hits/len(texts)*100
            print(f"\n📈 Cache efficiency: {cache_hits}/{len(texts)} entries ({cache_ratio:.1f}%)")
            
            if cache_ratio == 100:
                print("✨ PERFECT CACHE HIT! No translation needed.")
            elif cache_ratio > 80:
                print("🚀 EXCELLENT CACHE PERFORMANCE!")
            elif cache_ratio > 50:
                print("👍 GOOD CACHE PERFORMANCE!")
            elif cache_ratio > 20:
                print("🔍 MODERATE CACHE UTILIZATION")
            else:
                print("🆕 MOSTLY NEW CONTENT")
        
        # Phase 2: Translation
        if to_translate:
            print(f"\n🔄 PHASE 2: TRANSLATION")
            print(f"{'─'*50}")
            print(f"📦 Need to translate {len(to_translate)} entries")
            
            for retry in range(3):
                try:
                    print(f"\n🚀 ATTEMPT {retry + 1} {'='*30}")
                    batch_text = "\n\n\n".join(to_translate)
                    print(f"📤 Sending batch to Google Translate API...")
                    
                    # Show a simple spinner
                    start_time = time.time()
                    translated_batch = self.translator.translate(batch_text)
                    elapsed = time.time() - start_time
                    
                    print(f"📥 Response received in {elapsed:.2f}s")
                    translations = translated_batch.split("\n\n\n")
                    
                    if len(translations) != len(to_translate):
                        print(f"\n⚠️  SPLIT MISMATCH DETECTED!")
                        print(f"┌─ Expected: {len(to_translate)} segments")
                        print(f"└─ Received: {len(translations)} segments")
                        print(f"\n♻️  Switching to individual translation mode...")
                        
                        translations = []
                        for i, text in enumerate(to_translate):
                            print(f"   • Translating item {i+1}/{len(to_translate)}...", end="\r")
                            translations.append(self.translator.translate(text))
                        print("\n✅ Individual translations completed!")
                    else:
                        print(f"✅ Batch translation successful!")
                    
                    # Phase 3: Saving results
                    print(f"\n💾 PHASE 3: SAVING RESULTS")
                    print(f"{'─'*50}")
                    
                    for i, (idx, translation) in enumerate(zip(indices, translations)):
                        clean_translation = translation.strip()
                        results[idx] = clean_translation
                        cache_key = self._get_cache_key(to_translate[i])
                        self.cache[cache_key] = clean_translation
                        
                        # Show sample translations (first 3 and last 1)
                        if i < 3 or i == len(indices) - 1:
                            src_preview = to_translate[i][:30] + ('...' if len(to_translate[i]) > 30 else '')
                            tgt_preview = clean_translation[:30] + ('...' if len(clean_translation) > 30 else '')
                            print(f"   • \"{src_preview}\" → \"{tgt_preview}\"")
                        elif i == 3 and len(indices) > 4:
                            print(f"   • ... {len(indices) - 4} more translations ...")
                    
                    print(f"\n🎉 TRANSLATION COMPLETE!")
                    break
                    
                except Exception as e:
                    print(f"\n❌ ERROR: Translation failed (attempt {retry + 1})")
                    print(f"   {str(e)}")
                    
                    if retry < 2:
                        wait_time = 2 ** retry
                        print(f"⏱️  Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        print("❌ All attempts failed! Using original text.")
                        for i, idx in enumerate(indices):
                            results[idx] = to_translate[i]
        
        print(f"\n{'='*80}")
        return results
    
    def translate(self, text):
        print(f"\n{'='*80}")
        print(f"🔤 SINGLE TEXT TRANSLATION → {self.dest_lang}")
        print(f"{'='*80}")
        
        for retry in range(3):
            try:
                print(f"🔄 Attempt {retry + 1}: Translating text...")
                start_time = time.time()
                result = self.translator.translate(text)
                elapsed = time.time() - start_time
                
                print(f"✅ Translation successful in {elapsed:.2f}s!")
                print(f"📝 Original: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
                print(f"🌐 Result:   \"{result[:50]}{'...' if len(result) > 50 else ''}\"")
                print(f"{'='*80}")
                return result
                
            except Exception as e:
                print(f"❌ Translation error (attempt {retry + 1}): {e}")
                if retry < 2:
                    wait_time = 2 ** retry
                    print(f"⏱️  Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        print(f"⚠️  All translation attempts failed, returning original text")
        print(f"{'='*80}")
        return text

class TranslationWorker(QThread):
    progress = pyqtSignal(str)
    file_progress = pyqtSignal(int, int)  # current, total
    language_progress = pyqtSignal(int, int)  # current, total
    subtitle_progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal()
    error = pyqtSignal(str)
    stopped = pyqtSignal()
    
    def __init__(self, files, languages, settings):
        super().__init__()
        self.files = files
        self.languages = languages
        self.settings = settings
        self.is_stopped = False
    
    def run(self):
        try:
            for i, file_path in enumerate(self.files):
                if self.is_stopped:
                    self.stopped.emit()
                    return
                self.file_progress.emit(i + 1, len(self.files))
                self.process_file(file_path, len(self.files), i)
            if not self.is_stopped:
                self.finished.emit()
        except Exception as e:
            if not self.is_stopped:
                self.error.emit(str(e))
    
    def stop(self):
        self.is_stopped = True
    
    def process_file(self, file_path, total_files, current_index):
        path = Path(file_path)
        
        # Create output folder based on settings
        if self.settings.get('organize_by_file', True):
            output_folder = path.parent / path.stem
        else:
            output_folder = path.parent / "translated_subtitles"
        
        output_folder.mkdir(exist_ok=True)
        
        self.progress.emit(f"📁 Processing: {path.name} ({current_index + 1}/{total_files})")
        
        translators = {lang_code: SubtitleTranslator(lang_code) 
                      for lang_code in self.languages.values()}
        
        for i, (language, lang_code) in enumerate(self.languages.items()):
            if self.is_stopped:
                return
            
            self.language_progress.emit(i + 1, len(self.languages))
            
            # Determine output filename based on settings
            if self.settings.get('organize_by_file', True):
                output_file = output_folder / f"{path.stem}_{language}.srt"
            else:
                output_file = output_folder / f"{path.stem}_{language}.srt"
            
            if output_file.exists() and not self.settings.get('overwrite_existing', False):
                self.progress.emit(f"⏭️ {language} already exists, skipping...")
                continue
            
            try:
                translator = translators[lang_code]
                ext = path.suffix.lower()
                
                if ext == '.srt' or (ext == '.txt' and self.is_srt_format(file_path)):
                    self.translate_srt(file_path, output_file, translator)
                elif ext == '.ass':
                    self.translate_ass_to_srt(file_path, output_file, translator)
                elif ext == '.txt':
                    self.translate_plain_txt(file_path, output_file, translator)
                
                if not self.is_stopped:
                    self.progress.emit(f"✅ {language} completed!")
                
            except Exception as e:
                if not self.is_stopped:
                    print(f"❌ Error processing {language}: {e}")
                    self.progress.emit(f"❌ {language} failed: {str(e)}")
        
        if not self.is_stopped:
            # Move or copy original file based on settings
            try:
                if self.settings.get('organize_by_file', True) and self.settings.get('move_original', True):
                    original_in_folder = output_folder / path.name
                    shutil.move(str(path), str(original_in_folder))
                    print(f"📎 Moved original file to: {original_in_folder}")
                elif self.settings.get('organize_by_file', True) and not self.settings.get('move_original', True):
                    original_in_folder = output_folder / path.name
                    shutil.copy2(str(path), str(original_in_folder))
                    print(f"📎 Copied original file to: {original_in_folder}")
            except Exception as e:
                print(f"⚠️ Could not handle original file: {e}")
            
            self.progress.emit(f"🎉 Completed: {path.name}")
    
    def translate_srt(self, input_file, output_file, translator):
        subs = pysrt.open(input_file)
        texts = [sub.text for sub in subs]
        
        for i in range(0, len(texts), translator.batch_size):
            if self.is_stopped:
                return
                
            batch = texts[i:i+translator.batch_size]
            translations = translator.translate_batch(batch)
            
            for j, translation in enumerate(translations):
                subs[i+j].text = translation
            
            progress = min(i+translator.batch_size, len(subs))
            self.subtitle_progress.emit(progress, len(subs))
            print(f"📝 Processed {progress}/{len(subs)} subtitles")
        
        if not self.is_stopped:
            translator._save_cache()
            subs.save(output_file, encoding="utf-8")
    
    def translate_ass_to_srt(self, input_file, output_file, translator):
        with open(input_file, "r", encoding="utf-8-sig") as f:
            doc = ass.parse(f)
        
        texts = [event.text for event in doc.events]
        subs = pysrt.SubRipFile()
        
        for i in range(0, len(texts), translator.batch_size):
            if self.is_stopped:
                return
                
            batch = texts[i:i+translator.batch_size]
            translations = translator.translate_batch(batch)
            
            for j, translation in enumerate(translations):
                event = doc.events[i+j]
                start = pysrt.SubRipTime.from_ordinal(event.start.total_seconds() * 1000)
                end = pysrt.SubRipTime.from_ordinal(event.end.total_seconds() * 1000)
                subs.append(pysrt.SubRipItem(i+j+1, start, end, translation))
            
            progress = min(i+translator.batch_size, len(doc.events))
            self.subtitle_progress.emit(progress, len(doc.events))
            print(f"📝 Processed {progress}/{len(doc.events)} events")
        
        if not self.is_stopped:
            translator._save_cache()
            subs.save(output_file, encoding="utf-8")
    
    def translate_plain_txt(self, input_file, output_file, translator):
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
        
        translated = translator.translate(text)
        translator._save_cache()
        subs = pysrt.SubRipFile([pysrt.SubRipItem(1, 
            pysrt.SubRipTime(0,0,0,0), pysrt.SubRipTime(0,0,10,0), translated)])
        subs.save(output_file, encoding="utf-8")
    
    def is_srt_format(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [f.readline().strip() for _ in range(3)]
            return lines[0].isdigit() and '-->' in lines[1]
        except:
            return False

class SubtitleTranslatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Subtitle Translator Pro")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(DARK_STYLE)
        
        self.worker = None
        self.enabled_languages = {}
        self.settings = self.load_settings()
        
        self.setup_ui()
        self.setup_status_bar()
        self.setup_menu_bar()
        
        # Set window icon if available
        icon_path = Path("icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_tab = QWidget()
        self.settings_tab = QWidget()
        self.about_tab = QWidget()
        
        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        self.tab_widget.addTab(self.about_tab, "About")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.tab_widget)
        
        # Setup main tab
        self.setup_main_tab()
        
        # Setup settings tab
        self.setup_settings_tab()
        
        # Setup about tab
        self.setup_about_tab()
    
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add version info
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #888;")
        self.status_bar.addPermanentWidget(version_label)
    
    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        open_file_action = QAction("Open File", self)
        open_file_action.triggered.connect(self.select_single_file)
        file_menu.addAction(open_file_action)
        
        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.select_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        
        clear_cache_action = QAction("Clear Cache", self)
        clear_cache_action.triggered.connect(self.clear_cache)
        tools_menu.addAction(clear_cache_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        help_menu.addAction(about_action)
    
    def setup_main_tab(self):
        layout = QVBoxLayout(self.main_tab)
        
        # Header
        header = QLabel("🎬 Subtitle Translator Pro")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # File Selection
        file_group = QGroupBox("📁 File Selection")
        file_layout = QVBoxLayout(file_group)
        
        btn_layout = QHBoxLayout()
        self.btn_single = QPushButton("📄 Select Single File")
        self.btn_folder = QPushButton("📁 Select Folder")
        self.btn_single.clicked.connect(self.select_single_file)
        self.btn_folder.clicked.connect(self.select_folder)
        
        btn_layout.addWidget(self.btn_single)
        btn_layout.addWidget(self.btn_folder)
        file_layout.addLayout(btn_layout)
        
        self.file_label = QLabel("No files selected")
        self.file_label.setStyleSheet("color: #888; font-style: italic;")
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_group)
        
        # Language Selection
        lang_group = QGroupBox("🌐 Languages to Process")
        lang_layout = QVBoxLayout(lang_group)
        
        # Load enabled languages from settings or use defaults
        self.enabled_languages = self.load_enabled_languages()
        
        # Display selected languages as tags in a flow layout
        self.lang_flow_widget = QWidget()
        self.lang_flow_layout = FlowLayout(self.lang_flow_widget)
        
        # Add languages as tags
        if self.enabled_languages:
            for lang, code in self.enabled_languages.items():
                tag = QLabel(f" {lang} ({code}) ")
                tag.setStyleSheet(
                    "background-color: #0d7377; border-radius: 10px; padding: 5px 10px; margin: 3px;"
                )
                self.lang_flow_layout.addWidget(tag)
        else:
            no_langs = QLabel("No languages selected. Please go to Settings tab.")
            no_langs.setStyleSheet("color: #888; font-style: italic;")
            self.lang_flow_layout.addWidget(no_langs)
        
        lang_layout.addWidget(self.lang_flow_widget)
        
        # Add a note about changing languages
        note_label = QLabel("To add or remove languages, go to the Settings tab.")
        note_label.setStyleSheet("color: #888; font-style: italic;")
        lang_layout.addWidget(note_label)
        
        layout.addWidget(lang_group)
        
        # Progress Section
        progress_group = QGroupBox("📊 Translation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # File progress
        file_progress_layout = QHBoxLayout()
        file_progress_layout.addWidget(QLabel("Files:"))
        self.file_progress_bar = QProgressBar()
        file_progress_layout.addWidget(self.file_progress_bar)
        progress_layout.addLayout(file_progress_layout)
        
        # Language progress
        lang_progress_layout = QHBoxLayout()
        lang_progress_layout.addWidget(QLabel("Languages:"))
        self.lang_progress_bar = QProgressBar()
        lang_progress_layout.addWidget(self.lang_progress_bar)
        progress_layout.addLayout(lang_progress_layout)
        
        # Subtitle progress
        sub_progress_layout = QHBoxLayout()
        sub_progress_layout.addWidget(QLabel("Subtitles:"))
        self.sub_progress_bar = QProgressBar()
        sub_progress_layout.addWidget(self.sub_progress_bar)
        progress_layout.addLayout(sub_progress_layout)
        
        # Set all progress bars to 0
        self.file_progress_bar.setValue(0)
        self.lang_progress_bar.setValue(0)
        self.sub_progress_bar.setValue(0)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setPlaceholderText("Translation logs will appear here...")
        progress_layout.addWidget(self.log_text)
        
        layout.addWidget(progress_group)
        
        # Control Buttons
        control_layout = QHBoxLayout()
        self.btn_start = QPushButton("🚀 Start Translation")
        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_clear = QPushButton("🗑️ Clear Logs")
        self.btn_open_output = QPushButton("📂 Open Output Folder")
        
        self.btn_start.clicked.connect(self.start_translation)
        self.btn_stop.clicked.connect(self.stop_translation)
        self.btn_clear.clicked.connect(self.clear_logs)
        self.btn_open_output.clicked.connect(self.open_output_folder)
        
        self.btn_start.setStyleSheet("QPushButton { background-color: #0d7377; }")
        self.btn_stop.setStyleSheet("QPushButton { background-color: #d32f2f; }")
        self.btn_stop.setEnabled(False)
        self.btn_open_output.setEnabled(False)
        
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)
        control_layout.addWidget(self.btn_clear)
        control_layout.addWidget(self.btn_open_output)
        
        layout.addLayout(control_layout)
        
        self.files = []
        self.output_folder = None
    
    def setup_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)
        
        # Header
        header = QLabel("⚙️ Settings")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # Create a scroll area for all settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Language Settings
        lang_settings_group = QGroupBox("🌐 Language Settings")
        lang_settings_layout = QVBoxLayout(lang_settings_group)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to filter languages...")
        self.search_input.textChanged.connect(self.filter_languages)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        lang_settings_layout.addLayout(search_layout)
        
        # Language selection buttons
        lang_btn_layout = QHBoxLayout()
        self.settings_select_all = QPushButton("✅ Select All")
        self.settings_deselect_all = QPushButton("❌ Deselect All")
        self.settings_select_all.clicked.connect(self.settings_select_all_languages)
        self.settings_deselect_all.clicked.connect(self.settings_deselect_all_languages)
        lang_btn_layout.addWidget(self.settings_select_all)
        lang_btn_layout.addWidget(self.settings_deselect_all)
        lang_settings_layout.addLayout(lang_btn_layout)
        
        # Scroll area for languages
        lang_scroll = QScrollArea()
        lang_scroll.setWidgetResizable(True)
        lang_scroll_content = QWidget()
        self.settings_lang_layout = QVBoxLayout(lang_scroll_content)
        
        # Create checkboxes for all available languages
        self.settings_lang_checkboxes = {}
        
        # Sort languages alphabetically
        sorted_languages = sorted(LANGUAGES.items())
        
        for lang, code in sorted_languages:
            checkbox = QCheckBox(f"{lang} ({code})")
            # Check if this language is in enabled languages
            checkbox.setChecked(lang in self.enabled_languages)
            self.settings_lang_checkboxes[lang] = checkbox
            self.settings_lang_layout.addWidget(checkbox)
        
        lang_scroll_content.setLayout(self.settings_lang_layout)
        lang_scroll.setWidget(lang_scroll_content)
        lang_scroll.setMinimumHeight(300)
        lang_settings_layout.addWidget(lang_scroll)
        
        scroll_layout.addWidget(lang_settings_group)
        
        # Output Settings
        output_settings_group = QGroupBox("📂 Output Settings")
        output_settings_layout = QVBoxLayout(output_settings_group)
        
        # Organize by file
        self.organize_by_file = QCheckBox("Create separate folder for each file")
        self.organize_by_file.setChecked(self.settings.get('organize_by_file', True))
        output_settings_layout.addWidget(self.organize_by_file)
        
        # Move original file
        self.move_original = QCheckBox("Move original file to output folder")
        self.move_original.setChecked(self.settings.get('move_original', True))
        output_settings_layout.addWidget(self.move_original)
        
        # Overwrite existing files
        self.overwrite_existing = QCheckBox("Overwrite existing translations")
        self.overwrite_existing.setChecked(self.settings.get('overwrite_existing', False))
        output_settings_layout.addWidget(self.overwrite_existing)
        
        scroll_layout.addWidget(output_settings_group)
        
        # Translation Settings
        translation_settings_group = QGroupBox("🔄 Translation Settings")
        translation_settings_layout = QVBoxLayout(translation_settings_group)
        
        # Batch size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("Batch Size:"))
        self.batch_size = QSpinBox()
        self.batch_size.setMinimum(1)
        self.batch_size.setMaximum(100)
        self.batch_size.setValue(self.settings.get('batch_size', 50))
        batch_layout.addWidget(self.batch_size)
        translation_settings_layout.addLayout(batch_layout)
        
        # Retry count
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel("Retry Count:"))
        self.retry_count = QSpinBox()
        self.retry_count.setMinimum(1)
        self.retry_count.setMaximum(10)
        self.retry_count.setValue(self.settings.get('retry_count', 3))
        retry_layout.addWidget(self.retry_count)
        translation_settings_layout.addLayout(retry_layout)
        
        scroll_layout.addWidget(translation_settings_group)
        
        # Cache Settings
        cache_settings_group = QGroupBox("💾 Cache Settings")
        cache_settings_layout = QVBoxLayout(cache_settings_group)
        
        # Enable cache
        self.enable_cache = QCheckBox("Enable translation cache")
        self.enable_cache.setChecked(self.settings.get('enable_cache', True))
        cache_settings_layout.addWidget(self.enable_cache)
        
        # Clear cache button
        self.clear_cache_btn = QPushButton("🗑️ Clear Cache")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cache_settings_layout.addWidget(self.clear_cache_btn)
        
        # Cache info
        self.cache_info = QLabel("Cache size: Calculating...")
        cache_settings_layout.addWidget(self.cache_info)
        QTimer.singleShot(500, self.update_cache_info)
        
        scroll_layout.addWidget(cache_settings_group)
        
        # Save button
        self.save_settings_btn = QPushButton("💾 Save Settings")
        self.save_settings_btn.clicked.connect(self.save_all_settings)
        self.save_settings_btn.setStyleSheet("QPushButton { background-color: #0d7377; }")
        scroll_layout.addWidget(self.save_settings_btn)
        
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
    
    def setup_about_tab(self):
        layout = QVBoxLayout(self.about_tab)
        
        # Header
        header = QLabel("🎬 Subtitle Translator Pro")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # Version
        version = QLabel("Version 1.0.0")
        version.setAlignment(QtCore.Qt.AlignCenter)
        version.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(version)
        
        # Description
        description = QLabel(
            "Subtitle Translator Pro is a powerful tool for translating subtitle files "
            "into multiple languages using Google Translate. It supports SRT, ASS, and "
            "plain text files, and can batch process entire folders at once."
        )
        description.setWordWrap(True)
        description.setAlignment(QtCore.Qt.AlignCenter)
        description.setStyleSheet("margin: 10px;")
        layout.addWidget(description)
        
        # Features
        features_group = QGroupBox("✨ Features")
        features_layout = QVBoxLayout(features_group)
        
        features = [
            "🌍 Translate subtitles to multiple languages at once",
            "🗂️ Batch process entire folders of subtitle files",
            "🔄 Convert between subtitle formats (ASS to SRT)",
            "💾 Translation caching for improved performance",
            "⚙️ Customizable settings for output organization",
            "🎨 Modern, user-friendly dark interface"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("padding: 5px;")
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_group)
        
        # Credits
        credits_group = QGroupBox("👏 Credits")
        credits_layout = QVBoxLayout(credits_group)
        
        credits = [
            "Google Translate API via deep-translator",
            "PyQt5 for the user interface",
            "pysrt for SRT file handling",
            "ass for ASS subtitle parsing"
        ]
        
        for credit in credits:
            credit_label = QLabel(credit)
            credit_label.setStyleSheet("padding: 5px;")
            credits_layout.addWidget(credit_label)
        
        layout.addWidget(credits_group)
        
        # Add spacer at the bottom
        layout.addStretch()
    
    def select_single_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Subtitle File", "", 
            "Subtitle Files (*.srt *.ass *.txt)")
        if file_path:
            self.files = [file_path]
            self.file_label.setText(f"Selected: {Path(file_path).name}")
            self.file_label.setStyleSheet("color: #14a085;")
            self.output_folder = Path(file_path).parent
            self.btn_open_output.setEnabled(True)
            self.status_bar.showMessage(f"Selected file: {Path(file_path).name}")
    
    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            folder = Path(folder_path)
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)
            
            files = [str(f) for f in folder.iterdir() 
                    if f.suffix.lower() in SUPPORTED_FORMATS]
            if files:
                self.files = files
                self.file_label.setText(f"Selected: {len(files)} files from {folder.name}")
                self.file_label.setStyleSheet("color: #14a085;")
                self.output_folder = folder
                self.btn_open_output.setEnabled(True)
                self.status_bar.showMessage(f"Selected {len(files)} files from {folder.name}")
            else:
                QMessageBox.warning(self, "No Files", "No subtitle files found in the selected folder.")
    
    # These methods are no longer needed as we process all languages
    # Kept as empty methods in case they're called elsewhere
    def select_all_languages(self):
        pass
    
    def deselect_all_languages(self):
        pass
    
    def get_selected_languages(self):
        # Return all enabled languages since we process all of them
        return self.enabled_languages
    
    def load_settings(self):
        # Try to load from settings.json file, or use defaults
        settings_file = Path('settings.json')
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Default settings
        return {
            'organize_by_file': True,
            'move_original': True,
            'overwrite_existing': False,
            'batch_size': 50,
            'retry_count': 3,
            'enable_cache': True
        }
    
    def load_enabled_languages(self):
        # Try to load from settings.json file, or use defaults
        settings_file = Path('settings.json')
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('languages', DEFAULT_LANGUAGES)
            except Exception as e:
                print(f"Error loading language settings: {e}")
        return DEFAULT_LANGUAGES
    
    def save_all_settings(self):
        # Get selected languages from settings tab
        selected_languages = {lang: LANGUAGES[lang] for lang, checkbox in self.settings_lang_checkboxes.items() 
                            if checkbox.isChecked()}
        
        if not selected_languages:
            QMessageBox.warning(self, "No Languages", "Please select at least one language.")
            return
        
        # Get other settings
        settings = {
            'languages': selected_languages,
            'organize_by_file': self.organize_by_file.isChecked(),
            'move_original': self.move_original.isChecked(),
            'overwrite_existing': self.overwrite_existing.isChecked(),
            'batch_size': self.batch_size.value(),
            'retry_count': self.retry_count.value(),
            'enable_cache': self.enable_cache.isChecked()
        }
        
        # Save to file
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
                
            self.enabled_languages = selected_languages
            self.settings = settings
            
            # Update main tab language list
            self.update_main_tab_languages()
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.status_bar.showMessage("Settings saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
    
    def update_main_tab_languages(self):
        # Clear existing tags
        while self.lang_flow_layout.count():
            item = self.lang_flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new language tags
        if self.enabled_languages:
            for lang, code in self.enabled_languages.items():
                tag = QLabel(f" {lang} ({code}) ")
                tag.setStyleSheet(
                    "background-color: #0d7377; border-radius: 10px; padding: 5px 10px; margin: 3px;"
                )
                self.lang_flow_layout.addWidget(tag)
        else:
            no_langs = QLabel("No languages selected. Please go to Settings tab.")
            no_langs.setStyleSheet("color: #888; font-style: italic;")
            self.lang_flow_layout.addWidget(no_langs)
    
    def filter_languages(self):
        search_text = self.search_input.text().lower()
        
        for lang, checkbox in self.settings_lang_checkboxes.items():
            if search_text in lang.lower() or search_text in LANGUAGES[lang].lower():
                checkbox.setVisible(True)
            else:
                checkbox.setVisible(False)
    
    def settings_select_all_languages(self):
        for checkbox in self.settings_lang_checkboxes.values():
            if checkbox.isVisible():  # Only select visible (filtered) checkboxes
                checkbox.setChecked(True)
    
    def settings_deselect_all_languages(self):
        for checkbox in self.settings_lang_checkboxes.values():
            if checkbox.isVisible():  # Only deselect visible (filtered) checkboxes
                checkbox.setChecked(False)
    
    def update_cache_info(self):
        cache_size = 0
        cache_count = 0
        
        for cache_file in Path('./cache/').glob('cache_*.json'):
            try:
                cache_size += cache_file.stat().st_size
                cache_count += 1
            except:
                pass
        
        if cache_size > 1024 * 1024:
            size_str = f"{cache_size / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{cache_size / 1024:.2f} KB"
        
        self.cache_info.setText(f"Cache size: {size_str} ({cache_count} files)")
    
    def clear_cache(self):
        try:
            count = 0
            for cache_file in Path('./cache/').glob('cache_*.json'):
                cache_file.unlink()
                count += 1
            
            self.update_cache_info()
            QMessageBox.information(self, "Cache Cleared", f"Successfully cleared {count} cache files.")
            self.status_bar.showMessage(f"Cleared {count} cache files")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear cache: {e}")
    
    def open_output_folder(self):
        if not self.output_folder:
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(self.output_folder)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{self.output_folder}"')
            else:  # Linux
                os.system(f'xdg-open "{self.output_folder}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open folder: {e}")
    
    def start_translation(self):
        if not self.files:
            QMessageBox.warning(self, "No Files", "Please select files to translate.")
            return
        
        selected_langs = self.get_selected_languages()
        if not selected_langs:
            QMessageBox.warning(self, "No Languages", "Please select at least one language.")
            return
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.file_progress_bar.setValue(0)
        self.lang_progress_bar.setValue(0)
        self.sub_progress_bar.setValue(0)
        self.log_text.clear()
        
        # Get current settings
        current_settings = {
            'organize_by_file': self.settings.get('organize_by_file', True),
            'move_original': self.settings.get('move_original', True),
            'overwrite_existing': self.settings.get('overwrite_existing', False),
            'batch_size': self.settings.get('batch_size', 50),
            'retry_count': self.settings.get('retry_count', 3),
            'enable_cache': self.settings.get('enable_cache', True)
        }
        
        self.worker = TranslationWorker(self.files, selected_langs, current_settings)
        self.worker.progress.connect(self.update_progress)
        self.worker.file_progress.connect(self.update_file_progress)
        self.worker.language_progress.connect(self.update_language_progress)
        self.worker.subtitle_progress.connect(self.update_subtitle_progress)
        self.worker.finished.connect(self.translation_finished)
        self.worker.stopped.connect(self.translation_stopped)
        self.worker.error.connect(self.translation_error)
        self.worker.start()
        
        self.status_bar.showMessage("Translation in progress...")
    
    def stop_translation(self):
        if self.worker:
            self.worker.stop()
            self.worker.terminate()
            self.worker.wait()
        self.translation_stopped()
    
    def update_progress(self, message):
        self.log_text.append(message)
        QtCore.QCoreApplication.processEvents()
    
    def update_file_progress(self, current, total):
        self.file_progress_bar.setMaximum(total)
        self.file_progress_bar.setValue(current)
    
    def update_language_progress(self, current, total):
        self.lang_progress_bar.setMaximum(total)
        self.lang_progress_bar.setValue(current)
    
    def update_subtitle_progress(self, current, total):
        self.sub_progress_bar.setMaximum(total)
        self.sub_progress_bar.setValue(current)
    
    def translation_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log_text.append("\n🎉 Translation completed successfully!")
        QMessageBox.information(self, "Success", "Translation completed successfully!")
        self.status_bar.showMessage("Translation completed successfully")
    
    def translation_stopped(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log_text.append("\n⏹️ Translation stopped by user.")
        QMessageBox.warning(self, "Stopped", "Translation was stopped by user.")
        self.status_bar.showMessage("Translation stopped by user")
    
    def translation_error(self, error):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log_text.append(f"\n❌ Error: {error}")
        QMessageBox.critical(self, "Error", f"An error occurred: {error}")
        self.status_bar.showMessage(f"Error: {error}")
    
    def clear_logs(self):
        self.log_text.clear()
    
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        # Cleanup cache files if they're too large
        for cache_file in Path('./cache/').glob('cache_*.json'):
            if cache_file.stat().st_size > 10*1024*1024:
                cache_file.unlink()
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SubtitleTranslatorGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()