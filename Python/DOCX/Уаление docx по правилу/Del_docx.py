import os
from docx import Document

def check_sequence_phrase(docx_file_path, sequence_phrase):
    doc = Document(docx_file_path)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if sequence_phrase in cell.text:
                    return True
    return False

def remove_files_without_sequence_phrase(root_dir, sequence_phrase):
    for root, _, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith('.docx'):
                docx_file_path = os.path.join(root, filename)
                if not check_sequence_phrase(docx_file_path, sequence_phrase):
                    os.remove(docx_file_path)
                    print("Удалил - " + docx_file_path)
                else:
                    print("Оставил - " + docx_file_path)

root_directory = 'C:/Users/.../Documents/Папка/'
phrase_to_check = 'Искомый текст'
remove_files_without_sequence_phrase(root_directory, phrase_to_check)