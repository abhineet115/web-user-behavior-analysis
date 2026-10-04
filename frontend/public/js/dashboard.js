/**
 * Web User Behaviour Analysis - Semester VII Progress Dashboard Controller
 * Fetches real-time metrics, per-product tracking data, Chart.js visualizations,
 * and preprocessed behavioral analytics data.
 */

let funnelChartInstance = null;
let categoryChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    loadSummaryMetrics();
    loadProductMetrics();
    loadProcessedMetrics();

    // Auto-refresh metrics every 5 seconds for live demo
    setInterval(() => {
        loadSummaryMetrics();
        loadProductMetrics();
    }, 5000);

    const seedBtn = document.getElementById('btn-seed-data');
    if (seedBtn) {
        seedBtn.addEventListener('click', runSeedData);
    }

    const refreshPrepBtn = document.getElementById('btn-refresh-preprocess');
    if (refreshPrepBtn) {
        refreshPrepBtn.addEventListener('click', loadProcessedMetrics);
    }
});

async function loadSummaryMetrics() {
    try {
        const res = await fetch('/api/metrics/summary');
        const data = await res.json();

        // Update KPIs
        document.getElementById('kpi-visitors').innerText = data.total_visitors.toLocaleString();
        document.getElementById('kpi-sessions').innerText = data.total_sessions.toLocaleString();
        document.getElementById('kpi-pageviews').innerText = data.total_pageviews.toLocaleString();
        document.getElementById('kpi-clicks').innerText = data.total_clicks.toLocaleString();
        document.getElementById('kpi-duration').innerText = `${data.avg_duration_seconds}s`;
        document.getElementById('kpi-bounce').innerText = `${data.bounce_rate}%`;

        // Render Popular Pages
        const popularList = document.getElementById('popular-pages-list');
        if (popularList) {
            popularList.innerHTML = '';
            if (data.popular_pages && data.popular_pages.length > 0) {
                data.popular_pages.forEach((p, idx) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><strong>#${idx + 1}</strong> <span class="badge bg-secondary ms-1">${p.page_url}</span></td>
                        <td><span class="text-primary fw-bold">${p.views}</span> visits</td>
                        <td>${Math.round(p.avg_dwell || 0)}s avg dwell</td>
                    `;
                    popularList.appendChild(row);
                });
            } else {
                popularList.innerHTML = '<tr><td colspan="3" class="text-muted text-center">No page views recorded yet.</td></tr>';
            }
        }

        // Render Live Activity Feed
        const feedList = document.getElementById('live-activity-feed');
        if (feedList) {
            feedList.innerHTML = '';
            if (data.recent_activity && data.recent_activity.length > 0) {
                data.recent_activity.forEach(act => {
                    const badgeClass = act.type === 'page_view' ? 'bg-primary' : 'bg-success';
                    const icon = act.type === 'page_view' ? '📄' : '🖱️';
                    const item = document.createElement('div');
                    item.className = 'd-flex justify-content-between align-items-center py-2 border-bottom border-dark';
                    item.innerHTML = `
                        <div>
                            <span class="badge ${badgeClass} me-2">${icon} ${act.type}</span>
                            <span class="text-light small">${act.detail}</span>
                        </div>
                        <span class="text-muted small">${act.timestamp.split(' ')[1] || act.timestamp}</span>
                    `;
                    feedList.appendChild(item);
                });
            } else {
                feedList.innerHTML = '<div class="text-muted small">No recent activity detected. Click around the demo site!</div>';
            }
        }
    } catch (err) {
        console.error('Error loading summary metrics:', err);
    }
}

async function loadProductMetrics() {
    try {
        const res = await fetch('/api/metrics/products');
        const data = await res.json();

        // Update badge
        const badgeElem = document.getElementById('product-summary-badge');
        if (badgeElem && data.summary) {
            badgeElem.innerHTML = `
                <span class="text-info">Impressions: <strong>${data.summary.total_product_views}</strong></span> • 
                <span class="text-warning">Cart Adds: <strong>${data.summary.total_add_to_cart}</strong></span> • 
                <span class="text-success">Purchases: <strong>${data.summary.total_purchases}</strong></span> • 
                <span class="text-light">Conv Rate: <strong>${data.summary.overall_conversion_rate}%</strong></span>
            `;
        }

        // Populate Table
        const tableBody = document.getElementById('product-performance-body');
        if (tableBody) {
            tableBody.innerHTML = '';
            if (data.products && data.products.length > 0) {
                data.products.forEach(p => {
                    const row = document.createElement('tr');
                    const convRate = p.conversion_rate || 0;
                    let convBadge = 'bg-secondary';
                    if (convRate >= 20) convBadge = 'bg-success';
                    else if (convRate >= 10) convBadge = 'bg-primary';
                    else if (convRate > 0) convBadge = 'bg-warning text-dark';

                    row.innerHTML = `
                        <td><strong>${p.product_name}</strong> <code class="small text-secondary ms-1">(${p.product_id})</code></td>
                        <td><span class="badge bg-dark border border-secondary">${p.category}</span></td>
                        <td>$${p.price}</td>
                        <td><span class="fw-bold text-info">${p.views || 0}</span></td>
                        <td>${p.clicks || 0}</td>
                        <td><span class="text-warning fw-semibold">${p.add_to_cart || 0}</span></td>
                        <td><span class="text-success fw-bold">${p.purchases || 0}</span></td>
                        <td>${p.avg_dwell_seconds || 0}s</td>
                        <td>
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge ${convBadge}">${convRate}%</span>
                                <div class="progress flex-grow-1" style="height: 6px; background-color: #1f2937;">
                                    <div class="progress-bar bg-success" role="progressbar" style="width: ${Math.min(100, convRate)}%"></div>
                                </div>
                            </div>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-3">No product interactions logged yet. Browse products or click "Generate Test Traffic" above!</td></tr>';
            }
        }

        // Render Graphs using Chart.js
        renderProductCharts(data);

    } catch (err) {
        console.error('Error loading product metrics:', err);
    }
}

function renderProductCharts(data) {
    if (!window.Chart) return;

    const products = data.products || [];
    const categories = data.categories || [];

    // Chart 1: Product Engagement & Conversion Funnel Bar Chart
    const funnelCtx = document.getElementById('productFunnelChart');
    if (funnelCtx) {
        const labels = products.map(p => p.product_name.length > 15 ? p.product_name.substring(0, 14) + '...' : p.product_name);
        const viewsData = products.map(p => p.views || 0);
        const clicksData = products.map(p => p.clicks || 0);
        const cartData = products.map(p => p.add_to_cart || 0);
        const purchaseData = products.map(p => p.purchases || 0);

        if (funnelChartInstance) {
            funnelChartInstance.data.labels = labels;
            funnelChartInstance.data.datasets[0].data = viewsData;
            funnelChartInstance.data.datasets[1].data = clicksData;
            funnelChartInstance.data.datasets[2].data = cartData;
            funnelChartInstance.data.datasets[3].data = purchaseData;
            funnelChartInstance.update();
        } else {
            funnelChartInstance = new Chart(funnelCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Views (Impressions)', data: viewsData, backgroundColor: '#3b82f6', borderRadius: 4 },
                        { label: 'Detail Clicks', data: clicksData, backgroundColor: '#8b5cf6', borderRadius: 4 },
                        { label: 'Add to Cart', data: cartData, backgroundColor: '#f59e0b', borderRadius: 4 },
                        { label: 'Purchases', data: purchaseData, backgroundColor: '#10b981', borderRadius: 4 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#9ca3af', font: { size: 11 } }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#9ca3af', font: { size: 10 } },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y: {
                            ticks: { color: '#9ca3af' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        }
                    }
                }
            });
        }
    }

    // Chart 2: Category Share Doughnut Chart
    const catCtx = document.getElementById('categoryShareChart');
    if (catCtx) {
        const catLabels = categories.map(c => c.category);
        const catValues = categories.map(c => c.views || c.total_events || 0);
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899'];

        if (categoryChartInstance) {
            categoryChartInstance.data.labels = catLabels;
            categoryChartInstance.data.datasets[0].data = catValues;
            categoryChartInstance.update();
        } else {
            categoryChartInstance = new Chart(catCtx, {
                type: 'doughnut',
                data: {
                    labels: catLabels,
                    datasets: [{
                        data: catValues,
                        backgroundColor: colors.slice(0, catLabels.length),
                        borderColor: '#111827',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#9ca3af', font: { size: 11 } }
                        }
                    }
                }
            });
        }
    }
}

