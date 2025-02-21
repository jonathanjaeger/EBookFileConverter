import os
import subprocess

# Verzeichnis mit den EPUB-Dateien (Hier anpassen!)
input_folder = "E:\Dokumente\Privat\AA_BOOKS"


# Funktion zum Konvertieren von EPUB nach AZW3
def convert_epub_to_azw3(epub_path):
    azw3_path = epub_path.replace(".epub", ".azw3")

    # Calibre CLI-Befehl für die Konvertierung
    command = f'ebook-convert "{epub_path}" "{azw3_path}"'

    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ Konvertiert: {epub_path} → {azw3_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei: {epub_path}")
        print(e)


# Alle EPUB-Dateien im Verzeichnis (und Unterverzeichnissen) finden
for root, _, files in os.walk(input_folder):
    for file in files:
        if file.endswith(".epub"):
            epub_path = os.path.join(root, file)
            convert_epub_to_azw3(epub_path)

print("🎉 Alle Dateien konvertiert!")