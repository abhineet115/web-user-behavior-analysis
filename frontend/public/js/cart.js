/**
 * Web User Behaviour Analysis - Shopping Cart & Checkout Engine
 * Manages localStorage cart state and triggers tracking events for cart actions.
 */

const WUBA_CATALOG = {
    'prod_1': { id: 'prod_1', name: 'ANC Pro Headphones', category: 'Audio', price: 199, icon: '🎧', desc: 'Wireless ANC Headphones with 40h playtime.' },
    'prod_2': { id: 'prod_2', name: 'Pulse Smartwatch X', category: 'Wearables', price: 149, icon: '⌚', desc: 'AMOLED health & fitness tracker.' },
    'prod_3': { id: 'prod_3', name: 'Mechanical Keyboard RGB', category: 'Accessories', price: 89, icon: '⌨️', desc: 'Tactile mechanical switches with wireless BT.' },
    'prod_4': { id: 'prod_4', name: 'Ergo Precision Mouse', category: 'Accessories', price: 69, icon: '🖱️', desc: 'Ergonomic high-precision laser sensor.' },
    'prod_5': { id: 'prod_5', name: 'Developer Workstation', category: 'Electronics', price: 1499, icon: '💻', desc: 'Core i9, 32GB RAM, 1TB NVMe, RTX Graphics.' },
    'prod_6': { id: 'prod_6', name: 'Studio Monitor Speaker', category: 'Audio', price: 249, icon: '🔊', desc: 'Hi-Res balanced studio monitors.' },
    'prod_7': { id: 'prod_7', name: 'UltraWide Curved 4K Monitor', category: 'Electronics', price: 649, icon: '🖥️', desc: '34-inch 144Hz HDR curved IPS display.' },
    'prod_8': { id: 'prod_8', name: 'Studio Condenser Mic', category: 'Audio', price: 129, icon: '🎙️', desc: 'Cardioid USB-C studio mic with gain dial.' },
    'prod_9': { id: 'prod_9', name: 'Smart Health Fitness Ring', category: 'Wearables', price: 199, icon: '💍', desc: 'Titanium smart ring tracking sleep & readiness.' },
    'prod_10': { id: 'prod_10', name: 'Thunderbolt 4 Multi-Dock', category: 'Accessories', price: 179, icon: '🔌', desc: '14-in-1 dock with 100W PD and dual 4K display.' },
    'prod_11': { id: 'prod_11', name: 'True Wireless Sport Earbuds', category: 'Audio', price: 119, icon: '🎵', desc: 'IPX7 sweatproof sports earbuds with ear hooks.' },
    'prod_12': { id: 'prod_12', name: 'Rugged Portable SSD 2TB', category: 'Electronics', price: 159, icon: '💾', desc: '1050MB/s NVMe drop & splash resistant SSD.' },
    'prod_13': { id: 'prod_13', name: '4K Action Camera Pro', category: 'Electronics', price: 329, icon: '📷', desc: '4K 60fps, waterproof 30m, 3-axis stabilization.' },
    'prod_14': { id: 'prod_14', name: 'Smart AR Glasses', category: 'Wearables', price: 249, icon: '🥽', desc: 'Lightweight AR overlay with voice commands & 8h battery.' },
    'prod_15': { id: 'prod_15', name: 'Wireless Charging Pad Pro', category: 'Accessories', price: 49, icon: '🔋', desc: '15W Qi2 fast wireless charging with LED ring.' }
};

const CartService = {
    getCart() {
        try {
            return JSON.parse(localStorage.getItem('wuba_cart') || '[]');
        } catch (e) {
            return [];
        }
    },

    saveCart(cart) {
        localStorage.setItem('wuba_cart', JSON.stringify(cart));
        this.updateNavBadge();
    },

    addItem(productId, qty = 1) {
        const item = WUBA_CATALOG[productId];
        if (!item) return;

        let cart = this.getCart();
        const existing = cart.find(c => c.id === productId);

        if (existing) {
            existing.qty += qty;
        } else {
            cart.push({
                id: item.id,
                name: item.name,
                category: item.category,
                price: item.price,
                icon: item.icon,
                qty: qty
            });
        }

        this.saveCart(cart);

        // Send product tracking event
        if (window.wubaTracker && typeof window.wubaTracker.trackProduct === 'function') {
            window.wubaTracker.trackProduct({
                product_id: item.id,
                product_name: item.name,
                category: item.category,
                price: item.price,
                event_type: 'add_to_cart',
                dwell_time: 0
            });
        }
    },

    removeItem(productId) {
        let cart = this.getCart().filter(c => c.id !== productId);
        this.saveCart(cart);
    },

    updateQty(productId, qty) {
        let cart = this.getCart();
        const item = cart.find(c => c.id === productId);
        if (item) {
            item.qty = Math.max(1, qty);
            this.saveCart(cart);
        }
    },

    clearCart() {
        localStorage.removeItem('wuba_cart');
        this.updateNavBadge();
    },

    getTotalCount() {
        return this.getCart().reduce((sum, item) => sum + item.qty, 0);
    },

    getSubtotal() {
        return this.getCart().reduce((sum, item) => sum + (item.price * item.qty), 0);
    },

    updateNavBadge() {
        const badges = document.querySelectorAll('.cart-count-badge');
        const count = this.getTotalCount();
        badges.forEach(badge => {
            badge.innerText = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        });
    }
};

// Initialize nav badge on page load
document.addEventListener('DOMContentLoaded', () => {
    // If cart is empty, pre-populate with 1 popular item for a welcoming first demo experience
    if (CartService.getCart().length === 0 && !sessionStorage.getItem('wuba_cart_initialized')) {
        CartService.addItem('prod_1', 1);
        sessionStorage.setItem('wuba_cart_initialized', 'true');
    }
    CartService.updateNavBadge();
});
