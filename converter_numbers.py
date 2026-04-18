# Bulgarian Numbers Dictionary - Fixed and Proper

RATE = 1.95583

# Number to words lookup
NUMBERS = {
    # Units
    0: "нула",
    1: "едно",
    2: "две", 
    3: "три",
    4: "четири",
    5: "пет",
    6: "шест",
    7: "седем",
    8: "осем",
    9: "девет",
    
    # Teens
    10: "десет",
    11: "единадесет",
    12: "дванадесет",
    13: "тринадесет",
    14: "четиринадесет",
    15: "петнадесет",
    16: "шестнадесет",
    17: "седемнадесет",
    18: "осемнадесет",
    19: "деветнадесет",
    
    # Tens
    20: "двадесет",
    30: "тридесет",
    40: "четиридесет",
    50: "петдесет",
    60: "шестдесет",
    70: "седемдесет",
    80: "осемдесет",
    90: "деветдесет",
    
    # Hundreds
    100: "сто",
    200: "двеста",
    300: "триста",
    400: "четиристотин",
    500: "петстотин",
    600: "шестстотин",
    700: "седемстотин",
    800: "осемстотин",
    900: "деветстотин",
}


def number_to_words_bulgarian(n):
    """Convert integer to Bulgarian words"""
    if n == 0:
        return "нула"
    
    result = []
    remaining = n
    
    # Helper to process a triple (hundreds/tens/ones) with и logic
    def process_triple(val):
        if val == 0:
            return []
        
        parts = []
        hundreds = val // 100
        rest = val % 100
        
        # Hundreds
        if hundreds > 0:
            parts.append(NUMBERS.get(hundreds * 100, str(hundreds)))
        
        # If there's anything left (tens or ones)
        if rest > 0:
            if rest < 20:
                # Teens (11-19): single word
                if hundreds > 0:
                    parts.append("и")
                parts.append(NUMBERS.get(rest, str(rest)))
            else:
                # 20-99
                tens = (rest // 10) * 10
                ones = rest % 10
                
                if hundreds > 0:
                    # Already have hundreds
                    if ones > 0:
                        # tens AND ones: output tens, then "и", then ones
                        parts.append(NUMBERS.get(tens, str(tens)))
                        parts.append("и")
                        parts.append(NUMBERS.get(ones, str(ones)))
                    else:
                        # Only tens, no ones: "и" ONLY if tens == 10 (not 20, 30, etc)
                        if tens == 10:
                            parts.append("и")
                        parts.append(NUMBERS.get(tens, str(tens)))
                else:
                    # No hundreds: tens + "и" + ones if ones > 0
                    parts.append(NUMBERS.get(tens, str(tens)))
                    if ones > 0:
                        parts.append("и")
                        parts.append(NUMBERS.get(ones, str(ones)))
        
        return parts
    
    # Millions
    millions = remaining // 1000000
    if millions > 0:
        rest = remaining % 1000000
        has_hundreds = rest >= 100
        is_simple_tens = rest in (10, 20, 30, 40, 50, 60, 70, 80, 90)
        has_simple_ones = 0 < rest < 10
        has_thousands = rest >= 1000
        
        # For millions, use "един" (not "едно") for 1
        if millions == 1:
            result.append("един")
            result.append("милион")
        elif millions == 2:
            result.append("два")
            result.append("милиона")
        else:
            result.extend(process_triple(millions))
            result.append("милиона")
        
        # "и" if there's anything after millions
        if has_hundreds or is_simple_tens or has_simple_ones or has_thousands:
            result.append("и")
        
        remaining = remaining % 1000000
    
    # Thousands
    thousands = remaining // 1000
    if thousands > 0:
        rest = remaining % 1000
        has_hundreds = rest >= 100
        is_simple_tens = rest in (10, 20, 30, 40, 50, 60, 70, 80, 90)
        has_simple_ones = 0 < rest < 10
        
        if thousands == 1:
            result.append("хиляда")
        elif thousands == 2:
            result.append("две")
            result.append("хиляди")
        else:
            result.extend(process_triple(thousands))
            result.append("хиляди")
        
        # "и" if hundreds or simple round tens or simple ones
        if has_hundreds or is_simple_tens or has_simple_ones:
            result.append("и")
        
        remaining = remaining % 1000
    
    # Hundreds (0-999)
    result.extend(process_triple(remaining))
    
    return " ".join(result)


# Word to number mapping
WORD_TO_NUMBER = {
    "нула": 0,
    "едно": 1,
    "една": 1,
    "две": 2,
    "два": 2,
    "три": 3,
    "четири": 4,
    "пет": 5,
    "шест": 6,
    "седем": 7,
    "осем": 8,
    "девет": 9,
    "десет": 10,
    "единадесет": 11,
    "дванадесет": 12,
    "тринадесет": 13,
    "четиринадесет": 14,
    "петнадесет": 15,
    "шестнадесет": 16,
    "седемнадесет": 17,
    "осемнадесет": 18,
    "деветнадесет": 19,
    "двадесет": 20,
    "тридесет": 30,
    "четиридесет": 40,
    "петдесет": 50,
    "шестдесет": 60,
    "седемдесет": 70,
    "осемдесет": 80,
    "деветдесет": 90,
    "сто": 100,
    "двеста": 200,
    "триста": 300,
    "четиристотин": 400,
    "петстотин": 500,
    "шестстотин": 600,
    "седемстотин": 700,
    "осемстотин": 800,
    "деветстотин": 900,
    "хиляда": 1000,
    "една хиляда": 1000,
    "две хиляди": 2000,
    "три хиляди": 3000,
    "четири хиляди": 4000,
    "пет хиляди": 5000,
    "шест хиляди": 6000,
    "седем хиляди": 7000,
    "осем хиляди": 8000,
    "девет хиляди": 9000,
    "милион": 1000000,
    "два милиона": 2000000,
}


def word_to_number(word):
    """Convert Bulgarian word to number"""
    word_lower = word.lower().strip()
    
    # Direct lookup
    if word_lower in WORD_TO_NUMBER:
        return WORD_TO_NUMBER[word_lower]
    
    # Try compound: "двадесет и пет" = 25
    if " и " in word_lower:
        parts = word_lower.split(" и ")
        total = 0
        for part in parts:
            part = part.strip()
            if part in WORD_TO_NUMBER:
                total += WORD_TO_NUMBER[part]
        if total > 0:
            return total
    
    # Try: "двадесет и пет" format
    if " и " in word_lower:
        parts = word_lower.split(" и ")
        total = 0
        for p in parts:
            p = p.strip()
            if p in WORD_TO_NUMBER:
                total += WORD_TO_NUMBER[p]
        return total if total > 0 else None
    
    return None


def convert_bgn_to_eur(amount_bgn):
    """Convert BGN to EUR"""
    return amount_bgn / RATE


def format_eur_words(amount_eur):
    """Format EUR amount as Bulgarian words"""
    # Round to 2 decimal places first
    amount_eur = round(amount_eur, 2)
    euros = int(amount_eur)
    cents = int(round((amount_eur - euros) * 100))
    
    # Handle rounding up (e.g., 0.997 -> 1.00)
    if cents >= 100:
        euros += 1
        cents = 0
    
    if euros == 0 and cents == 0:
        return "нула евро"
    
    parts = []
    
    if euros > 0:
        parts.append(number_to_words_bulgarian(euros))
        parts.append("евро")
    
    if cents > 0:
        if euros > 0:
            parts.append("и")
        parts.append(number_to_words_bulgarian(cents))
        if cents == 1:
            parts.append("евроцент")
        else:
            parts.append("евроцента")
    
    return " ".join(parts)


def parse_bulgarian_number(s):
    """Parse Bulgarian number string"""
    s = str(s).strip()
    
    # Clean up
    s = s.replace('\xa0', ' ')
    s = s.replace('\u00a0', ' ')
    s = s.replace(' ', '')
    s = s.replace(',', '.')
    
    try:
        return float(s)
    except ValueError:
        return None