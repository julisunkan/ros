// POS JavaScript functionality

// Product search functionality
function searchProducts() {
    const searchTerm = document.getElementById('productSearch').value.toLowerCase();
    const productItems = document.querySelectorAll('.product-item');
    
    productItems.forEach(item => {
        const productName = item.querySelector('.card-title').textContent.toLowerCase();
        if (productName.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Barcode input handling
function handleBarcode(event) {
    if (event.key === 'Enter') {
        const barcode = event.target.value.trim();
        if (barcode) {
            searchProductByBarcode(barcode);
            event.target.value = '';
        }
    }
}

// Search product by barcode
function searchProductByBarcode(barcode) {
    fetch(`/inventory/api/products/${barcode}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert('error', data.error);
            } else {
                addProductToCart(data.id, 1);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Error searching for product');
        });
}

// Add product to cart via AJAX
function addProductToCart(productId, quantity) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    
    fetch('/sales/add-to-cart', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            location.reload(); // Refresh page to update cart
        } else {
            showAlert('error', 'Error adding product to cart');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('error', 'Error adding product to cart');
    });
}

// Show alert message
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Update cart totals dynamically
function updateCartTotals() {
    const discountInput = document.querySelector('input[name="discount_amount"]');
    const discountAmount = parseFloat(discountInput.value) || 0;
    
    // Get currency symbol from the page
    const currencySymbol = document.getElementById('totalAmount').textContent.replace(/[\d.,\s]/g, '').trim() || '$';
    
    // Get subtotal from cart
    let subtotal = 0;
    const cartItems = document.querySelectorAll('.cart-item');
    cartItems.forEach(item => {
        const price = parseFloat(item.dataset.price);
        const quantity = parseInt(item.dataset.quantity);
        subtotal += price * quantity;
    });
    
    // Get tax rate from the page or use default
    const taxRateText = document.querySelector('[id*="tax"]')?.textContent || '0%';
    const taxRate = parseFloat(taxRateText.match(/[\d.]+/)?.[0] || '0') / 100;
    
    const taxAmount = (subtotal - discountAmount) * taxRate;
    const total = subtotal - discountAmount + taxAmount;
    
    // Update display
    if (document.getElementById('subtotalAmount')) {
        document.getElementById('subtotalAmount').textContent = `${currencySymbol}${(subtotal - discountAmount).toFixed(2)}`;
    }
    if (document.getElementById('discountAmount')) {
        document.getElementById('discountAmount').textContent = `${currencySymbol}${discountAmount.toFixed(2)}`;
    }
    document.getElementById('taxAmount').textContent = `${currencySymbol}${taxAmount.toFixed(2)}`;
    document.getElementById('totalAmount').textContent = `${currencySymbol}${total.toFixed(2)}`;
}

// Initialize POS functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-focus on product search
    const productSearch = document.getElementById('productSearch');
    if (productSearch) {
        productSearch.focus();
    }
    
    // Add event listener for discount input
    const discountInput = document.querySelector('input[name="discount_amount"]');
    if (discountInput) {
        discountInput.addEventListener('input', updateCartTotals);
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // F1 - Focus on search
        if (event.key === 'F1') {
            event.preventDefault();
            productSearch.focus();
        }
        
        // F2 - Focus on barcode
        if (event.key === 'F2') {
            event.preventDefault();
            const barcodeInput = document.getElementById('barcodeInput');
            if (barcodeInput) {
                barcodeInput.focus();
            }
        }
        
        // F3 - Clear cart
        if (event.key === 'F3') {
            event.preventDefault();
            const clearCartBtn = document.querySelector('form[action*="clear-cart"] button');
            if (clearCartBtn && confirm('Clear entire cart?')) {
                clearCartBtn.click();
            }
        }
    });
});

// Quick quantity update
function updateQuantity(productId, newQuantity) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/sales/update-cart';
    
    const productInput = document.createElement('input');
    productInput.type = 'hidden';
    productInput.name = 'product_id';
    productInput.value = productId;
    
    const quantityInput = document.createElement('input');
    quantityInput.type = 'hidden';
    quantityInput.name = 'quantity';
    quantityInput.value = newQuantity;
    
    form.appendChild(productInput);
    form.appendChild(quantityInput);
    document.body.appendChild(form);
    form.submit();
}

// Format currency
function formatCurrency(amount) {
    // Get currency from global variable set in template
    const currency = window.currentCurrency || 'USD';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}
