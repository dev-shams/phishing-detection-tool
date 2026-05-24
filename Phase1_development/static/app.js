/**
 * Phishing Email Detector - Frontend JavaScript
 */

// DOM Elements
const emailFileInput = document.getElementById('emailFile');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');

// Manual input elements
const toggleManualBtn = document.getElementById('toggleManual');
const manualForm = document.getElementById('manualForm');
const analyzeTextBtn = document.getElementById('analyzeTextBtn');
const cancelTextBtn = document.getElementById('cancelTextBtn');

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    console.log('✓ Application loaded');
    checkSystemStatus();
});

analyzeBtn.addEventListener('click', analyzeFile);
analyzeAnotherBtn.addEventListener('click', resetForm);
toggleManualBtn.addEventListener('click', toggleManualInput);
analyzeTextBtn.addEventListener('click', analyzeManualText);
cancelTextBtn.addEventListener('click', () => {
    manualForm.style.display = 'none';
    toggleManualBtn.textContent = 'Or analyze email text directly';
});

// Drag and drop
emailFileInput.addEventListener('dragover', (e) => {
    e.preventDefault();
    emailFileInput.style.backgroundColor = '#f0f0f0';
});

emailFileInput.addEventListener('dragleave', () => {
    emailFileInput.style.backgroundColor = '';
});

emailFileInput.addEventListener('drop', (e) => {
    e.preventDefault();
    emailFileInput.files = e.dataTransfer.files;
    emailFileInput.style.backgroundColor = '';
});

/**
 * Check system status
 */
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        console.log('System status:', data);

        const statusBadge = document.getElementById('model-status');
        if (data.model_trained) {
            statusBadge.textContent = 'Model Ready';
            statusBadge.className = 'badge bg-success';
        } else {
            statusBadge.textContent = 'Initializing...';
            statusBadge.className = 'badge bg-warning';
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

/**
 * Analyze uploaded email file
 */
async function analyzeFile() {
    const file = emailFileInput.files[0];

    if (!file) {
        showError('Please select an email file (.eml or .msg)');
        return;
    }

    // Validate file extension
    const validExtensions = ['eml', 'msg'];
    const fileExtension = file.name.split('.').pop().toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
        showError(`Invalid file format. Accepted: ${validExtensions.join(', ')}`);
        return;
    }

    // Show loading
    hideError();
    showLoading();

    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);

        // Send to server
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            showError(data.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * Analyze email text
 */
async function analyzeManualText() {
    const sender = document.getElementById('manualSender').value;
    const subject = document.getElementById('manualSubject').value;
    const body = document.getElementById('manualBody').value;

    if (!body.trim()) {
        showError('Please enter email body text');
        return;
    }

    hideError();
    showLoading();

    try {
        const response = await fetch('/api/analyze-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sender: sender || 'unknown@example.com',
                subject: subject || 'No Subject',
                email_text: body
            })
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
            manualForm.style.display = 'none';
        } else {
            showError(data.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    // Hide error, show results
    hideError();

    // Update email info
    document.getElementById('emailFrom').textContent = data.email_info.sender;
    document.getElementById('emailDomain').textContent = data.email_info.sender_domain;
    document.getElementById('emailSubject').textContent = data.email_info.subject;
    document.getElementById('emailTo').textContent = data.email_info.to;

    // Update classification
    const prediction = data.prediction;
    const classificationBadge = document.getElementById('classificationBadge');
    const classificationCard = document.getElementById('classificationCard');
    const confidenceText = document.getElementById('confidenceText');

    if (prediction.classification === 'PHISHING') {
        classificationBadge.textContent = '⚠️ PHISHING DETECTED';
        classificationBadge.className = 'badge bg-danger';
        classificationCard.className = 'card shadow-sm mb-4 phishing-card';
        confidenceText.innerHTML = `
            <strong>This email is likely a phishing attempt</strong><br>
            Confidence: <strong>${prediction.confidence_phishing.toFixed(1)}%</strong>
        `;
    } else {
        classificationBadge.textContent = '✓ LIKELY SAFE';
        classificationBadge.className = 'badge bg-success';
        classificationCard.className = 'card shadow-sm mb-4 legitimate-card';
        confidenceText.innerHTML = `
            <strong>This email appears to be legitimate</strong><br>
            Confidence: <strong>${prediction.confidence_legitimate.toFixed(1)}%</strong>
        `;
    }

    // Update confidence bar
    const confidence = prediction.confidence_phishing;
    const barFill = document.getElementById('confidenceBarFill');
    const confidencePercent = document.getElementById('confidencePercent');

    barFill.style.width = confidence + '%';
    barFill.className = confidence > 50 ? 'progress-bar phishing' : 'progress-bar legitimate';
    confidencePercent.textContent = confidence.toFixed(1) + '%';

    // Display threat indicators
    const threatCard = document.getElementById('threatCard');
    const threatList = document.getElementById('threatList');

    if (data.threat_indicators && data.threat_indicators.length > 0) {
        threatList.innerHTML = '';
        data.threat_indicators.forEach(indicator => {
            const indicatorEl = document.createElement('div');
            indicatorEl.className = `threat-indicator ${indicator.severity}`;
            indicatorEl.innerHTML = `
                <div class="threat-indicator-title">
                    <i class="fas ${getSeverityIcon(indicator.severity)}"></i>
                    ${indicator.type}
                </div>
                <p class="threat-indicator-description">${indicator.description}</p>
            `;
            threatList.appendChild(indicatorEl);
        });
        threatCard.style.display = 'block';
    } else {
        threatCard.style.display = 'none';
    }

    // Update recommendation
    const recommendationEl = document.getElementById('recommendation');
    recommendationEl.textContent = data.recommendation;

    if (prediction.classification === 'PHISHING') {
        recommendationEl.className = 'alert alert-danger';
    } else {
        recommendationEl.className = 'alert alert-success';
    }

    // Show results
    resultsSection.style.display = 'block';
    document.querySelector('body').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Get severity icon
 */
function getSeverityIcon(severity) {
    switch (severity) {
        case 'high':
            return 'fa-exclamation-circle';
        case 'medium':
            return 'fa-exclamation-triangle';
        case 'low':
            return 'fa-info-circle';
        default:
            return 'fa-circle';
    }
}

/**
 * Toggle manual input form
 */
function toggleManualInput() {
    const isVisible = manualForm.style.display !== 'none';
    manualForm.style.display = isVisible ? 'none' : 'block';
    toggleManualBtn.textContent = isVisible ? 'Or analyze email text directly' : 'Hide text input';
}

/**
 * Reset form
 */
function resetForm() {
    emailFileInput.value = '';
    document.getElementById('manualSender').value = '';
    document.getElementById('manualSubject').value = '';
    document.getElementById('manualBody').value = '';
    resultsSection.style.display = 'none';
    hideError();
    hideLoading();
}

/**
 * Show loading indicator
 */
function showLoading() {
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    loadingSection.style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

/**
 * Hide error message
 */
function hideError() {
    errorSection.style.display = 'none';
}

// Utility: Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

console.log('✓ JavaScript loaded and ready');
