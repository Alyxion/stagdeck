/**
 * 🎬 StagDeck Slide Scaling Script
 * 
 * Handles responsive scaling of slides to fit the viewport.
 */

function updateSlideScale() {
    const wrapper = document.querySelector('.slide-wrapper');
    const frame = document.querySelector('.slide-frame');
    if (!wrapper || !frame) return;
    
    const isFullscreen = !!document.fullscreenElement;
    const padding = isFullscreen ? 0 : 48;
    
    const wrapperRect = wrapper.getBoundingClientRect();
    const availableWidth = wrapperRect.width - padding;
    const availableHeight = wrapperRect.height - padding;
    
    // Get slide dimensions from data attributes (native resolution)
    const slideWidth = parseInt(frame.dataset.width) || 1920;
    const slideHeight = parseInt(frame.dataset.height) || 1080;
    
    // Calculate uniform scale to fit while maintaining aspect ratio
    const scaleX = availableWidth / slideWidth;
    const scaleY = availableHeight / slideHeight;
    const maxScale = isFullscreen ? Infinity : 1;
    const scale = Math.min(scaleX, scaleY, maxScale);
    
    // Force the frame to native dimensions and apply uniform scale
    frame.style.width = slideWidth + 'px';
    frame.style.height = slideHeight + 'px';
    frame.style.transform = `scale(${scale})`;
    
    // Show frame after scaling is applied (prevents FOUC)
    frame.classList.add('scaled');
}

// Initialize scaling
window.addEventListener('resize', updateSlideScale);
document.addEventListener('fullscreenchange', updateSlideScale);

// Initial scale after DOM is ready
setTimeout(updateSlideScale, 100);

// Watch for DOM changes
const observer = new MutationObserver(updateSlideScale);
setTimeout(() => {
    const wrapper = document.querySelector('.slide-wrapper');
    if (wrapper) {
        observer.observe(wrapper, { childList: true, subtree: true });
    }
}, 100);
