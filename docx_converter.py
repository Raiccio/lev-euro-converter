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

# Debug flag - set to True to see what's happening
DEBUG = False

def debug_print(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")


# Currency patterns - match number + currency
CURRENCY_PATTERNS = [
    r'(\d+[\d\s\xa0]*(?:[.,]\d+)?)\s*(лв\.|лв|лева|lv|LV)',
    r'(\d+[\d\s\xa0]*(?:[.,]\d+)?)\s*(стотинки|ст\.)',
]

# Patterns WITH transliteration
SLASH_PATTERN = r'(\d[\d\s\xa0]*(?:[.,]\d+)?)\s*/([а-яА-Я\w\s]+)/\s*(?:лева|лв\.)'
PAREN_PATTERN = r'(\d[\d\s\xa0]*(?:[.,]\d+)?)\s*\(([а-яА-Я\w\s]+)\)\s*(?:лева|лв\.)'


def has_transliteration(text):
    """Check if text has word transliteration in / or ()"""
    return bool(re.search(r'/[а-яА-Я\w]+/|/[а-яА-Я\w]+\)', text, re.IGNORECASE))


def convert_docx(input_path, output_path):
    """Convert DOCX file from BGN to EUR"""
    
    try:
        debug_print(f"Opening: {input_path}")
        
        # Load the document
        doc = Document(input_path)
        
        conversions_made = 0
        
        # Process each paragraph
        for paragraph in doc.paragraphs:
            if paragraph.text and paragraph.text.strip():
                old_text = paragraph.text
                new_text = process_text(paragraph.text)
                if old_text != new_text:
                    paragraph.text = new_text
                    conversions_made += 1
        
        # Process each table
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.text and paragraph.text.strip():
                            old_text = paragraph.text
                            new_text = process_text(paragraph.text)
                            if old_text != new_text:
                                paragraph.text = new_text
                                conversions_made += 1
        
        debug_print(f"Conversions made: {conversions_made}")
        
        # Save the document
        doc.save(output_path)
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to convert {input_path}: {e}\n{traceback.format_exc()}")


def process_text(text):
    """Process text and replace BGN amounts with EUR"""
    if not text or not text.strip():
        return text
    
    original_text = text
    conversions = 0
    
    # Check if this text segment has transliteration
    text_has_transliteration = has_transliteration(text)
    if text_has_transliteration:
        debug_print(f"Found transliteration in: {text[:100]}")
    
    # First: Handle slash patterns like "12 500 /дванадесет хиляди/ лева"
    matches = re.findall(SLASH_PATTERN, text, re.IGNORECASE)
    for match in matches:
        number_str = match[0]
        word_part = match[1].strip()
        
        debug_print(f"Slash pattern: '{number_str}' /'{word_part}'/")
        
        amount = parse_bulgarian_number(number_str)
        if amount is None:
            debug_print(f"  Could not parse number: {number_str}")
            continue
        
        eur = convert_bgn_to_eur(amount)
        
        # Convert the word part
        word_num = word_to_number(word_part)
        if word_num and word_num > 0:
            word_eur = convert_bgn_to_eur(word_num)
            word_eur_words = format_eur_words(word_eur)
            output = f"{eur:.2f} /{word_eur_words}/"
        else:
            output = f"{eur:.2f} /{word_part}/"
        
        # Replace
        search_variants = [
            f"{number_str} /{match[1]}/",
            f"{number_str}  /{match[1]}/",
        ]
        for search in search_variants:
            if search in text:
                text = text.replace(search, output)
                conversions += 1
                debug_print(f"  Replaced: {search} -> {output}")
                break
    
    # Second: Handle parentheses patterns
    matches = re.findall(PAREN_PATTERN, text, re.IGNORECASE)
    for match in matches:
        number_str = match[0]
        word_part = match[1].strip()
        
        debug_print(f"Paren pattern: '{number_str}' ('{word_part}')/")
        
        amount = parse_bulgarian_number(number_str)
        if amount is None:
            continue
        
        eur = convert_bgn_to_eur(amount)
        
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
                conversions += 1
                break
    
    # Third: Handle simple currency patterns WITHOUT transliteration
    for pattern in CURRENCY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match[0]
            currency = match[1]
            
            debug_print(f"Currency pattern: '{amount_str}' '{currency}'")
            
            amount = parse_bulgarian_number(amount_str)
            if amount is None:
                debug_print(f"  Could not parse: {amount_str}")
                continue
            
            eur = convert_bgn_to_eur(amount)
            
            # Format output
            if currency.lower() in ['стотинки', 'ст.']:
                output = f"{eur:.2f} евроцента"
            else:
                if text_has_transliteration:
                    eur_words = format_eur_words(eur)
                    output = f"{eur:.2f} {eur_words}"
                else:
                    output = f"{eur:.2f} евро"
            
            # Try different spacing variants
            search_variants = [
                f"{amount_str} {currency}",
                f"{amount_str}  {currency}",
                f"{amount_str}{currency}",
            ]
            replaced = False
            for search in search_variants:
                if search in text:
                    text = text.replace(search, output)
                    conversions += 1
                    debug_print(f"  Replaced: {search} -> {output}")
                    replaced = True
                    break
            
            if not replaced:
                # Try partial: just show what we would replace
                debug_print(f"  NOT replaced - search variants: {search_variants}")
    
    if conversions > 0:
        debug_print(f"Total conversions in text segment: {conversions}")
    
    return text


def get_output_path(input_path):
    """Generate output path with _eur suffix"""
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    return os.path.join(dir_name, f"{name}_eur{ext}")