async function loadProcessedMetrics() {
    const tableBody = document.getElementById('preprocessed-table-body');
    const statusNotice = document.getElementById('preprocess-status');

    if (statusNotice) statusNotice.innerText = 'Processing data via Pandas & NumPy...';

    try {
        const res = await fetch('/api/metrics/processed');
        const result = await res.json();

        if (result.status === 'success' && result.samples) {
            if (statusNotice) statusNotice.innerText = `Pipeline active: ${result.summary.total_sessions} sessions analyzed. Avg Engagement Score: ${result.summary.avg_engagement_score}/100`;

            // Segment Badges
            const segDist = result.summary.segment_distribution || {};
            const segElem = document.getElementById('segment-distribution-container');
            if (segElem) {
                segElem.innerHTML = `
                    <span class="tag-segment tag-high me-2">High: ${segDist['High Engagement (Power User)'] || 0}</span>
                    <span class="tag-segment tag-mod me-2">Moderate: ${segDist['Moderate Engagement (Explorer)'] || 0}</span>
                    <span class="tag-segment tag-low">Low: ${segDist['Low Engagement (Bouncer / Casual)'] || 0}</span>
                `;
            }

            // Populate table
            if (tableBody) {
                tableBody.innerHTML = '';
                result.samples.forEach(row => {
                    const tr = document.createElement('tr');
                    let tagClass = 'tag-low';
                    if (row.behavior_segment && row.behavior_segment.includes('High')) tagClass = 'tag-high';
                    else if (row.behavior_segment && row.behavior_segment.includes('Moderate')) tagClass = 'tag-mod';

                    tr.innerHTML = `
                        <td><code class="text-info">${(row.session_id || '').substring(0, 10)}...</code></td>
                        <td><code class="text-secondary">${(row.visitor_id || '').substring(0, 10)}...</code></td>
                        <td>${row.duration_seconds}s</td>
                        <td>${row.page_views_count}</td>
                        <td>${row.click_count}</td>
                        <td>${row.avg_scroll_depth || 0}%</td>
                        <td><strong>${row.engagement_score}</strong></td>
                        <td><span class="tag-segment ${tagClass}">${row.behavior_segment || 'N/A'}</span></td>
                    `;
                    tableBody.appendChild(tr);
                });
            }
        } else {
            if (statusNotice) statusNotice.innerText = 'No sessions available to preprocess yet. Click "Generate Test Traffic" button above!';
        }
    } catch (err) {
        if (statusNotice) statusNotice.innerText = 'Preprocessing error: ' + err.message;
    }
}

async function runSeedData() {
    const btn = document.getElementById('btn-seed-data');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Generating...';
    }

    try {
        const res = await fetch('/api/admin/seed', { method: 'POST' });
        const data = await res.json();
        alert(data.message || 'Data generated!');
        loadSummaryMetrics();
        loadProductMetrics();
        loadProcessedMetrics();
    } catch (err) {
        alert('Failed to seed data: ' + err.message);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '⚡ Generate Realistic Test Traffic';
        }
    }
}
