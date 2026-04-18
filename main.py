"""
lev-euro-converter GUI
Tkinter native Windows GUI
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os

from docx_converter import convert_docx, get_output_path


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("lev-euro-converter")
        self.root.geometry("650x600")
        
        # Make GUI resizable
        self.root.resizable(True, True)
        self.root.minsize(450, 400)
        
        self.files = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="lev-euro-converter", font=("Arial", 18, "bold"))
        title.pack(pady=10)
        
        subtitle = tk.Label(self.root, text="Конвертиране на DOCX от лева в евро", font=("Arial", 10))
        subtitle.pack(pady=5)
        
        rate_label = tk.Label(self.root, text="1 EUR = 1.95583 BGN", font=("Arial", 9, "italic"))
        rate_label.pack(pady=5)
        
        # Buttons
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
        
        # Output/logs section
        tk.Label(self.root, text="Конвертирани файлове и промени:", anchor=tk.W).pack(padx=20, pady=(10, 0))
        
        log_frame = tk.Frame(self.root)
        log_frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        log_scrollbar = tk.Scrollbar(log_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_listbox = tk.Listbox(log_frame)
        self.log_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_listbox.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_listbox.yview)
        
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
        self.files = []
        self.file_listbox.delete(0, tk.END)
        self.log_listbox.delete(0, tk.END)
        self.status_label.config(text="Готово")
    
    def convert_files(self):
        if not self.files:
            self.status_label.config(text="Няма избрани файлове")
            return
        
        self.status_label.config(text="Конвертиране...")
        self.root.update()
        
        success = 0
        errors = 0
        
        for filename in self.files:
            try:
                output_path = get_output_path(filename)
                basename = os.path.basename(filename)
                
                self.log_listbox.insert(tk.END, f"Конвертиране: {basename}...")
                self.log_listbox.see(tk.END)
                self.root.update()
                
                result = convert_docx(filename, output_path)
                
                if result['success']:
                    if result['changes']:
                        self.log_listbox.insert(tk.END, f"  ✓ Промени ({len(result['changes'])}):")
                        for change in result['changes']:
                            # Truncate long changes for display
                            display_change = change[:80] + "..." if len(change) > 80 else change
                            self.log_listbox.insert(tk.END, f"    {display_change}")
                        self.log_listbox.insert(tk.END, f"  → {os.path.basename(output_path)}")
                    else:
                        self.log_listbox.insert(tk.END, f"  ⚠ Няма намерени суми в лева")
                    success += 1
                else:
                    self.log_listbox.insert(tk.END, f"  ✗ Грешка: {result['error']}")
                    errors += 1
                
                self.log_listbox.see(tk.END)
                
            except Exception as e:
                self.log_listbox.insert(tk.END, f"  ✗ Грешка: {str(e)[:50]}")
                errors += 1
        
        self.status_label.config(text=f"Готово: {success} успешни, {errors} грешки")
    
    def open_folder(self):
        if self.files:
            folder = os.path.dirname(self.files[0])
            try:
                os.startfile(folder)
            except:
                self.status_label.config(text="Не може да се отвори папката")


def main():
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()