import os
import sys
from PyQt5 import QtWidgets
import pysrt
import ass
from deep_translator import GoogleTranslator

# Dictionary mapping language names to their language codes.
LANGUAGES = {
    "Spanish": "es",
    "Dutch": "nl",
    "Russian": "ru",
    "German": "de",
    "Turkish": "tr",
    "Chinese": "zh-CN",
    "Japanese": "ja",
    "Persian": "fa",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Indonesian": "id",
    "Filipino": "tl"
}

def init_translator(dest_lang):
    """Initialize the GoogleTranslator with the specified destination language."""
    try:
        translator = GoogleTranslator(source='auto', target=dest_lang)
        return translator
    except Exception as e:
        print(f"Error initializing translator for {dest_lang}: {e}")
        return None

def translate_text(text, translator):
    """Translate text using GoogleTranslator."""
    if not text:
        return text
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def translate_srt(input_file, output_file, dest_lang):
    """Translate an SRT subtitle file and save the result."""
    subs = pysrt.open(input_file)
    translator = init_translator(dest_lang)
    for index, sub in enumerate(subs):
        txt = sub.text.split(":")[-1] if ":" in sub.text else sub.text
        sub.text = translate_text(txt, translator)
        print(f"Processed {index+1}/{len(subs)} | {dest_lang} | Text => {sub.text}")
    subs.save(output_file, encoding="utf-8")

def translate_ass_to_srt(input_file, output_file, dest_lang):
    """Translate an ASS subtitle file, convert to SRT, and save it."""
    with open(input_file, "r", encoding="utf-8-sig") as file:
        doc = ass.parse(file)

    subs = pysrt.SubRipFile()
    translator = init_translator(dest_lang)
    for index, event in enumerate(doc.events, start=1):
        start_time = pysrt.SubRipTime.from_ordinal(event.start.total_seconds() * 1000)
        end_time = pysrt.SubRipTime.from_ordinal(event.end.total_seconds() * 1000)
        
        txt = event.text.split(":")[-1] if ":" in event.text else event.text
        translated_text = translate_text(txt, translator)

        print(f"Processed {index}/{len(doc.events)} | {dest_lang} | Text => {translated_text}")
        subs.append(pysrt.SubRipItem(index, start_time, end_time, translated_text))

    subs.save(output_file, encoding="utf-8")

def translate_plain_txt(input_file, output_file, dest_lang):
    """Translate a plain text file and save as an SRT subtitle."""
    with open(input_file, "r", encoding="utf-8") as file:
        text = file.read()
    
    translator = init_translator(dest_lang)
    translated_text = translate_text(text, translator)
    
    subs = pysrt.SubRipFile([pysrt.SubRipItem(1, pysrt.SubRipTime(0,0,0,0), pysrt.SubRipTime(0,0,10,0), translated_text)])
    subs.save(output_file, encoding="utf-8")

def is_srt_format(file_path):
    """Determine if a .txt file follows the SRT format."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = [file.readline() for _ in range(3)]
        return lines[0].strip().isdigit() and '-->' in lines[1]
    except Exception:
        return False

def process_file(file_path):
    """Process a single subtitle file by translating it into multiple languages."""
    file_dir, file_fullname = os.path.split(file_path)
    file_base, _ = os.path.splitext(file_fullname)
    output_folder = os.path.join(file_dir, file_base)
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Processing file: {file_fullname}")

    for language, lang_code in LANGUAGES.items():
        output_file = os.path.join(output_folder, f"{file_base}_{language}.srt")
        
        if os.path.exists(output_file):
            print(f"File {output_file} For Language {language} ({lang_code}) Already Exists. Skipping...")
            continue
        
        try:
            if file_path.lower().endswith('.srt'):
                translate_srt(file_path, output_file, lang_code)
            elif file_path.lower().endswith('.ass'):
                translate_ass_to_srt(file_path, output_file, lang_code)
            elif file_path.lower().endswith('.txt'):
                if is_srt_format(file_path):
                    translate_srt(file_path, output_file, lang_code)
                else:
                    translate_plain_txt(file_path, output_file, lang_code)
            else:
                print(f"Unsupported format: {file_fullname}")
                return
        except Exception as e:
            print(f"Error processing {file_fullname} for {language} ({lang_code}): {e}")

    print(f"Finished processing: {file_fullname}")

def main():
    """Main function to handle user input and start processing."""
    app = QtWidgets.QApplication(sys.argv)

    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle("Select Processing Mode")
    msg_box.setText("Do you want to process an entire folder of subtitle files?")
    folder_button = msg_box.addButton("Folder", QtWidgets.QMessageBox.AcceptRole)
    file_button = msg_box.addButton("Single File", QtWidgets.QMessageBox.RejectRole)
    msg_box.exec_()

    if msg_box.clickedButton() == folder_button:
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Folder Containing Subtitle Files", "")
        if not folder_path:
            QtWidgets.QMessageBox.information(None, "No Folder Selected", "No folder was selected. Exiting.")
            sys.exit()

        subtitle_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.srt', '.ass', '.txt'))]
        if not subtitle_files:
            QtWidgets.QMessageBox.warning(None, "No Subtitle Files Found", "No valid subtitle files were found in the selected folder.")
            sys.exit()

        for file_path in subtitle_files:
            process_file(file_path)

    else:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Subtitle File", "", "Subtitle Files (*.srt *.ass *.txt)")
        if not file_path:
            QtWidgets.QMessageBox.information(None, "No File Selected", "No file was selected. Exiting.")
            sys.exit()

        process_file(file_path)

    QtWidgets.QMessageBox.information(None, "Success", "Translation completed successfully!")
    sys.exit()

if __name__ == "__main__":
    main()
