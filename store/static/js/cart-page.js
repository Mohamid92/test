class CartPage extends Cart {
    constructor() {
        super();
        this.bindCartPageEvents();
    }

    bindCartPageEvents() {
        document.querySelectorAll('.quantity-btn').forEach(btn => {
            btn.addEventListener('click', this.handleQuantityChange.bind(this));
        });

        document.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', this.handleRemoveItem.bind(this));
        });

        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', this.handleQuantityInput.bind(this));
        });
    }

    async handleQuantityChange(event) {
        const btn = event.target;
        const input = btn.parentNode.querySelector('.quantity-input');
        const currentValue = parseInt(input.value);
        const isPlus = btn.classList.contains('plus');
        
        input.value = isPlus ? currentValue + 1 : Math.max(1, currentValue - 1);
        await this.updateItemQuantity(input);
    }

    async handleQuantityInput(event) {
        const input = event.target;
        input.value = Math.max(1, Math.min(parseInt(input.value), parseInt(input.max)));
        await this.updateItemQuantity(input);
    }

    async updateItemQuantity(input) {
        const cartItem = input.closest('.cart-item');
        const itemId = cartItem.dataset.itemId;
        
        try {
            const response = await fetch(`/api/cart/items/${itemId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    quantity: parseInt(input.value)
                })
            });

            if (response.ok) {
                const data = await response.json();
                cartItem.querySelector('.subtotal-value').textContent = data.subtotal;
                this.updateCartTotal();
            }
        } catch (error) {
            console.error('Error updating quantity:', error);
            this.showMessage('Error updating quantity', 'error');
        }
    }

    async handleRemoveItem(event) {
        const cartItem = event.target.closest('.cart-item');
        const itemId = cartItem.dataset.itemId;

        try {
            const response = await fetch(`/api/cart/items/${itemId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            if (response.ok) {
                cartItem.remove();
                this.updateCartTotal();
                this.updateCartCount();
            }
        } catch (error) {
            console.error('Error removing item:', error);
            this.showMessage('Error removing item', 'error');
        }
    }

    async updateCartTotal() {
        const response = await fetch('/api/cart/');
        const data = await response.json();
        document.querySelector('.cart-summary .summary-row:first-child span:last-child')
            .textContent = `$${data.total}`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CartPage();
});
