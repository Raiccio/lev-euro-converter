package gui

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"

	"github.com/raiccio/lev-euro-converter/converter"
)

func Run() {
	a := app.New()
	w := a.NewWindow("lev-euro-converter")
	w.Resize(fyne.NewSize(550, 500))
	w.CenterOnScreen()

	files := []string{}
	outputFiles := []string{}

	title := widget.NewLabel("lev-euro-converter")
	title.Alignment = fyne.TextAlignCenter

	subtitle := widget.NewLabel("Конвертиране на DOCX от лева в евро")
	subtitle.Alignment = fyne.TextAlignCenter

	rateLabel := widget.NewLabel("1 EUR = 1.95583 BGN")

	fileList := widget.NewList(
		func() int { return len(files) },
		func() fyne.CanvasObject {
			return widget.NewLabel("")
		},
		func(id widget.ListItemID, obj fyne.CanvasObject) {
			obj.(*widget.Label).SetText(files[id])
		},
	)

	outputList := widget.NewList(
		func() int { return len(outputFiles) },
		func() fyne.CanvasObject {
			return widget.NewLabel("")
		},
		func(id widget.ListItemID, obj fyne.CanvasObject) {
			obj.(*widget.Label).SetText(outputFiles[id])
		},
	)

	status := widget.NewLabel("Готово")
	status.Alignment = fyne.TextAlignCenter

	selectBtn := widget.NewButton("Избери файлове", func() {
		dialog.ShowFileOpen(func(f fyne.URIReadCloser, err error) {
			if f == nil || err != nil {
				return
			}
			defer f.Close()

			dir := filepath.Dir(f.URI().Path())
			entries, _ := os.ReadDir(dir)
			files = []string{}
			outputFiles = []string{}

			for _, entry := range entries {
				name := entry.Name()
				if strings.HasSuffix(strings.ToLower(name), ".docx") && !strings.HasSuffix(name, "_eur.docx") {
					files = append(files, filepath.Join(dir, name))
				}
			}

			fileList.Refresh()
			outputList.Refresh()
			status.SetText(fmt.Sprintf("Избрани: %d файла", len(files)))
		}, w)
	})

	clearBtn := widget.NewButton("Изчисти", func() {
		files = []string{}
		outputFiles = []string{}
		fileList.Refresh()
		outputList.Refresh()
		status.SetText("Готово")
	})

	convertBtn := widget.NewButton("Конвертирай", func() {
		if len(files) == 0 {
			status.SetText("Няма избрани файлове")
			return
		}

		status.SetText("Конвертиране...")
		success := 0
		errors := 0
		outputFiles = []string{}

		for _, f := range files {
			outPath := getOutputPath(f)
			err := converter.ConvertDOCX(f, outPath)
			if err != nil {
				status.SetText(fmt.Sprintf("Грешка: %v", err))
				errors++
				continue
			}
			outputFiles = append(outputFiles, outPath)
			success++
		}

		outputList.Refresh()

		if errors == 0 {
			status.SetText(fmt.Sprintf("Готово: %d файла", success))
		} else {
			status.SetText(fmt.Sprintf("Успешни: %d, Грешки: %d", success, errors))
		}
	})
	convertBtn.Importance = widget.HighImportance

	versionLabel := widget.NewLabel("v1.0.0")

	scrollIn := container.NewVScroll(fileList)
	scrollIn.SetMinSize(fyne.NewSize(500, 100))

	scrollOut := container.NewVScroll(outputList)
	scrollOut.SetMinSize(fyne.NewSize(500, 100))

	content := container.NewVBox(
		title,
		subtitle,
		rateLabel,
		container.NewHBox(selectBtn, clearBtn),
		widget.NewLabel("Входни файлове:"),
		scrollIn,
		convertBtn,
		widget.NewLabel("Изходни файлове:"),
		scrollOut,
		status,
		versionLabel,
	)

	w.SetContent(content)
	w.ShowAndRun()
}

func getOutputPath(input string) string {
	dir := filepath.Dir(input)
	ext := filepath.Ext(input)
	name := strings.TrimSuffix(filepath.Base(input), ext)
	return filepath.Join(dir, name+"_eur"+ext)
}