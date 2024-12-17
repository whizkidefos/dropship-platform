// Toast Notification System
class Toast {
    static show(message, type = 'success') {
        const container = document.querySelector('.toast-container') || this.createContainer();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade-in`;
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${this.getIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
        `;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
            if (container.children.length === 0) container.remove();
        }, 3000);
    }

    static createContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    static getIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }
}

// Product Quick View
function quickView(productId) {
    fetch(`/products/api/quick-view/${productId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const modalBody = document.querySelector('#quickViewModal .modal-body');
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <img src="${data.main_image || '/static/img/no-image.png'}" 
                             class="img-fluid rounded" alt="${data.title}">
                    </div>
                    <div class="col-md-6">
                        <h4>${data.title}</h4>
                        <h5 class="text-primary mb-3">$${data.price.toFixed(2)}</h5>
                        <p>${data.description}</p>
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary" onclick="addToCart(${data.id})">
                                Add to Cart
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            const modal = new bootstrap.Modal(document.getElementById('quickViewModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            Toast.show('Error loading product details', 'error');
        });
}

// Add to Cart
function addToCart(productId) {
    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: 'quantity=1'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Toast.show('Product added to cart', 'success');
            updateCartCount(data.cart_total);
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        Toast.show('Error adding to cart', 'error');
    });
}

// Toggle Wishlist
function toggleWishlist(productId) {
    fetch(`/wishlist/toggle/${productId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Toast.show(data.message, 'success');
            updateWishlistIcon(productId, data.is_in_wishlist);
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        Toast.show('Error updating wishlist', 'error');
    });
}

// Helper Functions
function updateCartCount(count) {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

function updateWishlistIcon(productId, isInWishlist) {
    const wishlistBtn = document.querySelector(`.wishlist-btn[data-product-id="${productId}"]`);
    if (wishlistBtn) {
        const icon = wishlistBtn.querySelector('i');
        if (isInWishlist) {
            icon.classList.remove('far');
            icon.classList.add('fas');
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
        }
    }
}

// Initialize tooltips and popovers if using Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Lazy Loading Images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
});

// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Product Quick View
function initQuickView() {
    document.querySelectorAll('.quick-view-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            
            try {
                const response = await fetch(`/products/api/quick-view/${productId}`);
                const data = await response.json();
                
                // Update modal content
                const modal = document.getElementById('quickViewModal');
                modal.querySelector('.modal-body').innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <img src="${data.main_image}" class="img-fluid rounded" alt="${data.title}">
                        </div>
                        <div class="col-md-6">
                            <h4 class="mb-3">${data.title}</h4>
                            <h5 class="text-primary mb-3">$${data.price.toFixed(2)}</h5>
                            <p>${data.description}</p>
                            <div class="d-grid gap-2">
                                <button class="btn btn-primary" onclick="addToCart(${data.id})">
                                    Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Show modal
                bootstrap.Modal.getInstance(modal).show();
            } catch (error) {
                Toast.show('Error loading product details', 'error');
            }
        });
    });
}

// Initialize all interactions
document.addEventListener('DOMContentLoaded', function() {
    initQuickView();
});