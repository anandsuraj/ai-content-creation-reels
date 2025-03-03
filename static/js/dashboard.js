document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements
    const contentGrid = document.querySelector('.content-grid');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const searchInput = document.getElementById('content-search');
    
    // Content deletion handler
    function deleteContent(contentId) {
        if (confirm('Are you sure you want to delete this content?')) {
            fetch(`/content/${contentId}/delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (response.ok) {
                    // Remove content card from DOM
                    const contentCard = document.querySelector(`[data-content-id="${contentId}"]`);
                    if (contentCard) {
                        contentCard.remove();
                        updateStats();
                    }
                    showNotification('Content deleted successfully', 'success');
                } else {
                    throw new Error('Failed to delete content');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error deleting content', 'error');
            });
        }
    }

    // Update dashboard stats
    function updateStats() {
        const contentCards = document.querySelectorAll('.content-card');
        const photoQuotes = document.querySelectorAll('[data-type="photo_quote"]').length;
        const videos = document.querySelectorAll('[data-type="video_reel"], [data-type="voice_video"], [data-type="avatar_video"]').length;
        
        // Update stats display
        document.querySelector('#total-content').textContent = contentCards.length;
        document.querySelector('#photo-quotes').textContent = photoQuotes;
        document.querySelector('#videos').textContent = videos;
        
        // Update empty state visibility
        const emptyState = document.querySelector('.empty-state');
        if (emptyState) {
            emptyState.style.display = contentCards.length === 0 ? 'block' : 'none';
        }
    }

    // Content filtering
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const contentCards = document.querySelectorAll('.content-card');
            
            contentCards.forEach(card => {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const type = card.dataset.type.toLowerCase();
                
                if (title.includes(searchTerm) || type.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Content type filtering
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filterType = this.dataset.filter;
            const contentCards = document.querySelectorAll('.content-card');
            
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            contentCards.forEach(card => {
                if (filterType === 'all' || card.dataset.type === filterType) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Preview content
    const contentCards = document.querySelectorAll('.content-card');
    contentCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Ignore if clicking delete button or view button
            if (e.target.closest('.content-actions')) {
                return;
            }
            
            const contentId = this.dataset.contentId;
            window.location.href = `/content/${contentId}`;
        });
    });

    // Notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);
        
        // Auto dismiss after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Export functionality
    document.getElementById('export-content')?.addEventListener('click', function() {
        const contentData = Array.from(document.querySelectorAll('.content-card')).map(card => ({
            id: card.dataset.contentId,
            title: card.querySelector('.card-title').textContent,
            type: card.dataset.type,
            created: card.dataset.created
        }));
        
        const blob = new Blob([JSON.stringify(contentData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'content-export.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Make global functions available
    window.deleteContent = deleteContent;
    window.updateStats = updateStats;
});