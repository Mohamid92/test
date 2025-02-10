class PaymentHandler {
    constructor() {
        this.form = document.querySelector('#payment-form');
        this.methodCards = document.querySelectorAll('.payment-method-card');
        this.bindEvents();
    }

    bindEvents() {
        this.methodCards.forEach(card => {
            card.addEventListener('click', this.handleMethodSelection.bind(this));
        });

        if (this.form) {
            this.form.addEventListener('submit', this.handleSubmit.bind(this));
        }
    }

    handleMethodSelection(event) {
        const card = event.currentTarget;
        this.methodCards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        
        document.querySelector('#selected-payment-method').value = card.dataset.method;
    }

    async handleSubmit(event) {
        event.preventDefault();
        const formData = new FormData(this.form);
        
        try {
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            const data = await response.json();
            
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else if (data.error) {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('An error occurred while processing your payment');
        }
    }

    showError(message) {
        const errorDiv = document.querySelector('.payment-error');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    getCookie(name) {
        // ... existing getCookie implementation ...
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new PaymentHandler();
});
