// POS Terminal Logic
let cart = [];
let selectedMedicineForBatchModal = null;

document.addEventListener('DOMContentLoaded', function() {
    loadPOSMedicines('');

    // Search input keyup
    const searchInput = document.getElementById('posSearchInput');
    if (searchInput) {
        let timeout = null;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                loadPOSMedicines(this.value.trim());
            }, 300);
        });
    }

    // Billing form fields listener
    const taxInput = document.getElementById('posTaxInput');
    const discountInput = document.getElementById('posDiscountInput');

    if (taxInput) taxInput.addEventListener('input', updatePOSCartTotals);
    if (discountInput) discountInput.addEventListener('input', updatePOSCartTotals);

    // Checkout button
    const checkoutBtn = document.getElementById('posCheckoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', submitPOSOrder);
    }
});

function loadPOSMedicines(query) {
    const grid = document.getElementById('posMedicinesGrid');
    if (!grid) return;

    grid.innerHTML = '<div class="text-center py-4 text-muted"><div class="spinner-border spinner-border-sm text-primary"></div> Searching medicines...</div>';

    fetch(`/sales/api/search-medicines?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                grid.innerHTML = '<div class="text-center py-4 text-muted"><i class="fas fa-box-open fa-2x mb-2 d-block"></i> No available medicines found matching search.</div>';
                return;
            }

            let html = '<div class="row g-2">';
            data.forEach(med => {
                html += `
                    <div class="col-6 col-md-6 col-lg-4">
                        <div class="pos-item-card h-100" onclick="openBatchSelectionModal(${med.id}, '${escapeQuotes(med.name)}', '${escapeQuotes(med.generic_name || '')}', '${med.unit}')">
                            <div class="fw-bold text-dark text-truncate">${med.name}</div>
                            <div class="small text-muted text-truncate">${med.generic_name || 'Generic'}</div>
                            <div class="d-flex justify-content-between align-items-center mt-2">
                                <span class="badge bg-light text-dark border">${med.category_name}</span>
                                <span class="badge bg-success-subtle text-success border border-success">${med.total_available_stock} ${med.unit}s available</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            grid.innerHTML = html;
        })
        .catch(err => {
            console.error(err);
            grid.innerHTML = '<div class="text-center py-4 text-danger">Failed to load medicines.</div>';
        });
}

