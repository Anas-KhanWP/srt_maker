import os
import sys
import time
import hashlib
import json
import shutil
import re
import sqlite3
import requests
import tempfile
from pathlib import Path
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QSize, QRect, QPoint, QFileSystemWatcher, QTranslator, QLocale, QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap, QIcon, QKeySequence

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

try:
    import torch
    GPU_AVAILABLE = torch.cuda.is_available()
    print(f"TORCH: PyTorch is available. GPU support: {GPU_AVAILABLE}")
except ImportError:
    print("TORCH IMPORT ERROR: PyTorch is not installed or not available.")
    GPU_AVAILABLE = False

try:
    from transformers import MarianMTModel, MarianTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
    print("TRANSFORMERS: Available for offline translation")
except ImportError:
    print("TRANSFORMERS IMPORT ERROR: transformers library not available")
    TRANSFORMERS_AVAILABLE = False

# Comprehensive UI texts for translation
UI_TEXTS = {
    'app_title': 'Subtitle Translator Pro',
    'main_tab': 'Main',
    'settings_tab': 'Settings',
    'about_tab': 'About',
    'preview_tab': 'Preview',
    'watch_tab': 'Watch Folder',
    'stats_tab': 'Statistics',
    'file_selection': 'File Selection',
    'select_single_file': 'Select Single File',
    'select_folder': 'Select Folder',
    'start_translation': 'Start Translation',
    'stop': 'Stop',
    'clear_logs': 'Clear Logs',
    'open_output_folder': 'Open Output Folder',
    'language_settings': 'Language Settings',
    'output_settings': 'Output Settings',
    'translation_settings': 'Translation Settings',
    'cache_settings': 'Cache Settings',
    'ui_settings': 'UI Settings',
    'output_naming': 'Output Naming',
    'interface_language': 'Interface Language',
    'template': 'Template',
    'encoding': 'Encoding',
    'save_settings': 'Save Settings',
    'languages_to_process': 'Languages to Process',
    'translation_progress': 'Translation Progress',
    'files': 'Files',
    'languages': 'Languages',
    'subtitles': 'Subtitles',
    'folder_monitor': 'Folder Monitor',
    'monitored_folders': 'Monitored Folders',
    'controls': 'Controls',
    'activity_log': 'Activity Log',
    'add': 'Add',
    'remove': 'Remove',
    'start_monitoring': 'Start Monitoring',
    'stop_monitoring': 'Stop Monitoring',
    'auto_translate_detected': 'Auto-translate detected files',
    'clear': 'Clear',
    'file_preview': 'File Preview',
    'file': 'File',
    'translation_statistics': 'Translation Statistics',
    'current_session': 'Current Session',
    'reset_statistics': 'Reset Statistics',
    'version': 'Version',
    'features': 'Features',
    'credits': 'Credits',
    'keyboard_shortcuts': 'Keyboard Shortcuts',
    'batch_size': 'Batch Size',
    'retry_count': 'Retry Count',
    'enable_cache': 'Enable translation cache',
    'clear_cache': 'Clear Cache',
    'cache_size': 'Cache size',
    'create_folder_each_file': 'Create separate folder for each file',
    'move_original_folder': 'Move original file to output folder',
    'overwrite_existing': 'Overwrite existing translations',
    'no_files_selected': 'No files selected',
    'no_languages_selected': 'No languages selected. Please go to Settings tab.',
    'change_languages_settings': 'To add or remove languages, go to the Settings tab.',
    'search': 'Search',
    'filter_languages': 'Type to filter languages...',
    'select_all': 'Select All',
    'deselect_all': 'Deselect All',
    'profile': 'Profile',
    'select_profile': '-- Select Profile --',
    'queue': 'Queue',
    'status': 'Status',
    'stopped': 'Stopped',
    'monitoring': 'Monitoring'
}

# Cache for translated UI texts
TRANSLATED_CACHE = {}





# Performance Dashboard
class PerformanceDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh Dashboard')
        refresh_btn.clicked.connect(self.update_charts)
        layout.addWidget(refresh_btn)
        
        self.update_charts()
    
    def update_charts(self):
        self.figure.clear()
        
        # Create subplots
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 2, 3)
        ax4 = self.figure.add_subplot(2, 2, 4)
        
        # Sample data - replace with actual stats
        languages = ['Spanish', 'French', 'German', 'Chinese', 'Arabic']
        counts = [45, 32, 28, 22, 18]
        
        # Language usage chart
        ax1.bar(languages, counts)
        ax1.set_title('Most Translated Languages')
        ax1.tick_params(axis='x', rotation=45)
        
        # Translation speed over time
        days = list(range(1, 8))
        speeds = [120, 135, 142, 138, 155, 148, 162]
        ax2.plot(days, speeds, marker='o')
        ax2.set_title('Translation Speed (subtitles/min)')
        ax2.set_xlabel('Days')
        
        # Cache hit ratio
        cache_data = ['Cache Hits', 'Cache Misses']
        cache_values = [75, 25]
        ax3.pie(cache_values, labels=cache_data, autopct='%1.1f%%')
        ax3.set_title('Cache Performance')
        
        # File types processed
        file_types = ['SRT', 'ASS', 'TXT']
        file_counts = [65, 25, 10]
        ax4.bar(file_types, file_counts)
        ax4.set_title('File Types Processed')
        
        self.figure.tight_layout()
        self.canvas.draw()

