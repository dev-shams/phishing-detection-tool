/**
 * Phase 3: Phishing Detection Tool - Main JavaScript
 * Handles client-side interactions and API calls
 */

// Check server status on page load
document.addEventListener('DOMContentLoaded', function() {
    checkServerStatus();
});

async function checkServerStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        console.log('Server status:', data);
    } catch (error) {
        console.error('Server status check failed:', error);
    }
}

// Utility: Format percentage
function formatPercent(value) {
    return (parseFloat(value) * 100).toFixed(1) + '%';
}

// Utility: Format number with 2 decimals
function formatNumber(value) {
    return parseFloat(value).toFixed(2);
}

// Smooth scroll to elements
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        }
    });
});

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.feature-card, .stat, .result-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.3s, transform 0.3s';
    observer.observe(el);
});
