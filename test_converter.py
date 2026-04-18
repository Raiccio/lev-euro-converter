#!/usr/bin/env python3
"""CLI tool to test BGN to EUR conversion"""

import sys
from converter_numbers import (
    convert_bgn_to_eur,
    format_eur_words,
    parse_bulgarian_number,
    number_to_words_bulgarian
)
from docx_converter import process_text

def main():
    if len(sys.argv) > 1:
        # Process command line argument
        user_input = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        print("BGN to EUR Converter - Type 'quit' to exit")
        print("-" * 40)
        while True:
            user_input = input("\nEnter amount in BGN: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if not user_input:
                continue
            process_input(user_input)
        return
    
    process_input(user_input)

def process_input(user_input):
    # First, check if there's a Bulgarian currency indicator
    # If no currency indicator, don't convert
    currency_indicators = [
        'лева', 'лев', 'лв.', 'лв', 'lv.', 'lv', 'LV', 
        'BGN', 'leva', 'lev', 'български'
    ]
    
    has_currency = any(indicator.lower() in user_input.lower() for indicator in currency_indicators)
    
    if not has_currency:
        print(f"\nInput: {user_input}")
        print(f"Output: (no Bulgarian currency detected - not converted)")
        return
    
    # Process with full DOCX pattern
    result, changes = process_text(user_input)
    
    if changes:
        print(f"\nInput: {user_input}")
        print(f"Output: {result}")
        print(f"Changes: {changes}")
        return
    
    # Try parsing as simple BGN number
    amount = parse_bulgarian_number(user_input)
    
    if amount is not None:
        eur = convert_bgn_to_eur(amount)
        words = format_eur_words(eur)
        print(f"\nInput: {user_input} BGN")
        print(f"Parsed: {amount}")
        print(f"EUR: {eur:.2f}")
        print(f"Words: {words}")
    else:
        # Try as number-to-words test
        try:
            num = int(user_input)
            words = number_to_words_bulgarian(num)
            print(f"\nNumber: {num}")
            print(f"Bulgarian words: {words}")
        except ValueError:
            print(f"Could not parse: {user_input}")

if __name__ == "__main__":
    main()