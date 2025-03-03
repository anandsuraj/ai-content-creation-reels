document.addEventListener('DOMContentLoaded', function() {
    // Utility Functions
    window.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    // Flash Message Handling
    function initializeFlashMessages() {
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(message => {
            setTimeout(() => {
                const alert = bootstrap.Alert.getOrCreateInstance(message);
                alert.close();
            }, 5000);
        });
    }

    // Navigation Active State
    function setActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });
    }

    // Form Validation
    function initializeFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }

    // File Input Enhancement
    function initializeFileInputs() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', function() {
                const fileName = this.files[0]?.name;
                const label = this.nextElementSibling;
                if (label && fileName) {
                    label.textContent = fileName;
                }
            });
        });
    }

    // Copy to Clipboard Functionality
    function initializeCopyButtons() {
        const copyButtons = document.querySelectorAll('[data-copy]');
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const text = this.dataset.copy;
                navigator.clipboard.writeText(text).then(() => {
                    const originalText = this.innerHTML;
                    this.innerHTML = 'Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                });
            });
        });
    }

    // Ajax Request Helper
    window.ajaxRequest = async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Ajax Request Error:', error);
            throw error;
        }
    };

    // Back to Top Button
    function initializeBackToTop() {
        const backToTop = document.createElement('button');
        backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
        backToTop.className = 'btn btn-primary back-to-top';
        backToTop.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: none;
            z-index: 1000;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            padding: 0;
        `;
        
        document.body.appendChild(backToTop);
        
        window.addEventListener('scroll', debounce(function() {
            backToTop.style.display = window.scrollY > 300 ? 'block' : 'none';
        }, 150));
        
        backToTop.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Initialize Bootstrap Tooltips
    function initializeTooltips() {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    }

    // Initialize Bootstrap Popovers
    function initializePopovers() {
        const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
        popovers.forEach(popover => new bootstrap.Popover(popover));
    }

    // Initialize all components
    function initializeAll() {
        setActiveNavigation();
        initializeFlashMessages();
        initializeFormValidation();
        initializeFileInputs();
        initializeCopyButtons();
        initializeBackToTop();
        initializeTooltips();
        initializePopovers();
    }

    // Run initialization
    initializeAll();
});