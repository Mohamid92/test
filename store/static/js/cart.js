class Cart {
    constructor() {
        this.bindEvents();
    }

    bindEvents() {
        document.querySelectorAll('.add-to-cart-btn').forEach(button => {
            button.addEventListener('click', this.addToCart.bind(this));
        });
    }

    async addToCart(event) {
        const button = event.target;
        const productId = button.dataset.productId;
        
        try {
            const response = await fetch('/api/cart/add_item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1
                })
            });

            if (response.ok) {
                this.updateCartCount();
                this.showMessage('Product added to cart');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            this.showMessage('Error adding to cart', 'error');
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [cookieName, cookieVal] = cookie.trim().split('=');
                if (cookieName === name) {
                    cookieValue = decodeURIComponent(cookieVal);
                    break;
                }
            }
        }
        return cookieValue;
    }

    showMessage(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    async updateCartCount() {
        const response = await fetch('/api/cart/');
        const cart = await response.json();
        const cartCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
        document.querySelector('.cart-count').textContent = cartCount;
    }
}

// Initialize cart functionality
document.addEventListener('DOMContentLoaded', () => {
    new Cart();
});
