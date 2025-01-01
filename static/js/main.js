document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const progressContainer = document.getElementById('progress-container');
    const progress = document.getElementById('progress');
    const status = document.getElementById('status');

    // Obsługa kliknięcia w strefę upuszczania
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Obsługa wyboru pliku
    fileInput.addEventListener('change', handleFileSelect);

    // Obsługa przeciągania
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
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            uploadFile(file);
        }
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        progressContainer.classList.remove('hidden');
        progress.style.width = '0%';
        status.textContent = 'Konwersja w toku...';

        fetch('/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Wystąpił błąd podczas konwersji');
                });
            }
            return response.blob();
        })
        .then(blob => {
            progress.style.width = '100%';
            status.textContent = 'Konwersja zakończona!';
            
            // Utworzenie linku do pobrania
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'converted.ppk';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            setTimeout(() => {
                progressContainer.classList.add('hidden');
                progress.style.width = '0%';
            }, 2000);
        })
        .catch(error => {
            status.textContent = `Błąd: ${error.message}`;
            progress.style.width = '0%';
        });
    }
}); 