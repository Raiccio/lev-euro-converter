"""
lev-euro-converter GUI
Tkinter native Windows GUI
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import webbrowser

from docx_converter import convert_docx, get_output_path


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("lev-euro-converter")
        self.root.geometry("800x750")
        
        # Make GUI resizable
        self.root.resizable(True, True)
        self.root.minsize(600, 500)
        
        self.files = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="lev-euro-converter", font=("Arial", 16, "bold"))
        title.pack(pady=(10, 2))
        
        subtitle = tk.Label(self.root, text="Конвертиране на DOCX от лева в евро", font=("Arial", 10))
        subtitle.pack(pady=0)
        
        rate_label = tk.Label(self.root, text="1 EUR = 1.95583 BGN", font=("Arial", 9, "italic"))
        rate_label.pack(pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        add_btn = tk.Button(btn_frame, text="Добави файлове", command=self.add_files, width=15)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(btn_frame, text="Изчисти", command=self.clear_files, width=15)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Input files list
        tk.Label(self.root, text="Избрани файлове:", anchor=tk.W).pack(padx=20, pady=(5, 0), fill=tk.X)
        
        list_frame = tk.Frame(self.root)
        list_frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.EXTENDED)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Convert button
        convert_btn = tk.Button(self.root, text="Конвертирай", command=self.convert_files, 
                         bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), width=20)
        convert_btn.pack(pady=8)
        
        # Output/logs section
        tk.Label(self.root, text="Конвертирани файлове и промени:", anchor=tk.W).pack(padx=20, pady=(5, 0), fill=tk.X)
        
        log_frame = tk.Frame(self.root)
        log_frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        log_vscroll = tk.Scrollbar(log_frame, orient=tk.VERTICAL)
        log_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        log_hscroll = tk.Scrollbar(log_frame, orient=tk.HORIZONTAL)
        log_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.log_listbox = tk.Listbox(log_frame, 
                                       xscrollcommand=log_hscroll.set,
                                       yscrollcommand=log_vscroll.set)
        self.log_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_vscroll.config(command=self.log_listbox.yview)
        log_hscroll.config(command=self.log_listbox.xview)
        
        # Row between log and buttons - status on right
        row_frame = tk.Frame(self.root)
        row_frame.pack(fill=tk.X, padx=20, pady=5)
        
        open_btn = tk.Button(row_frame, text="Отвори папка", command=self.open_folder, width=15)
        open_btn.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(row_frame, text="Готово", font=("Arial", 9), anchor=tk.E)
        self.status_label.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Bottom info - version and email
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=8)
        
        version = tk.Label(info_frame, text="Version 1.0.1", font=("Arial", 8), fg="#666666")
        version.pack(side=tk.LEFT)
        
        sep = tk.Label(info_frame, text=" • ", font=("Arial", 8), fg="#666666")
        sep.pack(side=tk.LEFT)
        
        # Email - clickable
        email = tk.Label(info_frame, text="badevraycho@gmail.com", font=("Arial", 8), fg="#0066CC", cursor="hand2")
        email.pack(side=tk.LEFT)
        email.bind("<Button-1>", lambda e: webbrowser.open("mailto:badevraycho@gmail.com"))
    
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
                            self.log_listbox.insert(tk.END, f"    {change}")
                        self.log_listbox.insert(tk.END, f"  → {os.path.basename(output_path)}")
                    else:
                        self.log_listbox.insert(tk.END, f"  ⚠ Няма намерени суми в лева")
                    success += 1
                else:
                    self.log_listbox.insert(tk.END, f"  ✗ Грешка: {result['error']}")
                    errors += 1
                
                self.log_listbox.see(tk.END)
                
            except Exception as e:
                self.log_listbox.insert(tk.END, f"  ✗ Грешка: {str(e)}")
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