document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements
    const formatCards = document.querySelectorAll('.format-card');
    const contentTypeInput = document.getElementById('content_type');
    const titleInput = document.getElementById('title');
    const textInput = document.getElementById('input_text');
    const audioInput = document.getElementById('audio_file');
    const previewArea = document.getElementById('preview-area');
    const generatePromptsBtn = document.getElementById('generate-prompts');
    const form = document.querySelector('form');

    // Format card selection
    formatCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove selection from all cards
            formatCards.forEach(c => c.classList.remove('selected'));
            
            // Select clicked card
            this.classList.add('selected');
            
            // Update hidden input
            const format = this.dataset.format;
            contentTypeInput.value = format;
            
            // Show/hide appropriate inputs
            updateInputVisibility(format);
            
            // Update preview placeholder
            updatePreviewPlaceholder(format);
        });
    });

    // Input visibility management
    function updateInputVisibility(format) {
        const textSection = document.querySelector('.text-input-section');
        const audioSection = document.querySelector('.audio-input-section');
        
        switch(format) {
            case 'photo_quote':
            case 'video_reel':
                textSection.style.display = 'block';
                audioSection.style.display = 'none';
                break;
            case 'voice_video':
            case 'avatar_video':
                textSection.style.display = 'block';
                audioSection.style.display = 'block';
                break;
        }
    }

    // Preview placeholder updates
    function updatePreviewPlaceholder(format) {
        let icon, text;
        switch(format) {
            case 'photo_quote':
                icon = 'fa-quote-right';
                text = 'Quote preview will appear here';
                break;
            case 'video_reel':
                icon = 'fa-film';
                text = 'Video preview will appear here';
                break;
            case 'voice_video':
                icon = 'fa-microphone';
                text = 'Voice video preview will appear here';
                break;
            case 'avatar_video':
                icon = 'fa-user-tie';
                text = 'Avatar video preview will appear here';
                break;
            default:
                icon = 'fa-image';
                text = 'Select a content type to see preview';
        }

        previewArea.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas ${icon} fa-3x mb-3"></i>
                <p>${text}</p>
            </div>
        `;
    }

    // Generate prompts functionality
    generatePromptsBtn.addEventListener('click', async function() {
        try {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            
            const response = await fetch('/api/generate-prompts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    count: 3,
                    theme: titleInput.value || 'general'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const promptSelect = document.createElement('select');
                promptSelect.className = 'form-select mt-2';
                promptSelect.innerHTML = '<option value="">Select a prompt...</option>';
                
                data.prompts.forEach(prompt => {
                    const option = document.createElement('option');
                    option.value = prompt;
                    option.textContent = prompt;
                    promptSelect.appendChild(option);
                });
                
                promptSelect.addEventListener('change', function() {
                    if (this.value) {
                        textInput.value = this.value;
                    }
                });
                
                // Replace existing prompt select if any
                const existingSelect = document.querySelector('.prompt-select');
                if (existingSelect) {
                    existingSelect.remove();
                }
                promptSelect.classList.add('prompt-select');
                this.parentNode.insertBefore(promptSelect, this.nextSibling);
            }
        } catch (error) {
            console.error('Error generating prompts:', error);
            alert('Error generating prompts. Please try again.');
        } finally {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-magic"></i> Generate Prompts';
        }
    });

    // Form validation
    form.addEventListener('submit', function(e) {
        if (!contentTypeInput.value) {
            e.preventDefault();
            alert('Please select a content type');
            return;
        }
        
        if (!titleInput.value.trim()) {
            e.preventDefault();
            alert('Please enter a title');
            return;
        }
        
        const format = contentTypeInput.value;
        if (format === 'voice_video' || format === 'avatar_video') {
            if (!textInput.value.trim() && !audioInput.files.length) {
                e.preventDefault();
                alert('Please provide either text or an audio file');
                return;
            }
        } else if (!textInput.value.trim()) {
            e.preventDefault();
            alert('Please enter some text content');
            return;
        }
    });

    // File upload preview
    audioInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            const duration = document.createElement('p');
            duration.className = 'text-muted mt-2';
            duration.textContent = `Selected file: ${file.name}`;
            
            // Remove existing duration display if any
            const existingDuration = audioInput.parentNode.querySelector('p');
            if (existingDuration) {
                existingDuration.remove();
            }
            
            audioInput.parentNode.appendChild(duration);
        }
    });

    // Initialize with default state
    updatePreviewPlaceholder('');
});