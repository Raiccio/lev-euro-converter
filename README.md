# lev-euro-converter

Конвертиране на DOCX документи от лева в евро.

## Инсталация

```powershell
# Инсталирай необходимите библиотеки
pip install python-docx pyinstaller
```

## Стартиране

```powershell
python main.py
```

## Запазване като .exe

```powershell
pyinstaller --onefile --name=lev-euro-converter --windowed main.py
```

## Употреба

1. Кликни "Добави файлове" за да избереш DOCX файлове
2. Прегледай списъка с избрани файлове
3. Кликни "Конвертирай" за да конвертираш
4. Конвертираните файлове се запазват в същата папка с _eur
5. Кликни "Отвори папка" за да отвориш папката с конвертираните файлове

## Поддържани формати

| Сума | Превалутиране |
|------|------|
| `100 лв.` | `51.16 евро` |
| `100,00 /сто/ лв.` | `51.16 /петдесет и едно евро и шестнадесет евроцента/ евро` |
| `100 000,00 лева` | `51 156,45 евро` |

---

# lev-euro-converter

Convert DOCX documents from BGN to EUR.

## Installation

```powershell
pip install python-docx pyinstaller
```

## Run

```powershell
python main.py
```

## Build as .exe

```powershell
pyinstaller --onefile --name=lev-euro-converter --windowed main.py
```

## Usage

1. Click "Добави файлове" to select DOCX files
2. Review selected files in the list
3. Click "Конвертирай" to convert
4. Converted files are saved in same folder with _eur suffix
5. Click "Отвори папка" to open the output folder

## Exchange Rate

1 EUR = 1.95583 BGN (fixed)
