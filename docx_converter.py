"""
DOCX converter for BGN to EUR
Uses python-docx for reliable DOCX handling
"""

import os
import re
import traceback
from docx import Document
from converter_numbers import convert_bgn_to_eur, format_eur_words, parse_bulgarian_number, word_to_number

RATE = 1.95583

# Currency patterns - match number + currency
CURRENCY_PATTERNS = [
    r'(\d{1,3}(?:\s?\d{3})*(?:[.,]\d+)?)\s*(лв\.|лв|лева|lv|LV)',
    r'(\d{1,3}(?:\s?\d{3})*(?:[.,]\d+)?)\s*(стотинки|ст\.)',
]

# Patterns WITH transliteration - check if words exist before currency
SLASH_PATTERN = r'(\d[\d\s\xa0]*(?:[.,]\d+)?)\s*/([а-яА-Я\w\s]+)/\s*(?:лева|лв\.)'
PAREN_PATTERN = r'(\d[\d\s\xa0]*(?:[.,]\d+)?)\s*\(([а-яА-Я\w\s]+)\)\s*(?:лева|лв\.)'


def has_transliteration(text):
    """Check if text has word transliteration in / or ()"""
    return bool(re.search(r'/[а-яА-Я\w]+/|/[а-яА-Я\w]+\)', text, re.IGNORECASE))


def convert_docx(input_path, output_path):
    """Convert DOCX file from BGN to EUR"""
    
    try:
        # Load the document
        doc = Document(input_path)
        
        # Process each paragraph
        for paragraph in doc.paragraphs:
            if paragraph.text:
                try:
                    paragraph.text = process_text(paragraph.text)
                except Exception as e:
                    print(f"Paragraph error: {e}")
        
        # Process each table
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.text:
                            try:
                                paragraph.text = process_text(paragraph.text)
                            except Exception as e:
                                print(f"Table cell error: {e}")
        
        # Save the document
        doc.save(output_path)
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to convert {input_path}: {e}\n{traceback.format_exc()}")


def process_text(text):
    """Process text and replace BGN amounts with EUR"""
    if not text:
        return text
    
    # Check if this text has transliteration (word in / or ())
    text_has_transliteration = has_transliteration(text)
    
    # First: Handle slash patterns /word/ 
    matches = re.findall(SLASH_PATTERN, text, re.IGNORECASE)
    for match in matches:
        number_str = match[0]
        word_part = match[1].strip()
        
        amount = parse_bulgarian_number(number_str)
        if amount is None:
            continue
        
        eur = convert_bgn_to_eur(amount)
        
        # Convert the word part if it's a Bulgarian number
        word_num = word_to_number(word_part)
        if word_num and word_num > 0:
            word_eur = convert_bgn_to_eur(word_num)
            word_eur_words = format_eur_words(word_eur)
            output = f"{eur:.2f} /{word_eur_words}/"
        else:
            # Keep original word format but convert the number
            output = f"{eur:.2f} /{word_part}/"
        
        # Try different search patterns
        search_variants = [
            f"{number_str} /{match[1]}/",
            f"{number_str}  /{match[1]}/",
        ]
        for search in search_variants:
            if search in text:
                text = text.replace(search, output)
                break
    
    # Second: Handle parentheses patterns (word)
    matches = re.findall(PAREN_PATTERN, text, re.IGNORECASE)
    for match in matches:
        number_str = match[0]
        word_part = match[1].strip()
        
        amount = parse_bulgarian_number(number_str)
        if amount is None:
            continue
        
        eur = convert_bgn_to_eur(amount)
        
        # Convert the word part
        word_num = word_to_number(word_part)
        if word_num and word_num > 0:
            word_eur = convert_bgn_to_eur(word_num)
            word_eur_words = format_eur_words(word_eur)
            output = f"{eur:.2f} ({word_eur_words})"
        else:
            output = f"{eur:.2f} ({word_part})"
        
        search_variants = [
            f"{number_str} ({match[1]})",
            f"{number_str}  ({match[1]})",
        ]
        for search in search_variants:
            if search in text:
                text = text.replace(search, output)
                break
    
    # Third: Handle simple currency patterns WITHOUT transliteration
    for pattern in CURRENCY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match[0]
            currency = match[1]
            
            # Parse the number
            amount = parse_bulgarian_number(amount_str)
            if amount is None:
                continue
            
            # Convert to EUR
            eur = convert_bgn_to_eur(amount)
            
            # Format output - only add words if original has transliteration
            if currency.lower() in ['стотинки', 'ст.']:
                output = f"{eur:.2f} евроцента"
            else:
                if text_has_transliteration:
                    # Include word conversion
                    eur_words = format_eur_words(eur)
                    output = f"{eur:.2f} {eur_words}"
                else:
                    # Number only, no words
                    output = f"{eur:.2f} евро"
            
            # Replace in text - handle various spacing
            search_variants = [
                f"{amount_str} {currency}",
                f"{amount_str}  {currency}",
                f"{amount_str}{currency}",
            ]
            replaced = False
            for search in search_variants:
                if search in text:
                    text = text.replace(search, output)
                    replaced = True
                    break
            if not replaced:
                # Try partial replacement
                text = text.replace(amount_str, output.replace(" евро", "").replace(" евроцента", ""), 1)
    
    return text


def get_output_path(input_path):
    """Generate output path with _eur suffix"""
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    return os.path.join(dir_name, f"{name}_eur{ext}")