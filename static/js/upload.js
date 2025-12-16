document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const dropArea = document.getElementById('dropArea');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const statusElement = document.getElementById('status');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);

    // Handle file selection via input
    fileInput.addEventListener('change', handleFileSelect, false);

    // Handle form submission
    form.addEventListener('submit', handleSubmit);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropArea.classList.add('active');
    }

    function unhighlight() {
        dropArea.classList.remove('active');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect() {
        const files = this.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            // Update the file input with the dropped file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]);
            fileInput.files = dataTransfer.files;
            
            // Update UI to show file is ready
            const fileMessage = dropArea.querySelector('.file-message');
            fileMessage.textContent = `File ready: ${files[0].name}`;
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showStatus('Please select a file first', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Show progress
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            progressText.textContent = '0%';
            
            const xhr = new XMLHttpRequest();
            
            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percentComplete = Math.round((event.loaded / event.total) * 100);
                    updateProgress(percentComplete);
                }
            };

            xhr.onload = () => {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    showStatus(response.message, 'success');
                    
                    // Redirect to QA page if a redirect URL is provided
                    if (response.redirect) {
                        setTimeout(() => {
                            window.location.href = response.redirect;
                        }, 1000);
                    }
                    // Reset form after successful upload
                    setTimeout(() => {
                        form.reset();
                        progressContainer.style.display = 'none';
                        dropArea.querySelector('.file-message').textContent = 'Drag & drop your file here or click to browse';
                    }, 1500);
                } else {
                    showStatus('Upload failed. Please try again.', 'error');
                }
            };

            xhr.onerror = () => {
                showStatus('An error occurred during upload.', 'error');
                progressContainer.style.display = 'none';
            };

            // Replace '/upload' with your actual upload endpoint
            xhr.open('POST', '/upload', true);
            xhr.send(formData);

        } catch (error) {
            console.error('Error:', error);
            showStatus('An error occurred. Please try again.', 'error');
            progressContainer.style.display = 'none';
        }
    }

    function updateProgress(percent) {
        progressBar.style.width = `${percent}%`;
        progressText.textContent = `${percent}%`;
    }

    function showStatus(message, type = 'info') {
        statusElement.textContent = message;
        statusElement.className = 'status-message';
        statusElement.classList.add(type);
    }
});
