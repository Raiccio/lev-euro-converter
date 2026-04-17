package gui

import (
	"fmt"
	"path/filepath"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"

	"github.com/raiccio/lev-euro-converter/converter"
)

func Run() {
	a := app.NewWithID("lev-euro-converter")
	a.SetTheme(theme.DarkTheme())

	w := a.NewWindow("lev-euro-converter")
	w.SetMinSize(fyne.NewSize(550, 450))
	w.CenterOnScreen()

	mainUI(a, w)
	w.ShowAndRun()
}

func mainUI(a fyne.App, w fyne.Window) {
	files := []string{}
	outputFiles := []string{}

	title := widget.NewLabelWithStyle(
		"lev-euro-converter",
		fyne.TextAlignCenter,
		fyne.TextStyle{Bold: true, Size: 28},
	)

	subtitle := widget.NewLabelWithStyle(
		"Конвертиране на DOCX документи от лева в евро",
		fyne.TextAlignCenter,
		fyne.TextStyle{Size: 14, Color: fyne.ColorHex("#888888")},
	)

	rateLabel := widget.NewLabel("📊 1 EUR = 1.95583 BGN")
	rateLabel.Alignment = fyne.TextAlignCenter

	fileList := widget.NewList(
		func() int { return len(files) },
		func() fyne.CanvasObject {
			return widget.NewLabel("")
		},
		func(id widget.ListItemID, obj fyne.CanvasObject) {
			obj.(*widget.Label).SetText(files[id])
			obj.(*widget.Label).TextStyle = fyne.TextStyle{Monospace: true, Size: 12}
		},
	)

	outputList := widget.NewList(
		func() int { return len(outputFiles) },
		func() fyne.CanvasObject {
			return widget.NewLabel("")
		},
		func(id widget.ListItemID, obj fyne.CanvasObject) {
			obj.(*widget.Label).SetText(outputFiles[id])
			obj.(*widget.Label).TextStyle = fyne.TextStyle{Monospace: true, Size: 12}
		},
	)

	status := widget.NewLabel("Готово")
	status.Alignment = fyne.TextAlignCenter

	selectBtn := widget.NewButtonWithIcon("Избери файлове", theme.FileIcon(), func() {
		dialog.ShowOpenMultiFileDialog(w, func(filesRead []fyne.URI) {
			if len(filesRead) == 0 {
				return
			}
			files = []string{}
			outputFiles = []string{}
			for _, uri := range filesRead {
				path := uri.Path()
				if strings.HasSuffix(strings.ToLower(path), ".docx") {
					files = append(files, path)
				}
			}
			fileList.Refresh()
			outputList.Refresh()
			status.SetText(fmt.Sprintf("Избрани: %d файла", len(files)))
		})
	})

	clearBtn := widget.NewButtonWithIcon("Изчисти", theme.CancelIcon(), func() {
		files = []string{}
		outputFiles = []string{}
		fileList.Refresh()
		outputList.Refresh()
		status.SetText("Готово")
	})

	convertBtn := widget.NewButtonWithIcon("Конвертирай", theme.MediaPlayIcon(), func() {
		if len(files) == 0 {
			status.SetText("Моля, изберете файлове първо")
			return
		}

		status.SetText("Конвертиране...")
		success := 0
		errors := 0
		outputFiles = []string{}

		for _, f := range files {
			outputPath := getOutputPath(f)
			err := converter.ConvertDOCX(f, outputPath)
			if err != nil {
				status.SetText(fmt.Sprintf("Грешка: %v", err))
				errors++
				continue
			}
			outputFiles = append(outputFiles, outputPath)
			success++
		}

		outputList.Refresh()

		if errors == 0 {
			status.SetText(fmt.Sprintf("✓ Готово: %d файла", success))
		} else {
			status.SetText(fmt.Sprintf("Конвертирани: %d, Грешки: %d", success, errors))
		}
	})
	convertBtn.Importance = widget.HighImportance

	openOutputBtn := widget.NewButton("Отвори изходна папка", func() {
		if len(outputFiles) > 0 {
			dir := filepath.Dir(outputFiles[0])
			a.OpenURL("file:///" + dir)
		}
	})

	versionLabel := widget.NewLabelWithStyle(
		"v1.0.0",
		fyne.TextAlignCenter,
		fyne.TextStyle{Size: 11, Color: fyne.ColorHex("#666666")},
	)

	scrollContainer := container.NewVScroll(fileList)
	scrollContainer.SetMinSize(fyne.NewSize(400, 100))

	outputScrollContainer := container.NewVScroll(outputList)
	outputScrollContainer.SetMinSize(fyne.NewSize(400, 100))

	content := container.NewVBox(
		layout.NewSpacer(),
		title,
		subtitle,
		layout.NewSpacer(),
		container.NewHBox(
			selectBtn,
			clearBtn,
		),
		layout.NewSpacer(),
		widget.NewLabelWithStyle("Входни файлове:", fyne.TextAlignLeading, fyne.TextStyle{Bold: true, Size: 14}),
		scrollContainer,
		layout.NewSpacer(),
		rateLabel,
		layout.NewSpacer(),
		convertBtn,
		layout.NewSpacer(),
		widget.NewLabelWithStyle("Изходни файлове:", fyne.TextAlignLeading, fyne.TextStyle{Bold: true, Size: 14}),
		outputScrollContainer,
		layout.NewSpacer(),
		openOutputBtn,
		layout.NewSpacer(),
		status,
		versionLabel,
		layout.NewSpacer(),
	)

	content.Padding = layout.NewInset(20)
	content.Layout = layout.NewVBoxLayout()
	w.SetContent(content)
}

func getOutputPath(input string) string {
	dir := filepath.Dir(input)
	ext := filepath.Ext(input)
	name := strings.TrimSuffix(filepath.Base(input), ext)
	return filepath.Join(dir, name+"_eur"+ext)
}