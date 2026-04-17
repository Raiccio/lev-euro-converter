package gui

import (
	"fmt"
	"html/template"
	"io"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"github.com/raiccio/lev-euro-converter/converter"
)

var htmlTemplate = template.Must(template.New("").Parse(`<!DOCTYPE html>
<html lang="bg">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>lev-euro-converter</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }
        h1 {
            text-align: center;
            color: #1a1a2e;
            margin-bottom: 8px;
            font-size: 28px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .drop-zone {
            border: 2px dashed #ccc;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        .drop-zone:hover, .drop-zone.dragover {
            border-color: #4f46e5;
            background: #f8f8ff;
        }
        .drop-zone input {
            display: none;
        }
        .drop-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        .file-list {
            background: #f8f8f8;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: white;
            border-radius: 6px;
            margin-bottom: 6px;
            font-size: 13px;
        }
        .file-item:last-child { margin-bottom: 0; }
        .file-name { color: #333; word-break: break-all; }
        .file-remove {
            color: #ef4444;
            cursor: pointer;
            padding: 0 8px;
            font-weight: bold;
        }
        .rate-box {
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            margin-bottom: 20px;
            color: #0369a1;
        }
        .convert-btn {
            width: 100%;
            padding: 14px;
            background: #4f46e5;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .convert-btn:hover:not(:disabled) { background: #4338ca; }
        .convert-btn:disabled { background: #ccc; cursor: not-allowed; }
        .status {
            margin-top: 20px;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }
        .statusready { background: #f0fdf4; color: #166534; }
        .statusprocessing { background: #fef3c7; color: #92400e; }
        .statussuccess { background: #f0fdf4; color: #166534; }
        .statuserror { background: #fef2f2; color: #991b1b; }
        .version {
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 11px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>lev-euro-converter</h1>
        <p class="subtitle">Конвертиране на DOCX документи от лева в евро</p>
        
        <div class="drop-zone" id="dropZone">
            <div class="drop-icon">📄</div>
            <div>Кликни за да избереш файлове</div>
            <div style="font-size: 12px; color: #999; margin-top: 4px;">или пусни файлове тук</div>
            <input type="file" id="fileInput" multiple accept=".docx">
        </div>
        
        <div class="file-list" id="fileList" style="display:none">
            <div id="filesContainer"></div>
        </div>
        
        <div class="rate-box">
            📊 1 EUR = 1.95583 BGN
        </div>
        
        <button class="convert-btn" id="convertBtn" disabled>Конвертирай</button>
        
        <div class="status" id="status">Готово</div>
        
        <div class="version">v1.0.0</div>
    </div>

    <script>
        let files = [];
        
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const filesContainer = document.getElementById('filesContainer');
        const convertBtn = document.getElementById('convertBtn');
        const status = document.getElementById('status');
        
        dropZone.addEventListener('click', () => fileInput.click());
        
        fileInput.addEventListener('change', (e) => {
            addFiles(Array.from(e.target.files));
        });
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            addFiles(Array.from(e.dataTransfer.files));
        });
        
        function addFiles(newFiles) {
            newFiles.forEach(f => {
                if (f.name.toLowerCase().endsWith('.docx')) {
                    const exists = files.some(ef => ef.name === f.name && ef.path === f.path);
                    if (!exists) {
                        files.push(f);
                    }
                }
            });
            renderFiles();
        }
        
        function renderFiles() {
            if (files.length === 0) {
                fileList.style.display = 'none';
                convertBtn.disabled = true;
            } else {
                fileList.style.display = 'block';
                convertBtn.disabled = false;
                filesContainer.innerHTML = files.map((f, i) => 
                    '<div class="file-item"><span class="file-name">' + f.name + 
                    '</span><span class="file-remove" onclick="removeFile(' + i + ')">×</span></div>'
                ).join('');
            }
        }
        
        window.removeFile = function(index) {
            files.splice(index, 1);
            renderFiles();
        };
        
        convertBtn.addEventListener('click', async () => {
            if (files.length === 0) return;
            
            convertBtn.disabled = true;
            status.className = 'status statusprocessing';
            status.textContent = 'Конвертиране...';
            
            let success = 0;
            let errors = 0;
            
            for (let i = 0; i < files.length; i++) {
                const f = files[i];
                status.textContent = 'Конвертиране на ' + f.name + '...';
                
                const formData = new FormData();
                formData.append('file', f);
                
                try {
                    const resp = await fetch('/convert', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (resp.ok) {
                        success++;
                    } else {
                        errors++;
                        const text = await resp.text();
                        console.error(text);
                    }
                } catch (e) {
                    errors++;
                    console.error(e);
                }
            }
            
            if (errors === 0) {
                status.className = 'status statussuccess';
                status.textContent = '✓ Успешно конвертирани ' + success + ' файла';
            } else {
                status.className = 'status statuserror';
                status.textContent = '✗ Конвертирани: ' + success + ', Грешки: ' + errors;
            }
            
            convertBtn.disabled = false;
            files = [];
            renderFiles();
        });
    </script>
</body>
</html>`))

type Server struct {
	addr string
}

func Run() {
	port := findAvailablePort()
	addr := fmt.Sprintf("127.0.0.1:%d", port)
	s := &Server{addr: addr}

	http.HandleFunc("/", s.handleIndex)
	http.HandleFunc("/convert", s.handleConvert)
	http.HandleFunc("/health", s.handleHealth)

	url := fmt.Sprintf("http://localhost:%d", port)

	go func() {
		time.Sleep(100 * time.Millisecond)
		openBrowser(url)
	}()

	fmt.Println("lev-euro-converter")
	fmt.Println("================")
	fmt.Println("Serving UI at:", url)
	fmt.Println("Press Ctrl+C to exit")

	if err := http.ListenAndServe(addr, nil); err != nil && err != http.ErrServerClosed {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

func findAvailablePort() int {
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return 8080
	}
	l.Close()
	return l.Addr().(*net.TCPAddr).Port
}

func (s *Server) handleIndex(w http.ResponseWriter, r *http.Request) {
	htmlTemplate.Execute(w, nil)
}

func (s *Server) handleConvert(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	defer file.Close()

	tmpDir, err := os.MkdirTemp("", "lev-euro-*")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer os.RemoveAll(tmpDir)

	inputPath := filepath.Join(tmpDir, header.Filename)
	outputPath := filepath.Join(tmpDir, strings.Replace(header.Filename, ".docx", "_eur.docx", 1))

	outFile, err := os.Create(inputPath)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if _, err := io.Copy(outFile, file); err != nil {
		outFile.Close()
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	outFile.Close()

	if err := converter.ConvertDOCX(inputPath, outputPath); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Disposition", "attachment; filename="+filepath.Base(outputPath))
	http.ServeFile(w, r, outputPath)
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("ok"))
}

func openBrowser(url string) {
	var cmd *exec.Cmd

	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("cmd", "/c", "start", url)
	case "darwin":
		cmd = exec.Command("open", url)
	default:
		cmd = exec.Command("xdg-open", url)
	}

	if cmd.Run(); cmd.Stderr != nil {
		fmt.Fprintf(os.Stderr, "Error opening browser: %v\n", cmd.Stderr)
	}
}