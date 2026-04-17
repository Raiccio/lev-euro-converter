package converter

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/raiccio/lev-euro-converter/bulgarian"
)

const Rate = 1.95583

type ConversionResult struct {
	File   string
	Output string
	Error  error
}

func ConvertFile(inputPath string) (*ConversionResult, error) {
	outputPath := generateOutputPath(inputPath)

	if err := convertDOCX(inputPath, outputPath); err != nil {
		return &ConversionResult{
			File:   inputPath,
			Output: outputPath,
			Error:  err,
		}, err
	}

	return &ConversionResult{
		File:   inputPath,
		Output: outputPath,
		Error:  nil,
	}, nil
}

func ConvertDOCX(inputPath, outputPath string) error {
	return convertDOCX(inputPath, outputPath)
}

func generateOutputPath(inputPath string) string {
	dir := filepath.Dir(inputPath)
	ext := filepath.Ext(inputPath)
	name := strings.TrimSuffix(filepath.Base(inputPath), ext)
	return filepath.Join(dir, name+"_eur"+ext)
}

func convertDOCX(inputPath, outputPath string) error {
	inputFile, err := os.Open(inputPath)
	if err != nil {
		return fmt.Errorf("failed to open input file: %w", err)
	}
	defer inputFile.Close()

	zipReader, err := zip.NewReader(inputFile, 0)
	if err != nil {
		return fmt.Errorf("failed to read docx as zip: %w", err)
	}

	var buf bytes.Buffer
	zipWriter := zip.NewWriter(&buf)

	for _, file := range zipReader.File {
		zipEntry, err := zipWriter.Create(file.Name)
		if err != nil {
			return fmt.Errorf("failed to create zip entry: %w", err)
		}

		entryReader, err := file.Open()
		if err != nil {
			return fmt.Errorf("failed to open zip entry: %w", err)
		}

		content, err := io.ReadAll(entryReader)
		entryReader.Close()
		if err != nil {
			return fmt.Errorf("failed to read entry content: %w", err)
		}

		if file.Name == "word/document.xml" {
			content = []byte(processDocumentXML(string(content)))
		}

		if _, err := zipEntry.Write(content); err != nil {
			return fmt.Errorf("failed to write entry content: %w", err)
		}
	}

	if err := zipWriter.Close(); err != nil {
		return fmt.Errorf("failed to finalize zip: %w", err)
	}

	outputFile, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("failed to create output file: %w", err)
	}
	defer outputFile.Close()

	if _, err := buf.WriteTo(outputFile); err != nil {
		return fmt.Errorf("failed to write output: %w", err)
	}

	return nil
}

func processDocumentXML(content string) string {
	content = processBGNAmounts(content)
	content = processBGNCurrencyWords(content)
	content = processSlashBracketPatterns(content)
	return content
}

var (
	currencySymbols = []string{"лв.", "лв", "лева", "lv", "LV"}
	centWords        = []string{"стотинки", "ст."}

	replacementPatterns = []*regexp.Regexp{
		regexp.MustCompile(`(\d{1,3}(?:\s?\d{3})*(?:[.,]\d+)?)\s*(лв\.|лв|лева|lv|LV)`),
		regexp.MustCompile(`(\d{1,3}(?:\s?\d{3})*(?:[.,]\d+)?)\s*(стотинки|ст\.)`),
	}

	slashBracketPattern = regexp.MustCompile(`(\d[\d\s]*(?:[.,]\d+)?)\s*(/\([^)]+\)/|\([^)]+\)|/[\p{Lu}\p{Ll}\s]+/)`)
)

func processBGNAmounts(content string) string {
	for _, pattern := range replacementPatterns {
		content = pattern.ReplaceAllStringFunc(content, func(match string) string {
			parts := pattern.FindStringSubmatch(match)
			if len(parts) < 3 {
				return match
			}

			numberStr := parts[1]
			currency := parts[2]

			num, err := bulgarian.ParseBulgarianNumber(numberStr)
			if err != nil {
				return match
			}

			eurAmount := bulgarian.ConvertToEUR(num)

			if currency == "стотинки" || currency == "ст." {
				return fmt.Sprintf("%.2f евроцента", eurAmount)
			}

			return fmt.Sprintf("%.2f евро", eurAmount)
		})
	}
	return content
}

func processBGNCurrencyWords(content string) string {
	wordPatterns := []*regexp.Regexp{
		regexp.MustCompile(`(\p{Ll}+)\s+(лева)`),
		regexp.MustCompile(`(\p{Ll}+)\s+(стотинки)`),
		regexp.MustCompile(`(\p{Ll}+)\s+(lv)`),
		regexp.MustCompile(`(\p{Lu}+)\s+(ЛЕВА)`),
	}

	for _, pattern := range wordPatterns {
		content = pattern.ReplaceAllStringFunc(content, func(match string) string {
			parts := pattern.FindStringSubmatch(match)
			if len(parts) < 3 {
				return match
			}

			numberWord := parts[1]
			currency := parts[2]

			num := wordToNumberBG(numberWord)
			if num == 0 {
				return match
			}

			eurAmount := bulgarian.ConvertToEUR(float64(num))

			if currency == "стотинки" {
				return bulgarian.NumberToWordsEUR(float64(num))
			}

			return bulgarian.NumberToWordsEUR(eurAmount)
		})
	}
	return content
}

func processSlashBracketPatterns(content string) string {
	content = slashBracketPattern.ReplaceAllStringFunc(content, func(match string) string {
		parts := slashBracketPattern.FindStringSubmatch(match)
		if len(parts) < 3 {
			return match
		}

		numberStr := parts[1]
		bracketPart := parts[2]

		num, err := bulgarian.ParseBulgarianNumber(numberStr)
		if err != nil {
			return match
		}

		eurAmount := bulgarian.ConvertToEUR(num)
		eurWords := bulgarian.NumberToWordsEUR(eurAmount)

		var prefix string
		var suffix string

		if strings.HasPrefix(bracketPart, "(") && strings.HasSuffix(bracketPart, ")") {
			prefix = "("
			suffix = ")"
		} else if strings.HasPrefix(bracketPart, "/") && strings.HasSuffix(bracketPart, "/") {
			prefix = "/"
			suffix = "/"
		} else {
			return match
		}

		cleanWord := strings.Trim(bracketPart, "()/ ")
		wordNum := wordToNumberBG(cleanWord)
		var eurWordsInput string

		if wordNum > 0 {
			eurInputAmount := bulgarian.ConvertToEUR(float64(wordNum))
			eurWordsInput = bulgarian.NumberToWordsEUR(eurInputAmount)
		}

		if eurWordsInput != "" {
			return fmt.Sprintf("%.2f %s%s%s", num, prefix, eurWordsInput, suffix)
		}

		return fmt.Sprintf("%.2f %s%s%s", num, prefix, eurWords, suffix)
	})

	return content
}

var (
	bgWordNumbers = map[string]int64{
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
)

func wordToNumberBG(word string) int64 {
	if val, ok := bgWordNumbers[word]; ok {
		return val
	}
	return 0
}