class UITranslationWorker(QThread):
    progress = pyqtSignal(str, int, int)  # language, current, total
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.should_stop = False
    
    def run(self):
        languages = list(LANGUAGES.values())
        total_langs = len(languages)
        
        for i, lang_code in enumerate(languages):
            if self.should_stop:
                break
                
            if lang_code == 'en':  # Skip English
                continue
                
            self.progress.emit(lang_code, i + 1, total_langs)
            
            # Check if translations already exist for this language
            missing_translations = []
            for key in UI_TEXTS.keys():
                cache_key = f"{lang_code}_{key}"
                if cache_key not in TRANSLATED_CACHE:
                    missing_translations.append(key)
            
            if missing_translations:
                try:
                    translator = GoogleTranslator(source='en', target=lang_code)
                    
                    # Translate in batches
                    for j in range(0, len(missing_translations), 10):
                        if self.should_stop:
                            break
                            
                        batch = missing_translations[j:j+10]
                        texts_to_translate = [UI_TEXTS[key] for key in batch]
                        
                        # Batch translate
                        batch_text = "\n\n\n".join(texts_to_translate)
                        translated_batch = translator.translate(batch_text)
                        translations = translated_batch.split("\n\n\n")
                        
                        # Store in cache
                        for k, key in enumerate(batch):
                            if k < len(translations):
                                cache_key = f"{lang_code}_{key}"
                                TRANSLATED_CACHE[cache_key] = translations[k].strip()
                        
                        time.sleep(0.1)  # Small delay to avoid rate limiting
                        
                except Exception as e:
                    print(f"Error translating to {lang_code}: {e}")
                    continue
        
        self.finished.emit()
    
    def stop(self):
        self.should_stop = True

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

class TranslationStats:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.files_processed = 0
        self.languages_processed = 0
        self.subtitles_translated = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.start_time = None
        self.end_time = None
        self.errors = 0
    
    def start_session(self):
        self.start_time = datetime.now()
    
    def end_session(self):
        self.end_time = datetime.now()
    
    def get_duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    def get_cache_ratio(self):
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0

class FolderWatcher(QThread):
    file_detected = pyqtSignal(str)
    
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.watcher = QFileSystemWatcher()
        self.watcher.directoryChanged.connect(self.check_folder)
        self.processed_files = set()
    
    def start_watching(self):
        self.watcher.addPath(self.folder_path)
        self.check_folder()
    
    def stop_watching(self):
        self.watcher.removePaths(self.watcher.directories())
    
    def check_folder(self):
        folder = Path(self.folder_path)
        if folder.exists():
            for file in folder.iterdir():
                if file.suffix.lower() in SUPPORTED_FORMATS and str(file) not in self.processed_files:
                    self.processed_files.add(str(file))
                    self.file_detected.emit(str(file))

import pysrt
import ass
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES



# Offline Translation Models
class OfflineTranslator:
    def __init__(self, model_name='marian'):
        self.model_name = model_name
        self.models = {}
        self.tokenizers = {}
        
    def get_model_key(self, source_lang, target_lang):
        if source_lang == 'auto':
            source_lang = 'en'
        return f"{source_lang}-{target_lang}"
    
    def load_model(self, source_lang, target_lang):
        if not TRANSFORMERS_AVAILABLE:
            raise Exception("Transformers library not available")
            
        model_key = self.get_model_key(source_lang, target_lang)
        
        if model_key in self.models:
            return self.models[model_key], self.tokenizers[model_key]
        
        try:
            if self.model_name == 'marian':
                model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
            else:
                model = pipeline("translation", model=f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}")
                tokenizer = None
                
            self.models[model_key] = model
            self.tokenizers[model_key] = tokenizer
            return model, tokenizer
            
        except Exception as e:
            raise Exception(f"Model not available for {source_lang}->{target_lang}: {e}")
    
    def translate(self, text, target_lang, source_lang='en'):
        try:
            model, tokenizer = self.load_model(source_lang, target_lang)
            
            if tokenizer:
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
                translated = model.generate(**inputs)
                result = tokenizer.decode(translated[0], skip_special_tokens=True)
            else:
                result = model(text)[0]['translation_text']
                
            return result
        except Exception as e:
            return f"[Translation Error: {e}]"

# Translation Services
class TranslationService:
    def __init__(self, name, translator_class, is_offline=False):
        self.name = name
        self.translator_class = translator_class
        self.is_offline = is_offline
    
    def translate(self, text, target_lang, source_lang='auto'):
        if self.is_offline:
            translator = self.translator_class()
            return translator.translate(text, target_lang, source_lang)
        else:
            translator = self.translator_class(source=source_lang, target=target_lang)
            return translator.translate(text)

TRANSLATION_SERVICES = {
    'google': TranslationService('Google Translate (Recommended)', GoogleTranslator, False),
    'marian': TranslationService('Marian MT (Offline)', OfflineTranslator, True) if TRANSFORMERS_AVAILABLE else None,
    'opus': TranslationService('Opus-MT (Offline)', lambda: OfflineTranslator('opus'), True) if TRANSFORMERS_AVAILABLE else None
}

