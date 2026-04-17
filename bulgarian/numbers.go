package bulgarian

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

const Rate = 1.95583

var (
	unitsBG = []string{
		"нула", "едно", "две", "три", "четири", "пет", "шест", "седем", "осем", "девет",
	}
	teensBG = []string{
		"", "едно", "две", "три", "четири", "пет", "шест", "седем", "осем", "девет",
	}
	teensTextBG = []string{
		"", "една", "две", "три", "четири", "пет", "шест", "седем", "осем", "девет",
	}
	tensBG = []string{
		"", "", "двадесет", "тридесет", "четиридесет", "петдесет", "шестдесет", "седемдесет", "осемдесет", "деветдесет",
	}
	hundredsBG = []string{
		"", "сто", "двеста", "триста", "четиристотин", "петстотин", "шестстотин", "седемстотин", "осемстотин", "деветстотин",
	}
	thousandsBG = []string{
		"", "хиляда", "две хиляди", "три хиляди", "четири хиляди", "пет хиляди", "шест хиляди", "седем хиляди", "осем хиляди", "девет хиляди",
	}
	millionsBG = []string{
		"", "един милион", "два милиона", "три милиона", "четири милиона", "пет милиона", "шест милиона", "седем милиона", "осем милиона", "девет милиона",
	}
)

type NumberParts struct {
	Whole    int64
	Cents    int64
	HasCents bool
}

func ParseBulgarianNumber(s string) (float64, error) {
	s = strings.TrimSpace(s)
	s = strings.ReplaceAll(s, "\xa0", " ")
	s = strings.ReplaceAll(s, " ", "")
	s = strings.ReplaceAll(s, ",", ".")

	if strings.HasPrefix(s, "0.") && len(s) > 2 {
		s = "." + s[2:]
	}

	if s == "" {
		return 0, fmt.Errorf("empty string")
	}

	return strconv.ParseFloat(s, 64)
}

func FormatNumberForDisplay(n float64) string {
	whole := int64(n)
	cents := int64((n - float64(whole)) * 100)

	if cents == 0 {
		return fmt.Sprintf("%d", whole)
	}
	return fmt.Sprintf("%d,%02d", whole, cents)
}

func ConvertToEUR(bgn float64) float64 {
	return bgn / Rate
}

func NumberToWordsEUR(amount float64) string {
	partsEUR := SplitToParts(ConvertToEUR(amount))

	var result strings.Builder

	if partsEUR.Whole > 0 {
		result.WriteString(intToWordsBulgarian(partsEUR.Whole))
		result.WriteString(" евро")
	}

	if partsEUR.Cents > 0 || (partsEUR.Whole == 0 && !partsEUR.HasCents) {
		if result.Len() > 0 {
			result.WriteString(" и ")
		}
		if partsEUR.Cents > 0 {
			result.WriteString(intToWordsBulgarian(partsEUR.Cents))
		} else {
			result.WriteString("нула")
		}
		if partsEUR.Cents == 1 {
			result.WriteString(" евроцент")
		} else {
			result.WriteString(" евроцента")
		}
	}

	return result.String()
}

func intToWordsBulgarian(n int64) string {
	if n == 0 {
		return "нула"
	}

	var result strings.Builder

	millions := n / 1_000_000
	thousands := (n / 1000) % 1000
	hundreds := (n / 100) % 10
	tens := (n / 10) % 10
	units := n % 10

	if millions > 0 {
		result.WriteString(millionsToWordsBG(millions))
		if thousands > 0 || hundreds > 0 || tens > 0 || units > 0 {
			result.WriteString(" ")
		}
	}

	if thousands > 0 {
		result.WriteString(thousandsToWordsBG(thousands))
		if hundreds > 0 || tens > 0 || units > 0 {
			result.WriteString(" ")
		}
	}

	if hundreds > 0 {
		result.WriteString(hundredsBG[hundreds])
		if tens > 0 || units > 0 {
			result.WriteString(" ")
		}
	}

	if tens > 0 {
		if tens == 1 && units > 0 {
			result.WriteString(teensBG[units])
		} else {
			result.WriteString(tensBG[tens])
			if units > 0 {
				result.WriteString(" и ")
				result.WriteString(unitsBG[units])
			}
		}
	} else if units > 0 {
		result.WriteString(unitsBG[units])
	}

	return result.String()
}

func millionsToWordsBG(n int64) string {
	if n == 0 {
		return ""
	}

	var result strings.Builder

	millions := n / 1000
	remainder := n % 1000

	if millions > 0 {
		result.WriteString(millionsToWordsBG(millions))
		result.WriteString(" ")
	}

	if remainder > 0 {
		result.WriteString(threeDigitToWordsBG(remainder))
		result.WriteString(" милиона")
	} else {
		result.WriteString(millionsBG[int(n%10)])
		if n%10 != 1 || (n/10)%10 != 0 || (n/100)%10 != 0 {
			result.WriteString("а")
		}
	}

	return result.String()
}

func thousandsToWordsBG(n int64) string {
	if n == 0 {
		return ""
	}

	var result strings.Builder

	thousands := n / 1000
	remainder := n % 1000

	if thousands > 0 {
		result.WriteString(thousandsToWordsBG(thousands))
		result.WriteString(" ")
	}

	if remainder > 0 {
		result.WriteString(threeDigitToWordsBG(remainder))
		result.WriteString(" хиляди")
	} else {
		if n == 1 {
			result.WriteString("хиляда")
		} else {
			result.WriteString(thousandsBG[int(n%10)])
		}
	}

	return result.String()
}

func threeDigitToWordsBG(n int64) string {
	if n == 0 {
		return ""
	}

	var result strings.Builder

	hundreds := n / 100
	tens := (n / 10) % 10
	units := n % 10

	if hundreds > 0 {
		result.WriteString(hundredsBG[hundreds])
		if tens > 0 || units > 0 {
			result.WriteString(" ")
		}
	}

	if tens > 0 {
		if tens == 1 && units > 0 {
			if units == 1 {
				result.WriteString("една")
			} else if units == 2 {
				result.WriteString("две")
			} else {
				result.WriteString(teensTextBG[units])
			}
			result.WriteString("на")
		} else {
			result.WriteString(tensBG[tens])
			if units > 0 {
				result.WriteString(" и ")
				result.WriteString(unitsBG[units])
			}
		}
	} else if units > 0 {
		if units == 1 {
			result.WriteString("една")
		} else if units == 2 {
			result.WriteString("две")
		} else {
			result.WriteString(unitsBG[units])
		}
	}

	return result.String()
}

func SplitToParts(amount float64) NumberParts {
	whole := int64(amount)
	cents := int64((amount - float64(whole)) * 100)

	return NumberParts{
		Whole:    whole,
		Cents:    cents,
		HasCents: cents != 0 || (amount > 0 && amount < 1),
	}
}

var (
	bgNumberPattern = regexp.MustCompile(`(\d[\d\s]*(?:[,.]?\d+)?)`)
)

func FindNumberInText(text string) string {
	matches := bgNumberPattern.FindStringSubmatch(text)
	if len(matches) > 1 {
		return matches[1]
	}
	return ""
}