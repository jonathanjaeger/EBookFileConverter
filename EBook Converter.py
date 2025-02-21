import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

# -------------------------
# Spracheinstellungen direkt im Code (kein JSON!)
# -------------------------
LANGUAGES = {
    "Deutsch": {
        "title": "📚 E-Book Konverter",
        "select_folder": "📂 Ordner auswählen",
        "no_folder": "📂 Kein Ordner ausgewählt",
        "input_format": "Eingabeformat:",
        "output_format": "Zielformat:",
        "delete_original": "🔘 Originaldatei nach Konvertierung löschen",
        "convert_start": "🔄 Konvertierung starten",
        "delete_files": "🗑 Dateien löschen",
        "delete_ext_label": "Dateitypen zum Löschen:",
        "status": "Wähle einen Ordner aus...",
        "done": "🎉 Fertig! {} Dateien konvertiert.",
        "error": "❌ Fehler bei:",
        "select_language": "🌍 Sprache wählen:"
    },
    "English": {
        "title": "📚 E-Book Converter",
        "select_folder": "📂 Select Folder",
        "no_folder": "📂 No folder selected",
        "input_format": "Input Format:",
        "output_format": "Output Format:",
        "delete_original": "🔘 Delete original file after conversion",
        "convert_start": "🔄 Start Conversion",
        "delete_files": "🗑 Delete Files",
        "delete_ext_label": "File types to delete:",
        "status": "Select a folder...",
        "done": "🎉 Done! {} files converted.",
        "error": "❌ Error with:",
        "select_language": "🌍 Select Language:"
    }
}

# Standard-Sprache direkt im Code (keine settings.json!)
current_lang = "Deutsch"

# -------------------------
# Funktionen
# -------------------------
def update_language(*args):
    global current_lang
    current_lang = language_var.get()
    lang = LANGUAGES[current_lang]

    app.title(lang["title"])
    folder_label.config(text=lang["no_folder"])
    btn_select.config(text=lang["select_folder"])
    lbl_input_format.config(text=lang["input_format"])
    lbl_output_format.config(text=lang["output_format"])
    delete_checkbox.config(text=lang["delete_original"])
    btn_convert.config(text=lang["convert_start"])
    delete_label.config(text=lang["delete_ext_label"])
    btn_delete.config(text=lang["delete_files"])
    lbl_language.config(text=lang["select_language"])
    log_text.set(lang["status"])

def select_folder():
    """ Öffnet den Datei-Dialog und zeigt den gewählten Ordner an """
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)
        folder_label.config(text=f"📂 {folder}")

def convert_ebook(file_path, input_format, output_format, delete_original):
    if not file_path.lower().endswith(f".{input_format.lower()}"):
        return f"{LANGUAGES[current_lang]['error']} {os.path.basename(file_path)}"
    output_path = os.path.splitext(file_path)[0] + "." + output_format.lower()

    # Skip conversion if file already exists
    if skip_converted_var.get() and os.path.exists(output_path):
        return f"⏩ Skipped: {os.path.basename(file_path)} (Already converted)"

    command = f'ebook-convert "{file_path}" "{output_path}"'
    try:
        subprocess.run(command, shell=True, check=True)
        result = f"✅ {os.path.basename(file_path)} → {output_format.upper()}"
        if delete_original:
            os.remove(file_path)
            result += " (Original gelöscht)"
        return result
    except subprocess.CalledProcessError:
        return f"{LANGUAGES[current_lang]['error']} {os.path.basename(file_path)}"

def start_conversion():
    selected_folder = folder_path.get()
    in_format = input_format_var.get()
    out_format = output_format_var.get()
    delete_orig = delete_var.get()
    if not selected_folder:
        messagebox.showwarning("Fehler", "Bitte zuerst einen Ordner auswählen!")
        return

    log_text.set(f"🔄 {LANGUAGES[current_lang]['convert_start']}: {in_format.upper()} → {out_format.upper()}\n")

    def run_conv():
        converted_count = 0
        skipped_count = 0
        for root, _, files in os.walk(selected_folder):
            for file in files:
                if file.lower().endswith(f".{in_format.lower()}"):
                    file_path = os.path.join(root, file)
                    result = convert_ebook(file_path, in_format, out_format, delete_orig)

                    if "Skipped" in result:
                        skipped_count += 1
                    else:
                        converted_count += 1
                    log_text_widget.insert("end", result + "\n")
                    log_text_widget.yview("end")  # Auto-scroll to latest entry
        log_text_widget.insert("end", f"\n{LANGUAGES[current_lang]['done'].format(converted_count)}\n")
        log_text_widget.insert("end", f"⏩ Skipped: {skipped_count} files\n")
        log_text_widget.yview("end")
        messagebox.showinfo("Fertig", f"{converted_count} Dateien konvertiert.\n{skipped_count} wurden übersprungen.")

    threading.Thread(target=run_conv, daemon=True).start()