# Remove None services
TRANSLATION_SERVICES = {k: v for k, v in TRANSLATION_SERVICES.items() if v is not None}

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
    def __init__(self, dest_lang, stats=None, service='google'):
        self.dest_lang = dest_lang
        self.service = service
        self.cache = self._load_cache()
        self.batch_size = 50
        self.stats = stats
        
        # Initialize translator based on service
        if service in TRANSLATION_SERVICES:
            service_obj = TRANSLATION_SERVICES[service]
            if service_obj.is_offline:
                self.translator = service_obj.translator_class()
                self.is_offline = True
            else:
                self.translator = GoogleTranslator(source='auto', target=dest_lang)
                self.is_offline = False
        else:
            self.translator = GoogleTranslator(source='auto', target=dest_lang)
            self.is_offline = False
    
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
                if self.stats:
                    self.stats.cache_hits += 1
                results[i] = self.cache[cache_key]
                if i % 20 == 0 or i < 3:  # Show first few and occasional others
                    print(f"💾 [{i:4d}] Cache hit: \"{clean_text[:30]}{'...' if len(clean_text) > 30 else ''}\"")
            else:
                if self.stats:
                    self.stats.cache_misses += 1
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
                
                if self.is_offline:
                    result = self.translator.translate(text, self.dest_lang, 'en')
                else:
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
    
    def __init__(self, files, languages, settings, stats=None):
        super().__init__()
        self.files = files
        self.languages = languages
        self.settings = settings
        self.stats = stats
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
        
        service = self.settings.get('translation_service', 'google')
        translators = {lang_code: SubtitleTranslator(lang_code, self.stats, service) 
                      for lang_code in self.languages.values()}
        
        if self.stats:
            self.stats.files_processed += 1
        
        for i, (language, lang_code) in enumerate(self.languages.items()):
            if self.is_stopped:
                return
            
            self.language_progress.emit(i + 1, len(self.languages))
            
            # Generate custom filename
            naming_template = self.settings.get('output_naming', '{filename}_{language}')
            filename = naming_template.format(
                filename=path.stem,
                language=language,
                date=datetime.now().strftime('%Y%m%d'),
                time=datetime.now().strftime('%H%M%S')
            )
            
            if self.settings.get('organize_by_file', True):
                output_file = output_folder / f"{filename}.srt"
            else:
                output_file = output_folder / f"{filename}.srt"
            
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
                    if self.stats:
                        self.stats.languages_processed += 1
                    self.progress.emit(f"✅ {language} completed!")
                
            except Exception as e:
                if not self.is_stopped:
                    if self.stats:
                        self.stats.errors += 1
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
                if self.stats:
                    self.stats.subtitles_translated += 1
            
            progress = min(i+translator.batch_size, len(subs))
            self.subtitle_progress.emit(progress, len(subs))
            print(f"📝 Processed {progress}/{len(subs)} subtitles")
        
        if not self.is_stopped:
            translator._save_cache()
            encoding = self.settings.get('output_encoding', 'utf-8')
            subs.save(output_file, encoding=encoding)
    
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
            encoding = self.settings.get('output_encoding', 'utf-8')
            subs.save(output_file, encoding=encoding)
    
    def translate_plain_txt(self, input_file, output_file, translator):
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
        
        translated = translator.translate(text)
        translator._save_cache()
        subs = pysrt.SubRipFile([pysrt.SubRipItem(1, 
            pysrt.SubRipTime(0,0,0,0), pysrt.SubRipTime(0,0,10,0), translated)])
        encoding = self.settings.get('output_encoding', 'utf-8')
        subs.save(output_file, encoding=encoding)
    
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
        self.setAcceptDrops(True)
        
        self.worker = None
        self.enabled_languages = {}
        self.settings = self.load_settings()
        self.stats = TranslationStats()
        self.folder_watchers = []
        self.watch_folders = self.settings.get('watchlist', [])
        self.watch_queue = []
        self.recent_files = self.settings.get('recent_files', [])
        self.profiles = self.settings.get('profiles', {})
        self.ui_language = self.settings.get('ui_language', 'en')
        

        
        # Start background UI translation worker
        self.ui_translator = UITranslationWorker()
        self.ui_translator.progress.connect(self.on_translation_progress)
        self.ui_translator.finished.connect(self.on_translation_finished)
        self.ui_translator.start()
        
        self.setup_ui()
        self.setup_status_bar()
        self.setup_menu_bar()
        self.setup_shortcuts()
        
        # Set window icon if available
        icon_path = Path("icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Restore layout state
        if self.settings.get('layout_state'):
            self.restoreGeometry(QtCore.QByteArray.fromHex(self.settings['layout_state'].encode()))
    
    def tr(self, key):
        if self.ui_language == 'en':
            return UI_TEXTS.get(key, key)
        
        # Check cache first
        cache_key = f"{self.ui_language}_{key}"
        if cache_key in TRANSLATED_CACHE:
            return TRANSLATED_CACHE[cache_key]
        
        # Translate using Google Translate
        try:
            translator = GoogleTranslator(source='en', target=self.ui_language)
            translated = translator.translate(UI_TEXTS.get(key, key))
            TRANSLATED_CACHE[cache_key] = translated
            return translated
        except:
            return UI_TEXTS.get(key, key)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).is_file() and Path(file_path).suffix.lower() in SUPPORTED_FORMATS:
                files.append(file_path)
            elif Path(file_path).is_dir():
                folder_files = [str(f) for f in Path(file_path).iterdir() if f.suffix.lower() in SUPPORTED_FORMATS]
                files.extend(folder_files)
        
        if files:
            self.files = files
            self.file_label.setText(f"Dropped: {len(files)} file(s)")
            self.file_label.setStyleSheet("color: #14a085;")
            self.output_folder = Path(files[0]).parent
            self.btn_open_output.setEnabled(True)
            self.add_to_recent_files(files)
    
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.select_single_file)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self).activated.connect(self.select_folder)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.start_translation)
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.start_translation)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.stop_translation)
        
        # Tab navigation shortcuts
        QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(lambda: self.tab_widget.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(lambda: self.tab_widget.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(lambda: self.tab_widget.setCurrentIndex(2))
        QShortcut(QKeySequence("Ctrl+4"), self).activated.connect(lambda: self.tab_widget.setCurrentIndex(3))
        QShortcut(QKeySequence("Ctrl+5"), self).activated.connect(lambda: self.tab_widget.setCurrentIndex(4))
        QShortcut(QKeySequence("Ctrl+6"), self).activated.connect(lambda: self.tab_widget.setCurrentIndex(5))
        
        # Accessibility shortcuts
        QShortcut(QKeySequence("Alt+F"), self).activated.connect(self.focus_file_selection)
        QShortcut(QKeySequence("Alt+L"), self).activated.connect(self.focus_language_selection)
        QShortcut(QKeySequence("Alt+P"), self).activated.connect(self.focus_progress_log)
    
    def save_recent_files(self):
        self.settings['recent_files'] = self.recent_files[-10:]
        self.save_settings()
    
    def add_to_recent_files(self, files):
        for file in files:
            if file in self.recent_files:
                self.recent_files.remove(file)
            self.recent_files.append(file)
        self.save_recent_files()
        self.update_recent_menu()
    
    def load_profiles(self):
        try:
            with open('profiles.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_watchlist(self):
        self.settings['watchlist'] = self.watch_folders
        self.save_settings()
    
    def save_settings(self):
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def save_profiles(self):
        self.settings['profiles'] = self.profiles
        self.save_settings()
    
    def create_profile(self):
        name, ok = QInputDialog.getText(self, 'Create Profile', 'Profile name:')
        if ok and name:
            self.profiles[name] = dict(self.enabled_languages)
            self.save_profiles()
            self.update_profile_menu()
            self.update_profile_combo()
    
    def load_profile(self, name):
        if name in self.profiles:
            self.enabled_languages = self.profiles[name]
            self.update_main_tab_languages()
            self.status_bar.showMessage(f"Loaded profile: {name}")
    
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
        
        # Add new tabs
        self.preview_tab = QWidget()
        self.watch_tab = QWidget()
        self.stats_tab = QWidget()
        self.compare_tab = QWidget()
        self.find_replace_tab = QWidget()
        self.dashboard_tab = QWidget()
        
        self.tab_widget.addTab(self.preview_tab, "Preview")
        self.tab_widget.addTab(self.watch_tab, "Watch Folder")
        self.tab_widget.addTab(self.stats_tab, "Statistics")
        self.tab_widget.addTab(self.compare_tab, "Compare")
        self.tab_widget.addTab(self.find_replace_tab, "Find & Replace")
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.tab_widget)
        
        # Setup main tab
        self.setup_main_tab()
        
        # Setup settings tab
        self.setup_settings_tab()
        
        # Setup about tab
        self.setup_about_tab()
        
        # Setup new tabs
        self.setup_preview_tab()
        self.setup_watch_tab()
        self.setup_stats_tab()
        self.setup_compare_tab()
        self.setup_find_replace_tab()
        self.setup_dashboard_tab()
        
        # Auto-start watching if folders exist
        QTimer.singleShot(500, self.auto_start_watching)
        
        # Apply initial UI translations
        QTimer.singleShot(100, self.refresh_ui_texts)
    
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
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Profiles menu
        profiles_menu = menu_bar.addMenu("Profiles")
        
        create_profile_action = QAction("Create Profile", self)
        create_profile_action.triggered.connect(self.create_profile)
        profiles_menu.addAction(create_profile_action)
        
        profiles_menu.addSeparator()
        self.profile_menu = profiles_menu
        self.update_profile_menu()
        
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
        
        # Profile selector
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self.load_profile_from_combo)
        profile_layout.addWidget(self.profile_combo)
        self.update_profile_combo()
        lang_settings_layout.addLayout(profile_layout)
        
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
        
        # Advanced Translation Settings
        advanced_translation_group = QGroupBox("🚀 Advanced Translation")
        advanced_translation_layout = QVBoxLayout(advanced_translation_group)
        
        # Translation service selection
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("Translation Model:"))
        self.translation_service = QComboBox()
        
        # Add available translation services
        for key, service in TRANSLATION_SERVICES.items():
            self.translation_service.addItem(service.name, key)
        
        # Set current service
        current_service = self.settings.get('translation_service', 'google')
        for i in range(self.translation_service.count()):
            if self.translation_service.itemData(i) == current_service:
                self.translation_service.setCurrentIndex(i)
                break
        
        service_layout.addWidget(self.translation_service)
        advanced_translation_layout.addLayout(service_layout)
        
        # GPU acceleration
        self.use_gpu = QCheckBox("Use GPU Acceleration (if available)")
        self.use_gpu.setChecked(self.settings.get('use_gpu', False))
        self.use_gpu.setEnabled(GPU_AVAILABLE)
        advanced_translation_layout.addWidget(self.use_gpu)
        
        # Offline mode
        self.offline_mode = QCheckBox("Offline Mode (no internet required)")
        self.offline_mode.setChecked(self.settings.get('offline_mode', False))
        advanced_translation_layout.addWidget(self.offline_mode)
        
        scroll_layout.addWidget(advanced_translation_group)
        
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
        
        # UI Settings
        ui_settings_group = QGroupBox("🌍 UI Settings")
        ui_settings_layout = QVBoxLayout(ui_settings_group)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Interface Language:"))
        self.ui_language_combo = QComboBox()
        
        # Add all available languages
        for lang_name, lang_code in sorted(LANGUAGES.items()):
            self.ui_language_combo.addItem(f"{lang_name} ({lang_code})", lang_code)
        
        # Set current language
        for i in range(self.ui_language_combo.count()):
            if self.ui_language_combo.itemData(i) == self.ui_language:
                self.ui_language_combo.setCurrentIndex(i)
                break
        
        self.ui_language_combo.currentTextChanged.connect(self.on_ui_language_changed)
        lang_layout.addWidget(self.ui_language_combo)
        ui_settings_layout.addLayout(lang_layout)
        
        scroll_layout.addWidget(ui_settings_group)
        
        # Output Settings Enhancement
        output_naming_group = QGroupBox("📝 Output Naming")
        output_naming_layout = QVBoxLayout(output_naming_group)
        
        # Custom naming template
        naming_layout = QHBoxLayout()
        naming_layout.addWidget(QLabel("Template:"))
        self.output_naming = QLineEdit()
        self.output_naming.setText(self.settings.get('output_naming', '{filename}_{language}'))
        self.output_naming.setPlaceholderText("{filename}_{language}_{date}")
        naming_layout.addWidget(self.output_naming)
        output_naming_layout.addLayout(naming_layout)
        
        # Encoding selection
        encoding_layout = QHBoxLayout()
        encoding_layout.addWidget(QLabel("Encoding:"))
        self.output_encoding = QComboBox()
        self.output_encoding.addItems(["utf-8", "utf-16", "ascii", "latin-1"])
        self.output_encoding.setCurrentText(self.settings.get('output_encoding', 'utf-8'))
        encoding_layout.addWidget(self.output_encoding)
        output_naming_layout.addLayout(encoding_layout)
        
        scroll_layout.addWidget(output_naming_group)
        
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
        
        # Keyboard Shortcuts
        shortcuts_group = QGroupBox("⌨️ Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout(shortcuts_group)
        
        shortcuts = [
            "Ctrl+O - Open single file",
            "Ctrl+Shift+O - Open folder",
            "Ctrl+S / F5 - Start translation",
            "Escape - Stop translation",
            "Ctrl+Q - Quit application"
        ]
        
        for shortcut in shortcuts:
            shortcut_label = QLabel(shortcut)
            shortcut_label.setStyleSheet("padding: 5px; font-family: monospace;")
            shortcuts_layout.addWidget(shortcut_label)
        
        layout.addWidget(shortcuts_group)
        
        # Add spacer at the bottom
        layout.addStretch()
    
    def setup_preview_tab(self):
        layout = QVBoxLayout(self.preview_tab)
        
        header = QLabel("📄 File Preview")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # File selector for preview
        file_layout = QHBoxLayout()
        self.preview_file_combo = QComboBox()
        self.preview_file_combo.currentTextChanged.connect(self.update_preview)
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(self.preview_file_combo)
        layout.addLayout(file_layout)
        
        # Preview text area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
    
    def setup_watch_tab(self):
        layout = QVBoxLayout(self.watch_tab)
        
        header = QLabel("🔍 Folder Monitor")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # Main content in horizontal layout
        main_layout = QHBoxLayout()
        
        # Left panel - Folder management
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Folders section
        folders_group = QGroupBox("📁 Monitored Folders")
        folders_layout = QVBoxLayout(folders_group)
        
        # Folder list with custom styling
        self.watch_folders_list = QListWidget()
        self.watch_folders_list.setStyleSheet("""
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
                background-color: #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
            }
        """)
        folders_layout.addWidget(self.watch_folders_list)
        
        # Folder controls with icons
        folder_controls = QHBoxLayout()
        self.add_folder_btn = QPushButton("➕ Add")
        self.remove_folder_btn = QPushButton("➖ Remove")
        self.add_folder_btn.clicked.connect(self.add_watch_folder)
        self.remove_folder_btn.clicked.connect(self.remove_watch_folder)
        self.add_folder_btn.setStyleSheet("QPushButton { background-color: #0d7377; }")
        self.remove_folder_btn.setStyleSheet("QPushButton { background-color: #d32f2f; }")
        folder_controls.addWidget(self.add_folder_btn)
        folder_controls.addWidget(self.remove_folder_btn)
        folders_layout.addLayout(folder_controls)
        
        left_layout.addWidget(folders_group)
        
        # Control panel
        control_group = QGroupBox("⚙️ Controls")
        control_layout = QVBoxLayout(control_group)
        
        # Watch status
        self.watch_status = QLabel("Status: Stopped")
        self.watch_status.setStyleSheet("color: #d32f2f; font-weight: bold;")
        control_layout.addWidget(self.watch_status)
        
        # Watch buttons
        self.start_watch_btn = QPushButton("▶️ Start Monitoring")
        self.stop_watch_btn = QPushButton("⏹️ Stop Monitoring")
        self.start_watch_btn.clicked.connect(self.start_watching)
        self.stop_watch_btn.clicked.connect(self.stop_watching)
        self.start_watch_btn.setStyleSheet("QPushButton { background-color: #0d7377; }")
        self.stop_watch_btn.setStyleSheet("QPushButton { background-color: #d32f2f; }")
        self.stop_watch_btn.setEnabled(False)
        control_layout.addWidget(self.start_watch_btn)
        control_layout.addWidget(self.stop_watch_btn)
        
        # Auto-translate option
        self.auto_translate_cb = QCheckBox("🚀 Auto-translate detected files")
        self.auto_translate_cb.setChecked(True)
        control_layout.addWidget(self.auto_translate_cb)
        
        # Queue info
        self.queue_label = QLabel("Queue: 0 files")
        self.queue_label.setStyleSheet("color: #888;")
        control_layout.addWidget(self.queue_label)
        
        left_layout.addWidget(control_group)
        left_layout.addStretch()
        
        # Right panel - Activity log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        log_group = QGroupBox("📋 Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        # Log controls
        log_controls = QHBoxLayout()
        clear_log_btn = QPushButton("🗑️ Clear")
        clear_log_btn.clicked.connect(self.clear_activity_log)
        log_controls.addStretch()
        log_controls.addWidget(clear_log_btn)
        log_layout.addLayout(log_controls)
        
        # Advanced activity log
        self.watch_log = QListWidget()
        self.watch_log.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 8px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2d2d2d;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
        """)
        log_layout.addWidget(self.watch_log)
        
        right_layout.addWidget(log_group)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        layout.addLayout(main_layout)
    
    def setup_stats_tab(self):
        layout = QVBoxLayout(self.stats_tab)
        
        header = QLabel("📊 Translation Statistics")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # Stats display
        stats_group = QGroupBox("Current Session")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_labels = {
            'files': QLabel("Files processed: 0"),
            'languages': QLabel("Languages processed: 0"),
            'subtitles': QLabel("Subtitles translated: 0"),
            'cache_ratio': QLabel("Cache hit ratio: 0%"),
            'duration': QLabel("Duration: 0s"),
            'errors': QLabel("Errors: 0")
        }
        
        for label in self.stats_labels.values():
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_group)
        
        # Reset button
        reset_btn = QPushButton("Reset Statistics")
        reset_btn.clicked.connect(self.reset_stats)
        layout.addWidget(reset_btn)
        
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
            self.add_to_recent_files([file_path])
            self.update_preview_files()
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
                self.add_to_recent_files(files)
                self.update_preview_files()
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
            'enable_cache': True,
            'recent_files': [],
            'profiles': {},
            'watchlist': [],
            'ui_language': 'en',
            'output_naming': '{filename}_{language}',
            'output_encoding': 'utf-8',
            'layout_state': None,
            'translation_service': 'google',
            'use_gpu': GPU_AVAILABLE,
            'offline_mode': False,
            'offline_model': 'marian'
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
            'enable_cache': self.enable_cache.isChecked(),
            'ui_language': self.ui_language_combo.currentData(),
            'output_naming': self.output_naming.text(),
            'output_encoding': self.output_encoding.currentText(),
            'layout_state': self.saveGeometry().toHex().data().decode(),
            'translation_service': self.translation_service.currentData(),
            'use_gpu': self.use_gpu.isChecked(),
            'offline_mode': self.offline_mode.isChecked()
        }
        
        # Update settings object
        self.settings.update(settings)
        self.enabled_languages = selected_languages
        
        # Save to file
        try:
            self.save_settings()
            
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
        
        self.stats.start_session()
        self.worker = TranslationWorker(self.files, selected_langs, current_settings, self.stats)
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
        self.stats.end_session()
        self.update_stats_display()
        self.log_text.append("\n🎉 Translation completed successfully!")
        
        # Process next file in watch queue
        if self.watch_queue:
            next_file = self.watch_queue.pop(0)
            self.queue_label.setText(f"Queue: {len(self.watch_queue)} files")
            self.add_log_entry("🚀 Processing queue", f"{Path(next_file).name}", "success")
            self.files = [next_file]
            QTimer.singleShot(1000, self.start_translation)  # Small delay
        else:
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
    
    def update_preview_files(self):
        self.preview_file_combo.clear()
        if self.files:
            for file in self.files:
                self.preview_file_combo.addItem(Path(file).name, file)
    
    def update_preview(self):
        file_path = self.preview_file_combo.currentData()
        if file_path and Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.preview_text.setPlainText(content[:2000])  # First 2000 chars
            except Exception as e:
                self.preview_text.setPlainText(f"Error reading file: {e}")
    
    def add_watch_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Watch Folder")
        if folder and folder not in self.watch_folders:
            self.watch_folders.append(folder)
            self.watch_folders_list.addItem(folder)
            self.save_watchlist()
            self.add_log_entry("➕ Folder added", Path(folder).name, "success")
    
    def remove_watch_folder(self):
        current_row = self.watch_folders_list.currentRow()
        if current_row >= 0:
            folder = self.watch_folders[current_row]
            self.watch_folders.pop(current_row)
            self.watch_folders_list.takeItem(current_row)
            self.save_watchlist()
            self.add_log_entry("➖ Folder removed", Path(folder).name, "warning")
            # Stop watcher for this folder if running
            for watcher in self.folder_watchers:
                if watcher.folder_path == folder:
                    watcher.stop_watching()
                    self.folder_watchers.remove(watcher)
                    break
    
    def start_watching(self):
        if self.watch_folders:
            for folder in self.watch_folders:
                watcher = FolderWatcher(folder)
                watcher.file_detected.connect(self.on_file_detected)
                watcher.start_watching()
                self.folder_watchers.append(watcher)
            
            self.start_watch_btn.setEnabled(False)
            self.stop_watch_btn.setEnabled(True)
            self.watch_status.setText("Status: Monitoring")
            self.watch_status.setStyleSheet("color: #14a085; font-weight: bold;")
            self.add_log_entry("▶️ Started monitoring", f"{len(self.watch_folders)} folder(s)", "success")
        else:
            QMessageBox.warning(self, "No Folders", "Please add folders to monitor first.")
    
    def stop_watching(self):
        # Stop all folder watchers
        for watcher in self.folder_watchers:
            watcher.stop_watching()
        self.folder_watchers.clear()
        
        # Stop UI translation worker
        if hasattr(self, 'ui_translator') and self.ui_translator.isRunning():
            self.ui_translator.stop()
            self.ui_translator.wait()
        self.watch_queue.clear()
        self.start_watch_btn.setEnabled(True)
        self.stop_watch_btn.setEnabled(False)
        self.watch_status.setText("Status: Stopped")
        self.watch_status.setStyleSheet("color: #d32f2f; font-weight: bold;")
        self.queue_label.setText("Queue: 0 files")
        self.add_log_entry("⏹️ Stopped monitoring", "All folders", "warning")
    
    def on_file_detected(self, file_path):
        folder_name = Path(file_path).parent.name
        self.add_log_entry("📄 File detected", f"{Path(file_path).name}", "info", folder_name)
        
        if self.auto_translate_cb.isChecked():
            if not self.worker or not self.worker.isRunning():
                # Start translation immediately if not busy
                self.files = [file_path]
                self.add_log_entry("🚀 Translation started", f"{Path(file_path).name}", "success")
                self.start_translation()
            else:
                # Add to queue if translation is running
                self.watch_queue.append(file_path)
                self.queue_label.setText(f"Queue: {len(self.watch_queue)} files")
                self.add_log_entry("⏳ Added to queue", f"{Path(file_path).name}", "info")
    
    def reset_stats(self):
        self.stats.reset()
        self.update_stats_display()
    
    def update_stats_display(self):
        self.stats_labels['files'].setText(f"Files processed: {self.stats.files_processed}")
        self.stats_labels['languages'].setText(f"Languages processed: {self.stats.languages_processed}")
        self.stats_labels['subtitles'].setText(f"Subtitles translated: {self.stats.subtitles_translated}")
        self.stats_labels['cache_ratio'].setText(f"Cache hit ratio: {self.stats.get_cache_ratio():.1f}%")
        self.stats_labels['duration'].setText(f"Duration: {self.stats.get_duration():.1f}s")
        self.stats_labels['errors'].setText(f"Errors: {self.stats.errors}")
    
    def update_recent_menu(self):
        self.recent_menu.clear()
        for file_path in self.recent_files[-10:]:
            if Path(file_path).exists():
                action = QAction(Path(file_path).name, self)
                action.triggered.connect(lambda checked, f=file_path: self.load_recent_file(f))
                self.recent_menu.addAction(action)
    
    def load_recent_file(self, file_path):
        self.files = [file_path]
        self.file_label.setText(f"Selected: {Path(file_path).name}")
        self.file_label.setStyleSheet("color: #14a085;")
        self.output_folder = Path(file_path).parent
        self.btn_open_output.setEnabled(True)
        self.update_preview_files()
    
    def update_profile_menu(self):
        # Clear existing profile actions
        for action in self.profile_menu.actions()[2:]:  # Skip "Create Profile" and separator
            self.profile_menu.removeAction(action)
        
        for name in self.profiles.keys():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, n=name: self.load_profile(n))
            self.profile_menu.addAction(action)
    
    def update_profile_combo(self):
        self.profile_combo.clear()
        self.profile_combo.addItem("-- Select Profile --")
        for name in self.profiles.keys():
            self.profile_combo.addItem(name)
    
    def load_profile_from_combo(self, name):
        if name and name != "-- Select Profile --":
            self.load_profile(name)
            # Update checkboxes to match profile
            for lang, checkbox in self.settings_lang_checkboxes.items():
                checkbox.setChecked(lang in self.enabled_languages)
    
    def add_log_entry(self, action, details, level="info", folder=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create styled log entry
        item = QListWidgetItem()
        
        # Color coding based on level
        colors = {
            "success": "#14a085",
            "warning": "#ff9800", 
            "error": "#d32f2f",
            "info": "#2196f3"
        }
        
        color = colors.get(level, "#ffffff")
        folder_text = f" [{folder}]" if folder else ""
        
        # HTML formatted text with colors and styling
        html_text = f"""
        <div style="color: {color}; padding: 2px;">
            <span style="color: #888; font-size: 10px;">[{timestamp}]</span>
            <span style="font-weight: bold; margin-left: 8px;">{action}</span>
            <span style="color: #ccc; margin-left: 8px;">{details}</span>
            <span style="color: #666; font-style: italic;">{folder_text}</span>
        </div>
        """
        
        item.setText(f"[{timestamp}] {action}: {details}{folder_text}")
        item.setToolTip(html_text)
        
        # Set background color based on level
        bg_colors = {
            "success": "#0d4d40",
            "warning": "#4d3300",
            "error": "#4d1a1a", 
            "info": "#1a2d4d"
        }
        
        item.setBackground(QtGui.QColor(bg_colors.get(level, "#2d2d2d")))
        item.setForeground(QtGui.QColor(color))
        
        self.watch_log.addItem(item)
        self.watch_log.scrollToBottom()
        
        # Keep only last 100 entries
        if self.watch_log.count() > 100:
            self.watch_log.takeItem(0)
    
    def clear_activity_log(self):
        self.watch_log.clear()
        self.add_log_entry("🗑️ Log cleared", "Activity log reset", "info")
    
    def focus_file_selection(self):
        self.tab_widget.setCurrentIndex(0)
        self.btn_single.setFocus()
    
    def focus_language_selection(self):
        self.tab_widget.setCurrentIndex(0)
        if hasattr(self, 'lang_flow_widget'):
            self.lang_flow_widget.setFocus()
    
    def focus_progress_log(self):
        self.tab_widget.setCurrentIndex(0)
        self.log_text.setFocus()
    
    def on_ui_language_changed(self):
        new_language = self.ui_language_combo.currentData()
        if new_language != self.ui_language:
            self.ui_language = new_language
            self.refresh_ui_texts()
    
    def refresh_ui_texts(self):
        # Update window title
        self.setWindowTitle(f"🎬 {self.tr('app_title')}")
        
        # Update tab titles
        self.tab_widget.setTabText(0, self.tr('main_tab'))
        self.tab_widget.setTabText(1, self.tr('settings_tab'))
        self.tab_widget.setTabText(2, self.tr('about_tab'))
        self.tab_widget.setTabText(3, self.tr('preview_tab'))
        self.tab_widget.setTabText(4, self.tr('watch_tab'))
        self.tab_widget.setTabText(5, self.tr('stats_tab'))
        
        # Update main tab elements
        if hasattr(self, 'btn_single'):
            self.btn_single.setText(f"📄 {self.tr('select_single_file')}")
            self.btn_folder.setText(f"📁 {self.tr('select_folder')}")
            self.btn_start.setText(f"🚀 {self.tr('start_translation')}")
            self.btn_stop.setText(f"⏹️ {self.tr('stop')}")
            self.btn_clear.setText(f"🗑️ {self.tr('clear_logs')}")
            self.btn_open_output.setText(f"📂 {self.tr('open_output_folder')}")
        
        # Update settings elements
        if hasattr(self, 'save_settings_btn'):
            self.save_settings_btn.setText(f"💾 {self.tr('save_settings')}")
        
        # Update watch tab elements
        if hasattr(self, 'add_folder_btn'):
            self.add_folder_btn.setText(f"➕ {self.tr('add')}")
            self.remove_folder_btn.setText(f"➖ {self.tr('remove')}")
            self.start_watch_btn.setText(f"▶️ {self.tr('start_monitoring')}")
            self.stop_watch_btn.setText(f"⏹️ {self.tr('stop_monitoring')}")
            self.auto_translate_cb.setText(f"🚀 {self.tr('auto_translate_detected')}")
        
        # Update file selection label if no files
        if hasattr(self, 'file_label') and self.file_label.text() == "No files selected":
            self.file_label.setText(self.tr('no_files_selected'))
        
        # Show translation progress
        if hasattr(self, 'ui_language_combo'):
            self.status_bar.showMessage(f"UI translated to {self.ui_language_combo.currentText()}")
        
        # Save the language change
        self.settings['ui_language'] = self.ui_language
        self.save_settings()
    
    def select_original_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Original File", "", "Subtitle Files (*.srt *.ass *.txt)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.orig_text.setPlainText(f.read())
    
    def select_translated_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Translated File", "", "Subtitle Files (*.srt *.ass *.txt)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.trans_text.setPlainText(f.read())
    
    def find_all(self):
        find_text = self.find_input.text()
        if not find_text:
            return
        
        results = []
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if self.regex_mode.isChecked():
                        matches = re.finditer(find_text, content, 0 if self.case_sensitive.isChecked() else re.IGNORECASE)
                        for match in matches:
                            results.append(f"{Path(file_path).name}: Line {content[:match.start()].count(chr(10)) + 1}")
                    else:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if (find_text in line) if self.case_sensitive.isChecked() else (find_text.lower() in line.lower()):
                                results.append(f"{Path(file_path).name}: Line {i + 1}: {line.strip()}")
            except Exception as e:
                results.append(f"Error reading {Path(file_path).name}: {e}")
        
        self.find_results.setPlainText('\n'.join(results))
    
    def replace_all(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not find_text:
            return
        
        replaced_count = 0
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if self.regex_mode.isChecked():
                    new_content, count = re.subn(find_text, replace_text, content, 0 if self.case_sensitive.isChecked() else re.IGNORECASE)
                else:
                    if self.case_sensitive.isChecked():
                        new_content = content.replace(find_text, replace_text)
                        count = content.count(find_text)
                    else:
                        # Case insensitive replace
                        import re
                        new_content = re.sub(re.escape(find_text), replace_text, content, flags=re.IGNORECASE)
                        count = len(re.findall(re.escape(find_text), content, re.IGNORECASE))
                
                if count > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    replaced_count += count
            except Exception as e:
                self.find_results.append(f"Error processing {Path(file_path).name}: {e}")
        
        self.find_results.append(f"\nReplaced {replaced_count} occurrences across {len(self.files)} files")
    

    
    def on_translation_progress(self, language, current, total):
        progress = int((current / total) * 100)
        self.status_bar.showMessage(f"Pre-translating UI: {language} ({progress}%)")
    
    def on_translation_finished(self):
        self.status_bar.showMessage("UI translation cache ready - Language switching will be instant!")
        QTimer.singleShot(3000, lambda: self.status_bar.showMessage("Ready"))
    
    def setup_compare_tab(self):
        layout = QVBoxLayout(self.compare_tab)
        
        header = QLabel("🔍 File Comparison")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # File selection
        file_layout = QHBoxLayout()
        
        # Original file
        orig_layout = QVBoxLayout()
        orig_layout.addWidget(QLabel("Original File:"))
        self.orig_file_btn = QPushButton("Select Original")
        self.orig_file_btn.clicked.connect(self.select_original_file)
        orig_layout.addWidget(self.orig_file_btn)
        
        # Translated file
        trans_layout = QVBoxLayout()
        trans_layout.addWidget(QLabel("Translated File:"))
        self.trans_file_btn = QPushButton("Select Translated")
        self.trans_file_btn.clicked.connect(self.select_translated_file)
        trans_layout.addWidget(self.trans_file_btn)
        
        file_layout.addLayout(orig_layout)
        file_layout.addLayout(trans_layout)
        layout.addLayout(file_layout)
        
        # Comparison view
        compare_layout = QHBoxLayout()
        self.orig_text = QTextEdit()
        self.orig_text.setReadOnly(True)
        self.trans_text = QTextEdit()
        self.trans_text.setReadOnly(True)
        
        compare_layout.addWidget(self.orig_text)
        compare_layout.addWidget(self.trans_text)
        layout.addLayout(compare_layout)
    
    def setup_find_replace_tab(self):
        layout = QVBoxLayout(self.find_replace_tab)
        
        header = QLabel("🔍 Find & Replace")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # Find/Replace controls
        controls_layout = QVBoxLayout()
        
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        controls_layout.addLayout(find_layout)
        
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        controls_layout.addLayout(replace_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Case Sensitive")
        self.regex_mode = QCheckBox("Regular Expression")
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.regex_mode)
        controls_layout.addLayout(options_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        find_btn = QPushButton("Find All")
        replace_btn = QPushButton("Replace All")
        find_btn.clicked.connect(self.find_all)
        replace_btn.clicked.connect(self.replace_all)
        btn_layout.addWidget(find_btn)
        btn_layout.addWidget(replace_btn)
        controls_layout.addLayout(btn_layout)
        
        layout.addLayout(controls_layout)
        
        # Results
        self.find_results = QTextEdit()
        self.find_results.setReadOnly(True)
        layout.addWidget(self.find_results)
    
    def setup_dashboard_tab(self):
        layout = QVBoxLayout(self.dashboard_tab)
        
        header = QLabel("📈 Performance Dashboard")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #14a085; margin: 20px;")
        layout.addWidget(header)
        
        # Add dashboard widget
        self.dashboard = PerformanceDashboard()
        layout.addWidget(self.dashboard)
    

    
    def auto_start_watching(self):
        # Populate watchlist UI with saved folders
        for folder in self.watch_folders:
            if Path(folder).exists():
                self.watch_folders_list.addItem(folder)
            else:
                # Remove non-existent folders
                self.watch_folders.remove(folder)
        
        # Auto-start if folders exist
        if self.watch_folders:
            self.save_watchlist()  # Save cleaned list
            self.start_watching()
            self.add_log_entry("🚀 Auto-started", f"Monitoring {len(self.watch_folders)} saved folders", "success")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SubtitleTranslatorGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()