function openBatchSelectionModal(medId, medName, genericName, unit) {
    selectedMedicineForBatchModal = { id: medId, name: medName, generic: genericName, unit: unit };
    const batchListContainer = document.getElementById('modalBatchList');
    document.getElementById('modalMedicineTitle').innerText = medName;
    batchListContainer.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary"></div> Loading available batches...</div>';

    const batchModal = new bootstrap.Modal(document.getElementById('batchSelectModal'));
    batchModal.show();

    fetch(`/sales/api/get-batches/${medId}`)
        .then(res => res.json())
        .then(batches => {
            if (batches.length === 0) {
                batchListContainer.innerHTML = '<div class="alert alert-warning">No active batches with stock available for this medicine.</div>';
                return;
            }

            let html = '<div class="list-group">';
            batches.forEach(b => {
                html += `
                    <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                        <div>
                            <div class="fw-bold">Batch #${b.batch_no}</div>
                            <div class="small text-muted">Expires: ${b.expiry_date} | Stock: ${b.remaining_quantity} ${unit}s</div>
                            <div class="text-primary fw-bold">₹${parseFloat(b.selling_price).toFixed(2)} / ${unit}</div>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-primary px-3" onclick="addToPOSCart(${medId}, '${escapeQuotes(medName)}', ${b.id}, '${b.batch_no}', ${b.selling_price}, ${b.remaining_quantity})">
                                <i class="fas fa-plus"></i> Select
                            </button>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            batchListContainer.innerHTML = html;
        });
}

function addToPOSCart(medId, medName, batchId, batchNo, price, maxQty) {
    const existingIndex = cart.findIndex(item => item.batch_id === batchId);
    if (existingIndex > -1) {
        if (cart[existingIndex].quantity + 1 > maxQty) {
            alert(`Cannot add more. Maximum available stock in Batch #${batchNo} is ${maxQty}.`);
            return;
        }
        cart[existingIndex].quantity += 1;
    } else {
        cart.push({
            medicine_id: medId,
            medicine_name: medName,
            batch_id: batchId,
            batch_no: batchNo,
            unit_price: parseFloat(price),
            quantity: 1,
            max_qty: maxQty
        });
    }

    // Hide modal
    const batchModalEl = document.getElementById('batchSelectModal');
    const modalInstance = bootstrap.Modal.getInstance(batchModalEl);
    if (modalInstance) modalInstance.hide();

    renderPOSCart();
}

function updateItemQuantity(batchId, delta) {
    const item = cart.find(i => i.batch_id === batchId);
    if (!item) return;

    const newQty = item.quantity + delta;
    if (newQty <= 0) {
        removeFromCart(batchId);
        return;
    }
    if (newQty > item.max_qty) {
        alert(`Maximum available stock for Batch #${item.batch_no} is ${item.max_qty}.`);
        return;
    }
    item.quantity = newQty;
    renderPOSCart();
}

function removeFromCart(batchId) {
    cart = cart.filter(i => i.batch_id !== batchId);
    renderPOSCart();
}

function renderPOSCart() {
    const cartBody = document.getElementById('posCartTableBody');
    if (!cartBody) return;

    if (cart.length === 0) {
        cartBody.innerHTML = `
            <tr class="pos-empty-row">
                <td colspan="5" class="text-center py-4 text-muted">
                    <i class="fas fa-shopping-cart fa-2x mb-2 d-block"></i>
                    Cart is empty. Click on a medicine to add items.
                </td>
            </tr>
        `;
        updatePOSCartTotals();
        return;
    }

    let html = '';
    cart.forEach(item => {
        const itemTotal = (item.quantity * item.unit_price).toFixed(2);
        html += `
            <tr class="pos-cart-row">
                <td class="pos-cart-item" data-label="Medicine">
                    <div class="fw-bold text-break">${item.medicine_name}</div>
                    <small class="text-muted">Batch: ${item.batch_no}</small>
                </td>
                <td class="pos-cart-price" data-label="Price">₹${item.unit_price.toFixed(2)}</td>
                <td class="pos-cart-quantity" data-label="Quantity">
                    <div class="input-group input-group-sm pos-quantity-control">
                        <button class="btn btn-outline-secondary" aria-label="Decrease ${item.medicine_name} quantity" onclick="updateItemQuantity(${item.batch_id}, -1)">-</button>
                        <input type="text" class="form-control text-center px-1" value="${item.quantity}" readonly>
                        <button class="btn btn-outline-secondary" aria-label="Increase ${item.medicine_name} quantity" onclick="updateItemQuantity(${item.batch_id}, 1)">+</button>
                    </div>
                </td>
                <td class="fw-bold pos-cart-total" data-label="Total">₹${itemTotal}</td>
                <td class="pos-cart-remove">
                    <button class="btn btn-sm btn-outline-danger" aria-label="Remove ${item.medicine_name} from cart" title="Remove item" onclick="removeFromCart(${item.batch_id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    cartBody.innerHTML = html;
    updatePOSCartTotals();
}

function updatePOSCartTotals() {
    let subtotal = 0.0;
    cart.forEach(item => {
        subtotal += item.quantity * item.unit_price;
    });

    const taxPercent = parseFloat(document.getElementById('posTaxInput')?.value || 0.0);
    const discountPercent = parseFloat(document.getElementById('posDiscountInput')?.value || 0.0);
    const tax = Math.round(subtotal * taxPercent) / 100;
    const discount = Math.round(subtotal * discountPercent) / 100;
    const unroundedTotal = Math.max(0, subtotal + tax - discount);
    const grandTotal = Math.floor(unroundedTotal + 0.5);
    const roundValue = grandTotal - unroundedTotal;

    if (document.getElementById('posSubtotalText')) document.getElementById('posSubtotalText').innerText = '₹' + subtotal.toFixed(2);
    if (document.getElementById('posTaxAmountText')) document.getElementById('posTaxAmountText').innerText = '₹' + tax.toFixed(2);
    if (document.getElementById('posDiscountAmountText')) document.getElementById('posDiscountAmountText').innerText = '-₹' + discount.toFixed(2);
    if (document.getElementById('posRoundValueText')) {
        const roundSign = roundValue > 0 ? '+' : roundValue < 0 ? '-' : '';
        document.getElementById('posRoundValueText').innerText = roundSign + '₹' + Math.abs(roundValue).toFixed(2);
    }
    if (document.getElementById('posGrandTotalText')) document.getElementById('posGrandTotalText').innerText = '₹' + grandTotal.toFixed(0);
}

function submitPOSOrder() {
    if (cart.length === 0) {
        alert('Cart is empty. Please add items before completing bill.');
        return;
    }

    const customerName = document.getElementById('posCustomerName')?.value.trim() || 'Walk-in Customer';
    const customerPhone = document.getElementById('posCustomerPhone')?.value.trim() || '';
    const doctorName = document.getElementById('posDoctorName')?.value.trim() || '';
    const taxPercent = parseFloat(document.getElementById('posTaxInput')?.value || 0.0);
    const discountPercent = parseFloat(document.getElementById('posDiscountInput')?.value || 0.0);
    const paymentMethod = document.getElementById('posPaymentMethod')?.value || 'Cash';

    if (![taxPercent, discountPercent].every(rate => Number.isFinite(rate) && rate >= 0 && rate <= 100)) {
        alert('Tax and discount must be between 0% and 100%.');
        return;
    }

    const btn = document.getElementById('posCheckoutBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing...';

    const payload = {
        customer_name: customerName,
        customer_phone: customerPhone,
        doctor_name: doctorName,
        tax_percent: taxPercent,
        discount_percent: discountPercent,
        payment_method: paymentMethod,
        items: cart
    };

    fetch('/sales/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            alert('Error generating invoice: ' + data.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-print me-1"></i> Generate & Print Invoice';
        }
    })
    .catch(err => {
        console.error(err);
        alert('Server error processing sale.');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-print me-1"></i> Generate & Print Invoice';
    });
}

function escapeQuotes(str) {
    if (!str) return '';
    return str.replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
