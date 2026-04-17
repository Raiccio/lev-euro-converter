# lev-euro-converter

Конвертиране на DOCX документи от лева в евро.

## Употреба

```bash
lev-euro-converter.exe документ.docx
```

Ще създаде `документ_eur.docx` в същата папка.

## Инсталация

1. Свали най-новия `.exe` от [Releases](https://github.com/raiccio/lev-euro-converter/releases)
2. Постави до DOCX файловете
3. Стартирай

## Поддържани формати

| Вход | Изход |
|------|------|
| `100 лв.` | `51.16 евро` |
| `100,00 лв.` | `51.16 евро` |
| `100 000,00 лв.` | `51 156,45 евро` |
| `/петдесет/` | `/двадесет и пет евро и петдесет и осем евроцента/` |
| `(петдесет)` | `(двадесет и пет евро и петдесет и осем евроцента)` |
| `50 стотинки` | `25.58 евроцента` |

## Курс

1 EUR = 1.95583 BGN (фиксиран)

---

# lev-euro-converter

Convert DOCX documents from BGN to EUR.

## Usage

```bash
lev-euro-converter.exe document.docx
```

Will create `document_eur.docx` in the same folder.

## Installation

1. Download the latest `.exe` from [Releases](https://github.com/raiccio/lev-euro-converter/releases)
2. Place next to your DOCX files
3. Run

## Supported Formats

| Input | Output |
|-------|--------|
| `100 лв.` | `51.16 евро` |
| `100,00 лв.` | `51.16 евро` |
| `100 000,00 лв.` | `51 156,45 евро` |
| `/fifty/` | `/twenty-five euros and fifty-eight eurocents/` |
| `(fifty)` | `(twenty-five euros and fifty-eight eurocents)` |
| `50 стотинки` | `25.58 евроцента` |

## Exchange Rate

1 EUR = 1.95583 BGN (fixed)

## Build

```bash
GOOS=windows GOARCH=amd64 go build -o lev-euro-converter.exe
```