package gui

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"

	"github.com/raiccio/lev-euro-converter/converter"
)

var appInstance fyne.App

func Run() {
	appInstance = app.New()
	w := appInstance.NewWindow("lev-euro-converter")
	w.Resize(fyne.NewSize(650, 650))
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

	status := widget.NewLabel("Избери папка с DOCX файлове")
	status.Alignment = fyne.TextAlignCenter

	selectBtn := widget.NewButton("Избери папка", func() {
		dialog.ShowFolderOpen(func(dir fyne.ListableURI, err error) {
			if dir == nil || err != nil {
				status.SetText("Грешка при избора на папка")
				return
			}

			dirPath := dir.Path()
			entries, err := os.ReadDir(dirPath)
			if err != nil {
				status.SetText(fmt.Sprintf("Грешка: %v", err))
				return
			}

			files = []string{}
			outputFiles = []string{}

			for _, entry := range entries {
				name := entry.Name()
				if !entry.IsDir() && strings.HasSuffix(strings.ToLower(name), ".docx") && !strings.HasSuffix(name, "_eur.docx") {
					files = append(files, filepath.Join(dirPath, name))
				}
			}

			fileList.Refresh()
			outputList.Refresh()

			if len(files) == 0 {
				status.SetText("Няма DOCX файлове в папката")
			} else {
				status.SetText(fmt.Sprintf("Избрани: %d файла", len(files)))
			}
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

	openBtn := widget.NewButton("Отвори папка", func() {
		if len(outputFiles) > 0 {
			dir := filepath.Dir(outputFiles[0])
			openExplorer(dir)
		} else if len(files) > 0 {
			dir := filepath.Dir(files[0])
			openExplorer(dir)
		} else {
			status.SetText("Няма файлове")
		}
	})

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
		openBtn,
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

func openExplorer(path string) error {
	cmd := exec.Command("explorer", path)
	return cmd.Start()
}
