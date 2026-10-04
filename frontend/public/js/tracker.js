/**
 * Web User Behaviour Analysis - Client-Side Behavioral Tracking Engine
 * Developed for Final Year Project (Semester VII)
 * Features:
 *  - Visitor Fingerprint & Session lifecycle management
 *  - Pageview & Dwell Time tracking
 *  - Clickstream tracking (Target elements, tags, text, coordinates)
 *  - Scroll depth monitoring
 *  - Background Heartbeat & Keepalive beacons
 */

(function () {
    'use strict';

    const TRACKER_CONFIG = {
        apiBase: '/api/track',
        heartbeatIntervalMs: 10000, // 10s heartbeat
        sessionTimeoutMs: 30 * 60 * 1000 // 30 minutes inactivity
    };

    // Helper: Generate UUID
    function generateUUID() {
        return 'u_' + Math.random().toString(36).substring(2, 9) + Date.now().toString(36);
    }

    // 1. Visitor Identification (Persistent across visits)
    function getVisitorId() {
        let vid = localStorage.getItem('wuba_visitor_id');
        if (!vid) {
            vid = 'vis_' + generateUUID();
            localStorage.setItem('wuba_visitor_id', vid);
        }
        return vid;
    }

    // 2. Session Identification (Expires after inactivity)
    function getSessionId() {
        const now = Date.now();
        let sid = sessionStorage.getItem('wuba_session_id');
        let lastActivity = parseInt(sessionStorage.getItem('wuba_last_activity') || '0', 10);

        if (!sid || (now - lastActivity > TRACKER_CONFIG.sessionTimeoutMs)) {
            sid = 'sess_' + generateUUID();
            sessionStorage.setItem('wuba_session_id', sid);
            sessionStorage.setItem('wuba_session_start', now.toString());
        }

        sessionStorage.setItem('wuba_last_activity', now.toString());
        return sid;
    }

    // 3. Device & Browser Detection
    function getClientInfo() {
        const ua = navigator.userAgent;
        let device = 'Desktop';
        if (/Mobi|Android/i.test(ua)) device = 'Mobile';
        else if (/Tablet|iPad/i.test(ua)) device = 'Tablet';

        let browser = 'Unknown';
        if (ua.includes('Firefox')) browser = 'Firefox';
        else if (ua.includes('Edg')) browser = 'Edge';
        else if (ua.includes('Chrome')) browser = 'Chrome';
        else if (ua.includes('Safari')) browser = 'Safari';

        let os = 'Unknown OS';
        if (ua.includes('Win')) os = 'Windows';
        else if (ua.includes('Mac')) os = 'macOS';
        else if (ua.includes('Linux')) os = 'Linux';
        else if (ua.includes('Android')) os = 'Android';
        else if (ua.includes('iPhone') || ua.includes('iPad')) os = 'iOS';

        return {
            device_type: device,
            browser: browser,
            os: os,
            screen_resolution: `${window.screen.width}x${window.screen.height}`
        };
    }

    // API Post Helper
    function sendPayload(endpoint, payload, useBeacon = false) {
        const url = `${TRACKER_CONFIG.apiBase}/${endpoint}`;
        const dataStr = JSON.stringify(payload);

        if (useBeacon && navigator.sendBeacon) {
            const blob = new Blob([dataStr], { type: 'application/json' });
            navigator.sendBeacon(url, blob);
        } else {
            fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: dataStr,
                keepalive: true
            }).catch(err => console.debug('[WUBA Tracker] Network sync note:', err));
        }
    }

    // Tracker Engine Core
    class UserBehaviorTracker {
        constructor() {
            this.visitorId = getVisitorId();
            this.sessionId = getSessionId();
            this.pageStartTime = Date.now();
            this.maxScrollDepth = 0;
            this.pageUrl = window.location.pathname || '/';
            this.pageTitle = document.title || 'Untitled Page';
            this.referrer = document.referrer || 'Direct';

            this.init();
        }

        init() {
            // Register visitor
            const clientInfo = getClientInfo();
            sendPayload('init', {
                visitor_id: this.visitorId,
                ...clientInfo
            });

            // Log Initial Pageview
            this.logPageView();

            // Setup listeners
            this.setupClickTracking();
            this.setupScrollTracking();
            this.setupHeartbeat();
            this.setupUnloadTracking();
            this.setupProductPageTracking();

            console.log(`[WUBA Tracker Active] Session: ${this.sessionId} | Visitor: ${this.visitorId}`);
        }

        trackProduct(productData) {
            sendPayload('product', {
                session_id: this.sessionId,
                visitor_id: this.visitorId,
                product_id: productData.product_id || 'prod_unknown',
                product_name: productData.product_name || 'Unknown Product',
                category: productData.category || 'General',
                price: parseFloat(productData.price || 0),
                event_type: productData.event_type || 'view',
                dwell_time: parseFloat(productData.dwell_time || 0)
            });
        }

        setupProductPageTracking() {
            // Check if current page is a product details page
            const prodMeta = document.querySelector('[data-product-page]');
            if (prodMeta) {
                const prodId = prodMeta.dataset.productId || 'prod_1';
                const prodName = prodMeta.dataset.productName || document.title;
                const category = prodMeta.dataset.category || 'Audio';
                const price = parseFloat(prodMeta.dataset.price || 0);

                this.trackProduct({
                    product_id: prodId,
                    product_name: prodName,
                    category: category,
                    price: price,
                    event_type: 'view',
                    dwell_time: 0
                });
            }
        }

        logPageView() {
            sendPayload('pageview', {
                session_id: this.sessionId,
                visitor_id: this.visitorId,
                page_url: this.pageUrl,
                page_title: this.pageTitle,
                referrer: this.referrer,
                dwell_time: 0,
                scroll_depth: this.maxScrollDepth
            });
        }

        setupClickTracking() {
            document.addEventListener('click', (e) => {
                sessionStorage.setItem('wuba_last_activity', Date.now().toString());

                // Find element details
                const target = e.target.closest('a, button, input, [role="button"], .clickable, [data-product-id]') || e.target;
                const elementId = target.id || '';
                const elementTag = target.tagName || '';
                const elementClass = target.className && typeof target.className === 'string' ? target.className : '';
                const elementText = (target.innerText || target.value || target.getAttribute('aria-label') || '').trim().substring(0, 50);

                sendPayload('click', {
                    session_id: this.sessionId,
                    visitor_id: this.visitorId,
                    page_url: this.pageUrl,
                    element_id: elementId,
                    element_tag: elementTag,
                    element_class: elementClass,
                    element_text: elementText,
                    x_pos: Math.round(e.pageX),
                    y_pos: Math.round(e.pageY)
                });

                // Check for product-specific click interaction
                const prodEl = target.closest('[data-product-id]');
                if (prodEl) {
                    const prodId = prodEl.dataset.productId;
                    const prodName = prodEl.dataset.productName || prodEl.innerText;
                    const category = prodEl.dataset.category || 'General';
                    const price = parseFloat(prodEl.dataset.price || 0);
                    let eventType = prodEl.dataset.action || 'click_details';

                    if (elementId.includes('cart') || elementText.toLowerCase().includes('cart')) {
                        eventType = 'add_to_cart';
                    } else if (elementId.includes('buy') || elementText.toLowerCase().includes('buy')) {
                        eventType = 'buy_now';
                    }

                    this.trackProduct({
                        product_id: prodId,
                        product_name: prodName,
                        category: category,
                        price: price,
                        event_type: eventType,
                        dwell_time: 0
                    });
                }
            }, true);
        }

        setupScrollTracking() {
            let ticking = false;
            window.addEventListener('scroll', () => {
                if (!ticking) {
                    window.requestAnimationFrame(() => {
                        const h = document.documentElement;
                        const b = document.body;
                        const st = 'scrollTop' in h ? h.scrollTop : b.scrollTop;
                        const sh = 'scrollHeight' in h ? h.scrollHeight : b.scrollHeight;
                        const ch = h.clientHeight;
                        const percent = Math.min(100, Math.round((st / (sh - ch)) * 100)) || 0;
                        if (percent > this.maxScrollDepth) {
                            this.maxScrollDepth = percent;
                        }
                        ticking = false;
                    });
                    ticking = true;
                }
            });
        }

        setupHeartbeat() {
            setInterval(() => {
                const sessionStart = parseInt(sessionStorage.getItem('wuba_session_start') || Date.now().toString(), 10);
                const elapsedSeconds = Math.round((Date.now() - sessionStart) / 1000);

                sendPayload('heartbeat', {
                    session_id: this.sessionId,
                    duration_seconds: elapsedSeconds
                });
            }, TRACKER_CONFIG.heartbeatIntervalMs);
        }

        setupUnloadTracking() {
            const handleUnload = () => {
                const dwell = Math.round((Date.now() - this.pageStartTime) / 1000);
                sendPayload('pageview', {
                    session_id: this.sessionId,
                    visitor_id: this.visitorId,
                    page_url: this.pageUrl,
                    page_title: this.pageTitle,
                    referrer: this.referrer,
                    dwell_time: dwell,
                    scroll_depth: this.maxScrollDepth
                }, true);
            };

            window.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'hidden') {
                    handleUnload();
                }
            });
            window.addEventListener('beforeunload', handleUnload);
        }
    }

    // Auto-mount tracker when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new UserBehaviorTracker());
    } else {
        new UserBehaviorTracker();
    }
})();
