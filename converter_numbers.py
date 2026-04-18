"""
Bulgarian number to words conversion for EUR
"""

RATE = 1.95583

UNITS = ["нула", "едно", "две", "три", "четири", "пет", "шест", "седем", "осем", "девет"]
TEENS = ["", "едно", "две", "три", "четири", "пет", "шест", "седем", "осем", "девет"]
TENS = ["", "", "двадесет", "тридесет", "четиридесет", "петдесет", "шестдесет", "седемдесет", "осемдесет", "деветдесет"]
HUNDREDS = ["", "сто", "двеста", "триста", "четиристотин", "петстотин", "шестстотин", "седемстотин", "осемстотин", "деветстотин"]
THOUSANDS = ["", "хиляда", "две хиляди", "три хиляди", "четири хиляди", "пет хиляди", "шест хиляди", "седем хиляди", "осем хиляди", "девет хиляди"]


def number_to_words_bulgarian(n):
    """Convert integer to Bulgarian words - returns numeric value if word not found"""
    if n == 0:
        return "нула"
    
    result = []
    
    # Handle millions
    millions = n // 1_000_000
    if millions > 0:
        result.append(_three_digit_to_words(millions))
        if millions > 1:
            result.append("милиона")
        else:
            result.append("един милион")
        n = n % 1_000_000
    
    # Handle thousands
    thousands = n // 1_000
    if thousands > 0:
        result.append(_three_digit_to_words(thousands))
        if thousands > 1:
            result.append("хиляди")
        else:
            result.append("хиляда")
        n = n % 1_000
    
    # Handle hundreds
    if n > 0:
        result.append(_three_digit_to_words(n))
    
    return " ".join(result)


def _three_digit_to_words(n):
    """Convert 0-999 to Bulgarian words"""
    if n == 0:
        return ""
    
    result = []
    
    # Hundreds
    hundreds = n // 100
    if hundreds > 0:
        result.append(HUNDREDS[hundreds])
        n = n % 100
    
    # Tens and units
    if n > 0:
        if n < 10:
            result.append(UNITS[n])
        elif n < 20:
            tens_digit = n - 10
            teen_words = ["единадесет", "дванадесет", "тринадесет", "четиринадесет", "петнадесет", 
                     "шестнадесет", "седемнадесет", "осемнадесет", "деветнадесет"]
            result.append(teen_words[tens_digit])
        else:
            tens = n // 10
            units = n % 10
            result.append(TENS[tens])
            if units > 0:
                result.append(UNITS[units])
    
    return " ".join(result)


def convert_bgn_to_eur(amount_bgn):
    """Convert BGN amount to EUR"""
    return amount_bgn / RATE


def format_eur_words(amount_eur):
    """Format EUR amount as Bulgarian words"""
    # Round to 2 decimal places
    cents = int(round((amount_eur - int(amount_eur)) * 100))
    euros = int(amount_eur)
    
    if euros == 0 and cents == 0:
        return "нула евро"
    
    parts = []
    
    if euros > 0:
        parts.append(number_to_words_bulgarian(euros))
        parts.append("евро")
    
    if cents > 0:
        if cents == 1:
            parts.append("един евроцент")
        else:
            parts.append(f"{number_to_words_bulgarian(cents)} евроцента")
    
    return " ".join(parts)


def parse_bulgarian_number(s):
    """Parse a Bulgarian formatted number string"""
    s = str(s).strip()
    # Remove spaces, handle non-breaking space
    s = s.replace(" ", "").replace("\xa0", "").replace(",", ".")
    
    try:
        return float(s)
    except ValueError:
        return None


def number_word_to_value(word):
    """Convert Bulgarian word to number - returns None if not found"""
    word = word.lower().strip()
    
    # Simple mapping for common words
    word_map = {
        "нула": 0, "едно": 1, "една": 1, "две": 2, "три": 3, "четири": 4,
        "пет": 5, "шест": 6, "седем": 7, "осем": 8, "девет": 9,
        "десет": 10, "единадесет": 11, "дванадесет": 12, "тринадесет": 13,
        "четиринадесет": 14, "петнадесет": 15, "шестнадесет": 16,
        "седемнадесет": 17, "осемнадесет": 18, "деветнадесет": 19,
        "двадесет": 20, "тридесет": 30, "четиридесет": 40, "петдесет": 50,
        "шестдесет": 60, "седемдесет": 70, "осемдесет": 80, "деветдесет": 90,
        "сто": 100, "двеста": 200, "триста": 300, "четиристотин": 400,
        "петстотин": 500, "шестстотин": 600, "седемстотин": 700,
        "осемстотин": 800, "деветстотин": 900,
        "хиляда": 1000, "две хиляди": 2000, "три хиляди": 3000,
        "четири хиляди": 4000, "пет хиляди": 5000,
    }
    
    return word_map.get(word)


def word_to_number(word):
    """Convert Bulgarian word to number value - returns 0 if not found"""
    val = number_word_to_value(word)
    if val is not None:
        return val
    
    # Try compound numbers (e.g., "двадесет и пет" = 25)
    parts = word.split()
    total = 0
    for part in parts:
        part_val = number_word_to_value(part)
        if part_val:
            total += part_val
    
    return total if total > 0 else None