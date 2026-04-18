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


def convert_docx(input_path, output_path):
    """Convert DOCX file from BGN to EUR
    
    Returns:
        dict: {'success': bool, 'changes': list of str, 'error': str or None}
    """
    
    changes = []
    try:
        doc = Document(input_path)
        
        # Process each paragraph
        for paragraph in doc.paragraphs:
            if paragraph.text and paragraph.text.strip():
                old_text = paragraph.text
                new_text, section_changes = process_text(paragraph.text)
                if section_changes:
                    changes.extend(section_changes)
                    paragraph.text = new_text
        
        # Process each table cell
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.text and paragraph.text.strip():
                            old_text = paragraph.text
                            new_text, section_changes = process_text(paragraph.text)
                            if section_changes:
                                changes.extend(section_changes)
                                paragraph.text = new_text
        
        # Also process runs within paragraphs (some docx store text in runs)
        for paragraph in doc.paragraphs:
            for run in paragraph.runs:
                if run.text and run.text.strip():
                    old_text = run.text
                    new_text, section_changes = process_text(run.text)
                    if section_changes:
                        changes.extend(section_changes)
                        run.text = new_text
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            if run.text and run.text.strip():
                                old_text = run.text
                                new_text, section_changes = process_text(run.text)
                                if section_changes:
                                    changes.extend(section_changes)
                                    run.text = new_text
        
        doc.save(output_path)
        
        return {'success': True, 'changes': changes, 'error': None}
        
    except Exception as e:
        return {'success': False, 'changes': changes, 'error': str(e)}


def has_transliteration(text):
    """Check if text has word transliteration"""
    if not text:
        return False
    return bool(re.search(r'/[а-яА-Я\w]+/|/[а-яА-Я\w]+\)', text, re.IGNORECASE))


def process_text(text):
    """Process text and replace BGN amounts with EUR
    
    Returns:
        tuple: (new_text, list_of_changes)
    """
    if not text or not text.strip():
        return text, []
    
    # Clean up \xa0 (non-breaking space) first
    text = text.replace('\xa0', ' ')
    text = text.replace('\u00a0', ' ')
    
    original_text = text
    changes = []
    
    # Check if transliteration exists in this text segment
    text_has_transliteration = has_transliteration(text)
    
    # Pattern 1: Slash patterns /word/ like "50 /петдесет/ лева"
    slash_pattern = r'(\d[\d\s]*(?:[.,]\d+)?)\s*/([а-яА-Я\w\s]+)/\s*(?:лева|лв\.?)'
    for match in re.findall(slash_pattern, text, re.IGNORECASE):
        number_str = match[0].strip()
        word_part = match[1].strip()
        
        amount = parse_bulgarian_number(number_str)
        if amount is None:
            continue
        
        eur = convert_bgn_to_eur(amount)
        
        # Convert word part
        word_num = word_to_number(word_part)
        if word_num and word_num > 0:
            word_eur = convert_bgn_to_eur(word_num)
            word_eur_words = format_eur_words(word_eur)
            output = f"{eur:.2f} /{word_eur_words}/"
        else:
            output = f"{eur:.2f} /{word_part}/"
        
        search = f"{number_str} /{match[1]}/"
        if search in text:
            changes.append(f"{search}лева --> {output}евро")
            text = text.replace(search, output)
    
    # Pattern 2: Paren patterns (word) like "50 (петдесет) лева"
    paren_pattern = r'(\d[\d\s]*(?:[.,]\d+)?)\s*\(([а-яА-Я\w\s]+)\)\s*(?:лева|лв\.?)'
    for match in re.findall(paren_pattern, text, re.IGNORECASE):
        number_str = match[0].strip()
        word_part = match[1].strip()
        
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
        
        search = f"{number_str} ({match[1]})"
        if search in text:
            changes.append(f"{search}лева --> {output}евро")
            text = text.replace(search, output)
    
    # Pattern 3: Simple currency without words "100 лв." or "100 лева"
    currency_patterns = [
        r'(\d[\d\s]*(?:[.,]\d+)?)\s*(лв\.|лв|лева|lv|LV)',
        r'(\d[\d\s]*(?:[.,]\d+)?)\s*(стотинки|ст\.)',
    ]
    
    for pattern in currency_patterns:
        for match in re.findall(pattern, text, re.IGNORECASE):
            amount_str = match[0].strip()
            currency = match[1]
            
            amount = parse_bulgarian_number(amount_str)
            if amount is None:
                continue
            
            eur = convert_bgn_to_eur(amount)
            
            # Format output based on original having transliteration or not
            if currency.lower() in ['стотинки', 'ст.']:
                output = f"{eur:.2f} евроцента"
            else:
                if text_has_transliteration:
                    eur_words = format_eur_words(eur)
                    output = f"{eur:.2f} {eur_words}"
                else:
                    output = f"{eur:.2f} евро"
            
            # Try different spacing
            search = f"{amount_str} {currency}"
            if search in text:
                changes.append(f"{search} --> {output}")
                text = text.replace(search, output)
            elif f"{amount_str}  {currency}" in text:
                text = text.replace(f"{amount_str}  {currency}", output)
            elif f"{amount_str}{currency}" in text:
                text = text.replace(f"{amount_str}{currency}", output)
    
    return text, changes


def get_output_path(input_path):
    """Generate output path"""
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    return os.path.join(dir_name, f"{name}_eur{ext}")