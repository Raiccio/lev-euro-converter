"""
lev-euro-converter GUI
Tkinter native Windows GUI
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

from docx_converter import convert_docx, get_output_path


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("lev-euro-converter")
        self.root.geometry("600x550")
        
        # Make GUI resizable
        self.root.resizable(True, True)
        self.root.minsize(400, 400)
        
        # Selected files
        self.files = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="lev-euro-converter", font=("Arial", 18, "bold"))
        title.pack(pady=10)
        
        subtitle = tk.Label(self.root, text="Конвертиране на DOCX от лева в евро", font=("Arial", 10))
        subtitle.pack(pady=5)
        
        # Rate label
        rate_label = tk.Label(self.root, text="1 EUR = 1.95583 BGN", font=("Arial", 9, "italic"))
        rate_label.pack(pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        add_btn = tk.Button(btn_frame, text="Добави файлове", command=self.add_files, width=15)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(btn_frame, text="Изчисти", command=self.clear_files, width=15)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Input files list
        tk.Label(self.root, text="Избрани файлове:", anchor=tk.W).pack(padx=20, pady=(10, 0))
        
        list_frame = tk.Frame(self.root)
        list_frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Convert button
        convert_btn = tk.Button(self.root, text="Конвертирай", command=self.convert_files, 
                         bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=20)
        convert_btn.pack(pady=10)
        
        # Output files list
        tk.Label(self.root, text="Конвертирани файлове:", anchor=tk.W).pack(padx=20, pady=(10, 0))
        
        out_list_frame = tk.Frame(self.root)
        out_list_frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        out_scrollbar = tk.Scrollbar(out_list_frame)
        out_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.output_listbox = tk.Listbox(out_list_frame)
        self.output_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_listbox.config(yscrollcommand=out_scrollbar.set)
        out_scrollbar.config(command=self.output_listbox.yview)
        
        # Open folder button
        open_btn = tk.Button(self.root, text="Отвори папка", command=self.open_folder, width=15)
        open_btn.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="Готово", font=("Arial", 9))
        self.status_label.pack(pady=5)
        
        # Version
        version = tk.Label(self.root, text="v1.0.0", font=("Arial", 8))
        version.pack(pady=5)
    
    def add_files(self):
        """Open file dialog to add DOCX files"""
        filenames = filedialog.askopenfilenames(
            title="Избери DOCX файлове",
            filetypes=[("DOCX файлове", "*.docx"), ("Всички файлове", "*.*")]
        )
        
        for filename in filenames:
            if filename not in self.files:
                self.files.append(filename)
                self.file_listbox.insert(tk.END, os.path.basename(filename))
        
        self.status_label.config(text=f"Избрани: {len(self.files)} файла")
    
    def clear_files(self):
        """Clear all selected files"""
        self.files = []
        self.file_listbox.delete(0, tk.END)
        self.output_listbox.delete(0, tk.END)
        self.status_label.config(text="Готово")
    
    def convert_files(self):
        """Convert all selected files"""
        if not self.files:
            self.status_label.config(text="Няма избрани файлове")
            return
        
        self.status_label.config(text="Конвертиране...")
        self.root.update()
        
        success = 0
        errors = 0
        self.output_listbox.delete(0, tk.END)
        
        for filename in self.files:
            try:
                output_path = get_output_path(filename)
                convert_docx(filename, output_path)
                self.output_listbox.insert(tk.END, os.path.basename(output_path))
                success += 1
            except Exception as e:
                errors += 1
                self.status_label.config(text=f"Грешка: {str(e)[:50]}")
        
        if errors == 0:
            self.status_label.config(text=f"Готово: {success} файла")
        else:
            self.status_label.config(text=f"Успешни: {success}, Грешки: {errors}")
    
    def open_folder(self):
        """Open folder in Explorer"""
        if self.files:
            folder = os.path.dirname(self.files[0])
            os.startfile(folder)


def main():
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()