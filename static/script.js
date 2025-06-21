// YouTube Playlist Learning Module Generator - JavaScript

class PlaylistGenerator {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentStep = 0;
        this.totalSteps = 3;
        this.initializeFirebase();
    }    initializeElements() {
        // Input elements
        this.playlistUrlInput = document.getElementById('playlist-url');
        this.maxVideosSelect = document.getElementById('max-videos');
        this.courseFormatSelect = document.getElementById('course-format');
        this.generateBtn = document.getElementById('generate-btn');
        
        // Status elements
        this.urlValidation = document.getElementById('url-validation');
        
        // Section elements
        this.progressSection = document.getElementById('progress-section');
        this.resultsSection = document.getElementById('results-section');
        this.errorSection = document.getElementById('error-section');
        
        // Progress elements
        this.progressText = document.getElementById('progress-text');
        this.progressFill = document.getElementById('progress-fill');
        this.progressSteps = document.querySelectorAll('.step');
        
        // Result elements
        this.courseOverview = document.getElementById('course-overview');
        this.modulesPreview = document.getElementById('modules-preview');
        this.downloadHtml = document.getElementById('download-html');
        this.downloadJson = document.getElementById('download-json');
        this.downloadMd = document.getElementById('download-md');
        
        // Error elements
        this.errorText = document.getElementById('error-text');
        this.retryBtn = document.getElementById('retry-btn');
        
        // Firebase elements
        this.firebaseSection = document.getElementById('firebase-section');
        this.searchInput = document.getElementById('search-input');
        this.searchBtn = document.getElementById('search-btn');
        this.refreshBtn = document.getElementById('refresh-btn');
        this.playlistsContainer = document.getElementById('playlists-container');
        this.playlistsLoading = document.getElementById('playlists-loading');
        this.playlistsList = document.getElementById('playlists-list');
        this.playlistsEmpty = document.getElementById('playlists-empty');
    }

    bindEvents() {
        // URL input validation
        this.playlistUrlInput.addEventListener('input', this.debounce(this.validateUrl.bind(this), 500));
        this.playlistUrlInput.addEventListener('paste', () => {
            setTimeout(() => this.validateUrl(), 100);
        });
        
        // Generate button
        this.generateBtn.addEventListener('click', this.generateModules.bind(this));
        
        // Firebase events
        this.searchBtn?.addEventListener('click', this.searchPlaylists.bind(this));
        this.refreshBtn?.addEventListener('click', this.loadSavedPlaylists.bind(this));
        this.searchInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchPlaylists();
            }
        });
        
        // Retry button
        this.retryBtn.addEventListener('click', this.resetForm.bind(this));
        
        // Enter key support
        this.playlistUrlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.generateBtn.disabled) {
                this.generateModules();
            }
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async validateUrl() {
        const url = this.playlistUrlInput.value.trim();
        
        if (!url) {
            this.setValidationMessage('', 'neutral');
            this.generateBtn.disabled = true;
            return;
        }

        // Basic URL validation
        if (!this.isValidYouTubeUrl(url)) {
            this.setValidationMessage('❌ Please enter a valid YouTube playlist URL', 'invalid');
            this.generateBtn.disabled = true;
            return;
        }

        try {
            // Validate with server
            this.setValidationMessage('🔍 Checking playlist...', 'neutral');
            
            const response = await fetch('/api/validate_url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (data.valid) {
                if (data.playlist_info) {
                    const info = data.playlist_info;
                    this.setValidationMessage(
                        `✅ Found: "${info.title}" (${info.video_count} videos) by ${info.channel}`,
                        'valid'
                    );
                } else {
                    this.setValidationMessage('✅ Valid YouTube playlist URL', 'valid');
                }
                this.generateBtn.disabled = false;
            } else {
                this.setValidationMessage(
                    `❌ ${data.error || 'Invalid or inaccessible playlist'}`,
                    'invalid'
                );
                this.generateBtn.disabled = true;
            }
        } catch (error) {
            console.error('URL validation error:', error);
            this.setValidationMessage('⚠️ Unable to validate URL (check connection)', 'invalid');
            this.generateBtn.disabled = true;
        }
    }

    isValidYouTubeUrl(url) {
        const youtubeRegex = /^https?:\/\/(www\.)?(youtube\.com|youtu\.be)\/.*[?&]list=([a-zA-Z0-9_-]+)/;
        return youtubeRegex.test(url);
    }

    setValidationMessage(message, type) {
        this.urlValidation.textContent = message;
        this.urlValidation.className = `validation-message ${type}`;
        
        // Update input styling
        this.playlistUrlInput.className = `url-input ${type}`;
    }    async generateModules() {
        const url = this.playlistUrlInput.value.trim();
        const maxVideos = parseInt(this.maxVideosSelect.value);
        const courseFormat = this.courseFormatSelect.value;

        if (!url || this.generateBtn.disabled) {
            return;
        }

        try {
            this.startProgress();
            
            // Choose API endpoint based on selected format
            const endpoint = courseFormat === 'enhanced' ? '/api/generate_enhanced_course' : '/api/process_playlist';
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    playlist_url: url,
                    max_videos: maxVideos
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to process playlist');
            }

            const data = await response.json();
            
            // Handle different response formats
            if (courseFormat === 'enhanced') {
                this.showEnhancedResults(data);
            } else {
                this.showResults(data);
            }

        } catch (error) {
            console.error('Generation error:', error);
            this.showError(error.message);
        }
    }

    startProgress() {
        // Hide other sections
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';
        
        // Show progress section
        this.progressSection.style.display = 'block';
        this.progressSection.classList.add('fade-in');
        
        // Disable generate button
        this.generateBtn.disabled = true;
        this.generateBtn.querySelector('.btn-text').style.display = 'none';
        this.generateBtn.querySelector('.btn-loader').style.display = 'inline';
        
        // Reset progress
        this.currentStep = 0;
        this.updateProgress();
        
        // Simulate progress steps
        this.simulateProgress();
    }

    simulateProgress() {
        const steps = [
            { delay: 1000, text: 'Extracting playlist metadata...', progress: 20 },
            { delay: 3000, text: 'Downloading video transcripts...', progress: 40 },
            { delay: 2000, text: 'Analyzing content with AI...', progress: 70 },
            { delay: 2000, text: 'Generating learning modules...', progress: 90 },
            { delay: 1000, text: 'Finalizing course materials...', progress: 100 }
        ];

        let totalDelay = 0;
        steps.forEach((step, index) => {
            totalDelay += step.delay;
            setTimeout(() => {
                if (this.progressSection.style.display === 'block') {
                    this.progressText.textContent = step.text;
                    this.progressFill.style.width = `${step.progress}%`;
                    
                    if (index < this.totalSteps) {
                        this.setStepStatus(index, 'active');
                        if (index > 0) {
                            this.setStepStatus(index - 1, 'completed');
                        }
                    }
                }
            }, totalDelay);
        });
    }

    updateProgress() {
        const progressPercent = (this.currentStep / this.totalSteps) * 100;
        this.progressFill.style.width = `${progressPercent}%`;
        
        // Update step indicators
        this.progressSteps.forEach((step, index) => {
            if (index < this.currentStep) {
                this.setStepStatus(index, 'completed');
            } else if (index === this.currentStep) {
                this.setStepStatus(index, 'active');
            } else {
                this.setStepStatus(index, 'inactive');
            }
        });
    }

    setStepStatus(stepIndex, status) {
        const step = this.progressSteps[stepIndex];
        if (step) {
            step.className = `step ${status}`;
        }
    }

    showResults(data) {
        // Hide progress section
        this.progressSection.style.display = 'none';
        
        // Show results section
        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('fade-in');
        
        // Populate course overview
        this.populateCourseOverview(data.course_info);
        
        // Populate modules preview
        this.populateModulesPreview(data.modules);
        
        // Set up download links
        this.setupDownloadLinks();
        
        // Reset generate button
        this.resetGenerateButton();
    }

    populateCourseOverview(courseInfo) {
        const overview = `
            <div class="course-title">${this.escapeHtml(courseInfo.title)}</div>
            <p class="course-description">${this.escapeHtml(courseInfo.description)}</p>
            <div class="course-meta">
                <div class="meta-item">
                    <span class="meta-icon">📊</span>
                    <span>${courseInfo.total_modules} Learning Modules</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">🎥</span>
                    <span>${courseInfo.total_videos} Videos</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">⏱️</span>
                    <span>${this.escapeHtml(courseInfo.estimated_time)}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">📈</span>
                    <span>${this.escapeHtml(courseInfo.difficulty_level)} Level</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">📚</span>
                    <span>${this.escapeHtml(courseInfo.subject)}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">🎯</span>
                    <span>${this.escapeHtml(courseInfo.approach)} Approach</span>
                </div>
            </div>
        `;
        this.courseOverview.innerHTML = overview;
    }

    populateModulesPreview(modules) {
        if (!modules || modules.length === 0) {
            this.modulesPreview.innerHTML = '<p>No modules generated.</p>';
            return;
        }

        let html = '<h3>📖 Learning Modules Preview</h3>';
        
        modules.forEach((module, index) => {
            html += `
                <div class="module-card">
                    <div class="module-header">
                        <div class="module-title">
                            Module ${module.order || index + 1}: ${this.escapeHtml(module.title)}
                        </div>
                        <div class="module-meta">
                            <div>${this.escapeHtml(module.estimated_time || 'Unknown')}</div>
                            <div>${this.escapeHtml(module.difficulty || 'intermediate')} level</div>
                        </div>
                    </div>
                    <div class="module-description">
                        ${this.escapeHtml(module.description || 'No description available')}
                    </div>
                    <div class="module-stats">
                        <span>📹 ${module.videos ? module.videos.length : 0} videos</span>
                        <span>🎯 ${module.learning_objectives ? module.learning_objectives.length : 0} objectives</span>
                        <span>💡 ${module.key_concepts ? module.key_concepts.length : 0} key concepts</span>
                        <span>🎪 ${module.activities ? module.activities.length : 0} activities</span>
                    </div>
                </div>
            `;
        });
        
        this.modulesPreview.innerHTML = html;
    }

    setupDownloadLinks() {
        const timestamp = new Date().toISOString().split('T')[0];
        
        this.downloadHtml.href = '/api/download/course_guide.html';
        this.downloadHtml.download = `learning_course_${timestamp}.html`;
        
        this.downloadJson.href = '/api/download/course_data.json';
        this.downloadJson.download = `course_data_${timestamp}.json`;
        
        this.downloadMd.href = '/api/download/course_guide.md';
        this.downloadMd.download = `course_guide_${timestamp}.md`;
    }    showError(message) {
        // Hide progress section
        this.progressSection.style.display = 'none';
        
        // Show error section
        this.errorSection.style.display = 'block';
        this.errorSection.classList.add('fade-in');
        
        // Set error message
        this.errorText.textContent = message;
        
        // Reset generate button
        this.resetGenerateButton();
    }

    showEnhancedResults(data) {
        // Hide progress section
        this.progressSection.style.display = 'none';
        
        // Show results section
        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('fade-in');
        
        // Populate enhanced course overview
        this.populateEnhancedCourseOverview(data.course);
        
        // Populate enhanced modules preview
        this.populateEnhancedModulesPreview(data);
        
        // Set up enhanced download links
        this.setupEnhancedDownloadLinks(data);
        
        // Reset generate button
        this.resetGenerateButton();
    }

    populateEnhancedCourseOverview(course) {
        const prerequisites = course.prerequisites?.map(p => `<li>${this.escapeHtml(p)}</li>`).join('') || '';
        const objectives = course.learningObjectives?.map(o => `<li>${this.escapeHtml(o)}</li>`).join('') || '';
        const tags = course.tags?.map(t => `<span class="tag">${this.escapeHtml(t)}</span>`).join('') || '';
        
        const overview = `
            <div class="enhanced-course-overview">
                <div class="course-header">
                    <img src="${course.thumbnail}" alt="${this.escapeHtml(course.title)}" class="course-thumbnail" 
                         onerror="this.src='https://via.placeholder.com/640x360?text=Course+Thumbnail'">
                    <div class="course-info">
                        <div class="course-title">${this.escapeHtml(course.title)}</div>
                        <p class="course-description">${this.escapeHtml(course.description)}</p>
                        <div class="course-meta">
                            <div class="meta-item">
                                <span class="meta-icon">🏷️</span>
                                <span>${this.escapeHtml(course.category)}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-icon">📈</span>
                                <span>${this.escapeHtml(course.level)}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-icon">⏱️</span>
                                <span>${course.estimatedHours} hours</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-icon">📅</span>
                                <span>${this.escapeHtml(course.duration)}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-icon">👨‍🏫</span>
                                <span>${this.escapeHtml(course.instructor)}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-icon">💰</span>
                                <span>$${course.price}</span>
                            </div>
                        </div>
                        <div class="course-tags">
                            ${tags}
                        </div>
                    </div>
                </div>
                
                <div class="course-details">
                    <div class="course-section">
                        <h4>🎯 Learning Objectives</h4>
                        <ul class="objectives-list">
                            ${objectives}
                        </ul>
                    </div>
                    
                    <div class="course-section">
                        <h4>📋 Prerequisites</h4>
                        <ul class="prerequisites-list">
                            ${prerequisites}
                        </ul>
                    </div>
                </div>
            </div>
        `;
        this.courseOverview.innerHTML = overview;
    }

    populateEnhancedModulesPreview(data) {
        const modules = data.modules || [];
        const assignments = data.assignments || [];
        const finalExam = data.finalExam;
        
        if (modules.length === 0) {
            this.modulesPreview.innerHTML = '<p>No modules generated.</p>';
            return;
        }

        let html = '<div class="enhanced-modules-preview">';
        html += '<h3>📖 Course Structure</h3>';
        
        // Modules
        html += '<div class="modules-section">';
        modules.forEach((module, index) => {
            const lessons = module.lessons || [];
            html += `
                <div class="enhanced-module-card">
                    <div class="module-header">
                        <div class="module-title">
                            ${this.escapeHtml(module.title)}
                        </div>
                        <div class="module-meta">
                            <span>📅 ${this.escapeHtml(module.duration)}</span>
                            <span>📹 ${lessons.length} lessons</span>
                        </div>
                    </div>
                    <div class="module-description">
                        ${this.escapeHtml(module.description)}
                    </div>
                    <div class="lessons-preview">
                        ${lessons.map(lesson => `
                            <div class="lesson-item">
                                <span class="lesson-type">${this.getLessonTypeIcon(lesson.type)}</span>
                                <span class="lesson-title">${this.escapeHtml(lesson.title)}</span>
                                <span class="lesson-duration">${this.escapeHtml(lesson.duration)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        // Assignments
        if (assignments.length > 0) {
            html += '<div class="assignments-section">';
            html += '<h4>📝 Assignments</h4>';
            assignments.forEach(assignment => {
                html += `
                    <div class="assignment-card">
                        <div class="assignment-title">${this.escapeHtml(assignment.title)}</div>
                        <div class="assignment-description">${this.escapeHtml(assignment.description)}</div>
                        <div class="assignment-meta">
                            <span>📅 Due: ${new Date(assignment.dueDate).toLocaleDateString()}</span>
                            <span>🎯 ${assignment.points} points</span>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        // Final Exam
        if (finalExam) {
            html += '<div class="final-exam-section">';
            html += '<h4>🎓 Final Exam</h4>';
            html += `
                <div class="exam-card">
                    <div class="exam-title">${this.escapeHtml(finalExam.title)}</div>
                    <div class="exam-description">${this.escapeHtml(finalExam.description)}</div>
                    <div class="exam-meta">
                        <span>⏱️ ${finalExam.timeLimit} minutes</span>
                        <span>📊 ${finalExam.passingScore}% passing score</span>
                        <span>❓ ${finalExam.questions?.length || 0} questions</span>
                    </div>
                </div>
            `;
            html += '</div>';
        }
        
        html += '</div>';
        this.modulesPreview.innerHTML = html;
    }

    getLessonTypeIcon(type) {
        const icons = {
            'video': '🎥',
            'text': '📖',
            'quiz': '❓',
            'project': '🛠️'
        };
        return icons[type] || '📄';
    }

    setupEnhancedDownloadLinks(data) {
        const timestamp = new Date().toISOString().split('T')[0];
        
        // Create downloadable JSON content
        const jsonContent = JSON.stringify(data, null, 2);
        const jsonBlob = new Blob([jsonContent], { type: 'application/json' });
        const jsonUrl = URL.createObjectURL(jsonBlob);
        
        this.downloadJson.href = jsonUrl;
        this.downloadJson.download = `enhanced_course_${timestamp}.json`;
        
        // For HTML and MD, we'll use the existing endpoints for now
        this.downloadHtml.href = '/api/download/course_guide.html';
        this.downloadHtml.download = `enhanced_course_${timestamp}.html`;
        
        this.downloadMd.href = '/api/download/course_guide.md';
        this.downloadMd.download = `enhanced_course_${timestamp}.md`;
    }

    resetForm() {
        // Hide error and results sections
        this.errorSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        
        // Clear input
        this.playlistUrlInput.value = '';
        this.setValidationMessage('', 'neutral');
        
        // Reset generate button
        this.resetGenerateButton();
        
        // Focus on input
        this.playlistUrlInput.focus();
    }

    resetGenerateButton() {
        this.generateBtn.disabled = true;
        this.generateBtn.querySelector('.btn-text').style.display = 'inline';
        this.generateBtn.querySelector('.btn-loader').style.display = 'none';
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    initializeFirebase() {
        // Check Firebase status and initialize
        this.checkFirebaseStatus();
    }

    async checkFirebaseStatus() {
        try {
            const response = await fetch('/api/firebase/status');
            const data = await response.json();
            
            if (data.connected) {
                this.showFirebaseSection();
                this.loadSavedPlaylists();
            } else {
                console.log('Firebase not connected:', data);
            }
        } catch (error) {
            console.error('Error checking Firebase status:', error);
        }
    }

    showFirebaseSection() {
        if (this.firebaseSection) {
            this.firebaseSection.style.display = 'block';
        }
    }

    async loadSavedPlaylists() {
        try {
            this.showPlaylistsLoading();
            
            const response = await fetch('/api/playlists?limit=50');
            const data = await response.json();
            
            if (data.success) {
                this.displayPlaylists(data.playlists);
            } else {
                throw new Error(data.error || 'Failed to load playlists');
            }
        } catch (error) {
            console.error('Error loading playlists:', error);
            this.showPlaylistsError('Failed to load saved playlists');
        }
    }

    async searchPlaylists() {
        const query = this.searchInput?.value.trim();
        if (!query) {
            this.loadSavedPlaylists();
            return;
        }

        try {
            this.showPlaylistsLoading();
            
            const response = await fetch(`/api/playlists/search?q=${encodeURIComponent(query)}&limit=20`);
            const data = await response.json();
            
            if (data.success) {
                this.displayPlaylists(data.playlists);
            } else {
                throw new Error(data.error || 'Search failed');
            }
        } catch (error) {
            console.error('Error searching playlists:', error);
            this.showPlaylistsError('Search failed');
        }
    }

    displayPlaylists(playlists) {
        this.hidePlaylistsLoading();
        
        if (!playlists || playlists.length === 0) {
            this.showPlaylistsEmpty();
            return;
        }

        this.playlistsList.innerHTML = '';
        this.playlistsEmpty.style.display = 'none';

        playlists.forEach(playlist => {
            const playlistCard = this.createPlaylistCard(playlist);
            this.playlistsList.appendChild(playlistCard);
        });
    }

    createPlaylistCard(playlist) {
        const card = document.createElement('div');
        card.className = 'playlist-card';
        
        const thumbnailUrl = playlist.thumbnail_url || 'https://via.placeholder.com/480x360?text=No+Thumbnail';
        const updatedDate = new Date(playlist.updated_at.seconds * 1000).toLocaleDateString();
        
        card.innerHTML = `
            <img src="${thumbnailUrl}" alt="${playlist.title}" class="playlist-thumbnail" 
                 onerror="this.src='https://via.placeholder.com/480x360?text=No+Thumbnail'">
            <div class="playlist-info">
                <h4 class="playlist-title">${this.escapeHtml(playlist.title)}</h4>
                <div class="playlist-meta">
                    <span class="playlist-channel">${this.escapeHtml(playlist.channel_title)}</span>
                    <span class="playlist-count">${playlist.video_count} videos</span>
                </div>
                <div class="playlist-meta">
                    <span>Updated: ${updatedDate}</span>
                </div>
                <div class="playlist-actions">
                    <button class="action-btn primary" onclick="playlistGenerator.openPlaylist('${playlist.playlist_id}')">
                        📖 View Details
                    </button>
                    <button class="action-btn primary" onclick="playlistGenerator.loadPlaylistInForm('${playlist.url}')">
                        🔄 Reprocess
                    </button>
                    <button class="action-btn danger" onclick="playlistGenerator.deletePlaylist('${playlist.playlist_id}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `;
        
        return card;
    }

    async openPlaylist(playlistId) {
        try {
            const response = await fetch(`/api/playlists/${playlistId}`);
            const data = await response.json();
            
            if (data.success) {
                this.showPlaylistDetails(data.playlist, data.analysis);
            } else {
                throw new Error(data.error || 'Failed to load playlist details');
            }
        } catch (error) {
            console.error('Error opening playlist:', error);
            this.showErrorMessage('Failed to load playlist details');
        }
    }

    loadPlaylistInForm(url) {
        this.playlistUrlInput.value = url;
        this.validateUrl();
        this.playlistUrlInput.scrollIntoView({ behavior: 'smooth' });
    }

    async deletePlaylist(playlistId) {
        if (!confirm('Are you sure you want to delete this playlist? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/playlists/${playlistId}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            
            if (data.success) {
                this.loadSavedPlaylists(); // Refresh the list
                this.showSuccessMessage('Playlist deleted successfully');
            } else {
                throw new Error(data.error || 'Failed to delete playlist');
            }
        } catch (error) {
            console.error('Error deleting playlist:', error);
            this.showErrorMessage('Failed to delete playlist');
        }
    }

    showPlaylistDetails(playlist, analysis) {
        // Create a modal or details view for the playlist
        const modal = document.createElement('div');
        modal.className = 'playlist-modal';
        modal.innerHTML = `
            <div class="playlist-modal-content">
                <div class="playlist-modal-header">
                    <h2>${this.escapeHtml(playlist.title)}</h2>
                    <button class="close-modal" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="playlist-modal-body">
                    <div class="playlist-overview">
                        <img src="${playlist.thumbnail_url}" alt="${playlist.title}" class="playlist-detail-thumbnail">
                        <div class="playlist-detail-info">
                            <p><strong>Channel:</strong> ${this.escapeHtml(playlist.channel_title)}</p>
                            <p><strong>Videos:</strong> ${playlist.video_count}</p>
                            <p><strong>Created:</strong> ${new Date(playlist.created_at.seconds * 1000).toLocaleDateString()}</p>
                            <a href="${playlist.url}" target="_blank" class="playlist-link">🔗 Open on YouTube</a>
                            <button class="action-btn secondary" onclick="playlistGenerator.showVideoLinks('${playlist.playlist_id}')">
                                🔗 Show Video Links
                            </button>
                        </div>
                    </div>
                    ${analysis ? `
                        <div class="analysis-section">
                            <h3>📊 Analysis Results</h3>
                            <p><strong>Subject:</strong> ${analysis.structure_analysis?.subject || 'N/A'}</p>
                            <p><strong>Difficulty:</strong> ${analysis.difficulty_level || 'N/A'}</p>
                            <p><strong>Estimated Time:</strong> ${analysis.estimated_completion_time || 'N/A'}</p>
                            ${analysis.learning_objectives?.length ? `
                                <div class="learning-objectives">
                                    <h4>🎯 Learning Objectives:</h4>
                                    <ul>
                                        ${analysis.learning_objectives.map(obj => `<li>${this.escapeHtml(obj)}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    async showVideoLinks(playlistId) {
        try {
            const response = await fetch(`/api/playlists/${playlistId}/links`);
            const data = await response.json();

            if (data.success) {
                this.displayVideoLinksModal(playlistId, data.video_links, data.detailed_links);
            } else {
                throw new Error(data.error || 'Failed to load video links');
            }
        } catch (error) {
            console.error('Error getting video links:', error);
            this.showErrorMessage('Failed to load video links');
        }
    }

    displayVideoLinksModal(playlistId, links, detailedLinks) {
        const modal = document.createElement('div');
        modal.className = 'video-links-modal';
        
        let linksHtml = detailedLinks.map((video, index) => `<li><a href="${video.url}" target="_blank">${index + 1}. ${this.escapeHtml(video.title)}</a></li>`).join('');

        modal.innerHTML = `
            <div class="video-links-modal-content">
                <div class="video-links-modal-header">
                    <h3>Video Links for ${this.escapeHtml(playlistId)}</h3>
                    <button class="close-modal" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="video-links-modal-body">
                    <p>Found ${links.length} video links.</p>
                    <textarea class="links-textarea" readonly>${links.join('\n')}</textarea>
                    <button class="action-btn primary" onclick="playlistGenerator.copyLinksToClipboard(this)">Copy Links</button>
                    <h4>Video List</h4>
                    <ul class="links-list">${linksHtml}</ul>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    copyLinksToClipboard(button) {
        const textarea = button.parentElement.querySelector('.links-textarea');
        textarea.select();
        navigator.clipboard.writeText(textarea.value);
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = 'Copy Links';
        }, 2000);
    }

    // Helper methods for Firebase UI
    showPlaylistsLoading() {
        this.playlistsLoading.style.display = 'block';
        this.playlistsList.style.display = 'none';
        this.playlistsEmpty.style.display = 'none';
    }

    hidePlaylistsLoading() {
        this.playlistsLoading.style.display = 'none';
        this.playlistsList.style.display = 'grid';
    }

    showPlaylistsEmpty() {
        this.playlistsLoading.style.display = 'none';
        this.playlistsList.style.display = 'none';
        this.playlistsEmpty.style.display = 'block';
    }

    showPlaylistsError(message) {
        this.hidePlaylistsLoading();
        this.playlistsList.innerHTML = `<div class="error-message">${message}</div>`;
    }

    showSuccessMessage(message) {
        const toast = document.createElement('div');
        toast.className = 'toast success';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    showErrorMessage(message) {
        const toast = document.createElement('div');
        toast.className = 'toast error';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    // ...existing code...
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PlaylistGenerator();
    
    // Add some interactive enhancements
    addInteractiveEnhancements();
});

function addInteractiveEnhancements() {
    // Add ripple effect to buttons
    document.querySelectorAll('button, .download-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add smooth scrolling to sections
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.form-section, .progress-section, .results-section').forEach(section => {
        observer.observe(section);
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter to generate
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const generateBtn = document.getElementById('generate-btn');
            if (!generateBtn.disabled) {
                generateBtn.click();
            }
        }
        
        // Escape to reset
        if (e.key === 'Escape') {
            const errorSection = document.getElementById('error-section');
            if (errorSection.style.display === 'block') {
                document.getElementById('retry-btn').click();
            }
        }
    });
}

// Add CSS for ripple effect
const rippleCSS = `
.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: scale(0);
    animation: ripple-animation 0.6s linear;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(4);
        opacity: 0;
    }
}
`;

const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);