def delete_files():
    selected_folder = folder_path.get()
    ext = delete_ext_var.get().strip().lower()

    if not selected_folder:
        messagebox.showwarning("Fehler", "Bitte zuerst einen Ordner auswählen!")
        return

    count = 0
    for root, _, files in os.walk(selected_folder):
        for file in files:
            if file.lower().endswith(f".{ext}"):
                os.remove(os.path.join(root, file))
                count += 1

    messagebox.showinfo("Löschen", f"🗑 {count} Dateien mit Endung '{ext}' wurden gelöscht.")
    log_text.set(log_text.get() + f"\n🗑 {count} Dateien mit Endung '{ext}' gelöscht.\n")

# -------------------------
# GUI erstellen (Mit `tkinter`)
# -------------------------
app = tk.Tk()
app.title(LANGUAGES[current_lang]["title"])
app.geometry("600x550")

# Variablen
folder_path = tk.StringVar()
log_text = tk.StringVar(value=LANGUAGES[current_lang]["status"])
input_format_var = tk.StringVar(value="epub")
output_format_var = tk.StringVar(value="azw3")
delete_var = tk.BooleanVar(value=False)
language_var = tk.StringVar(value=current_lang)
delete_ext_var = tk.StringVar(value="pdf")
skip_converted_var = tk.BooleanVar(value=True)  # Default: Skip already converted files


language_var.trace_add("write", update_language)

# GUI-Elemente
folder_label = tk.Label(app, text=LANGUAGES[current_lang]["no_folder"])
folder_label.pack(pady=5)
btn_select = tk.Button(app, text=LANGUAGES[current_lang]["select_folder"], command=select_folder)
btn_select.pack(pady=5)

lbl_input_format = tk.Label(app, text=LANGUAGES[current_lang]["input_format"])
lbl_input_format.pack()
ttk.Combobox(app, textvariable=input_format_var, values=["epub", "pdf", "mobi", "azw3", "txt"]).pack()

# Ausgabeformat auswählen
lbl_output_format = tk.Label(app, text=LANGUAGES[current_lang]["output_format"])
lbl_output_format.pack()

output_format_menu = ttk.Combobox(app, textvariable=output_format_var, values=["azw3", "mobi", "pdf", "epub", "txt"])
output_format_menu.pack()

# Option zum Löschen der Eingabedateien nach der Konvertierung
delete_checkbox = tk.Checkbutton(app, text=LANGUAGES[current_lang]["delete_original"], variable=delete_var)
delete_checkbox.pack(pady=5)

skip_checkbox = tk.Checkbutton(app, text="Skip already converted files", variable=skip_converted_var)
skip_checkbox.pack(pady=5)

btn_convert = tk.Button(app, text=LANGUAGES[current_lang]["convert_start"], command=start_conversion)
btn_convert.pack(pady=10)

# Frame for the log and scrollbar
log_frame = tk.Frame(app)
log_frame.pack(pady=5, fill="both", expand=True)

# Scrollable text widget for log output
log_text_widget = scrolledtext.ScrolledText(log_frame, wrap="word", height=10)
log_text_widget.pack(fill="both", expand=True)
log_text_widget.insert("end", LANGUAGES[current_lang]["status"] + "\n")
log_text_widget.yview("end")


def log_message(message):
    """ Adds a message to the log with auto-scrolling """
    log_text_widget.insert("end", message + "\n")
    log_text_widget.yview("end")  # Auto-scroll to the latest entry


# Dateien löschen
delete_label = tk.Label(app, text=LANGUAGES[current_lang]["delete_ext_label"])
delete_label.pack()

delete_ext_menu = ttk.Combobox(app, textvariable=delete_ext_var, values=["pdf", "epub", "mobi", "txt", "azw3"])
delete_ext_menu.pack()

btn_delete = tk.Button(app, text=LANGUAGES[current_lang]["delete_files"], command=delete_files)
btn_delete.pack(pady=5)

# Sprachauswahl (unten rechts)
language_frame = tk.Frame(app)
language_frame.pack(side="bottom", anchor="se", padx=10, pady=10)

lbl_language = tk.Label(language_frame, text=LANGUAGES[current_lang]["select_language"])
lbl_language.pack(side="left", padx=5)

language_menu = ttk.Combobox(language_frame, textvariable=language_var, values=["Deutsch", "English"])
language_menu.pack(side="left")

# Start GUI
app.mainloop()
