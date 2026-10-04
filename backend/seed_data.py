import random
import uuid
from datetime import datetime, timedelta
from database import init_db, register_user, record_page_view, record_click_event, update_session_heartbeat, record_product_event

PRODUCTS_CATALOG = [
    {'id': 'prod_1', 'name': 'ANC Pro Headphones', 'category': 'Audio', 'price': 199.0},
    {'id': 'prod_2', 'name': 'Pulse Smartwatch X', 'category': 'Wearables', 'price': 149.0},
    {'id': 'prod_3', 'name': 'Mechanical Keyboard RGB', 'category': 'Accessories', 'price': 89.0},
    {'id': 'prod_4', 'name': 'Ergo Precision Mouse', 'category': 'Accessories', 'price': 69.0},
    {'id': 'prod_5', 'name': 'Developer Workstation', 'category': 'Electronics', 'price': 1499.0},
    {'id': 'prod_6', 'name': 'Studio Monitor Speaker', 'category': 'Audio', 'price': 249.0},
    {'id': 'prod_7', 'name': 'UltraWide Curved 4K Monitor', 'category': 'Electronics', 'price': 649.0},
    {'id': 'prod_8', 'name': 'Studio Condenser Mic', 'category': 'Audio', 'price': 129.0},
    {'id': 'prod_9', 'name': 'Smart Health Fitness Ring', 'category': 'Wearables', 'price': 199.0},
    {'id': 'prod_10', 'name': 'Thunderbolt 4 Multi-Dock', 'category': 'Accessories', 'price': 179.0},
    {'id': 'prod_11', 'name': 'True Wireless Sport Earbuds', 'category': 'Audio', 'price': 119.0},
    {'id': 'prod_12', 'name': 'Rugged Portable SSD 2TB', 'category': 'Electronics', 'price': 159.0}
]

PAGES = [
    ('/', 'Home - Modern E-Commerce Platform'),
    ('/products.html', 'Products Catalog - All Categories'),
    ('/product-details.html?id=prod_1', 'ANC Pro Headphones - Product Details'),
    ('/product-details.html?id=prod_2', 'Pulse Smartwatch X - Product Details'),
    ('/product-details.html?id=prod_5', 'Developer Workstation - Product Details'),
    ('/product-details.html?id=prod_7', 'UltraWide 4K Monitor - Product Details'),
    ('/product-details.html?id=prod_9', 'Smart Fitness Ring - Product Details'),
    ('/product-details.html?id=prod_12', 'Rugged SSD 2TB - Product Details'),
    ('/blog.html', 'Tech Insights & User Behavior Case Study'),
    ('/contact.html', 'Contact Support & Feedback')
]

DEVICES = [
    ('Desktop', 'Chrome', 'Windows 11', '1920x1080'),
    ('Desktop', 'Firefox', 'Windows 10', '1920x1080'),
    ('Desktop', 'Edge', 'Windows 11', '2560x1440'),
    ('Mobile', 'Safari', 'iOS 17', '390x844'),
    ('Mobile', 'Chrome Mobile', 'Android 14', '412x915'),
    ('Tablet', 'Safari', 'iPadOS 17', '820x1180')
]

INTERACTIONS = [
    ('btn-explore', 'BUTTON', 'btn btn-primary', 'Explore Catalog'),
    ('btn-add-to-cart', 'BUTTON', 'btn btn-success', 'Add to Cart'),
    ('nav-products', 'A', 'nav-link', 'Products'),
    ('nav-blog', 'A', 'nav-link', 'Blog'),
    ('nav-contact', 'A', 'nav-link', 'Contact'),
    ('btn-newsletter', 'BUTTON', 'btn btn-outline-light', 'Subscribe'),
    ('faq-toggle-1', 'DIV', 'accordion-button', 'How does tracking work?'),
    ('btn-view-details', 'A', 'btn btn-sm btn-outline-primary', 'View Details'),
    ('input-search', 'INPUT', 'form-control', 'Search')
]

def seed_database(num_visitors=35, min_sessions_per_user=1, max_sessions_per_user=4):
    """Generates realistic synthetic user interaction data for testing and demonstration."""
    init_db()
    print(f"Seeding database with {num_visitors} visitors...")

    total_sessions_created = 0
    total_views_created = 0
    total_clicks_created = 0

    base_time = datetime.now() - timedelta(days=3)

    for i in range(num_visitors):
        visitor_id = f"usr_{uuid.uuid4().hex[:12]}"
        device, browser, os_name, screen_res = random.choice(DEVICES)
        register_user(visitor_id, device, browser, os_name, screen_res)

        num_sessions = random.randint(min_sessions_per_user, max_sessions_per_user)
        for s in range(num_sessions):
            session_id = f"sess_{uuid.uuid4().hex[:14]}"
            total_sessions_created += 1

            # Decide user behavior profile
            # 25% Bouncers (visit 1 page, 0-1 clicks, leave quickly)
            # 50% Regular Browsers (2-4 pages, 2-8 clicks)
            # 25% Power Users (4-7 pages, 8-15 clicks, high dwell)
            profile = random.choices(['bouncer', 'regular', 'power'], weights=[0.25, 0.50, 0.25])[0]

            if profile == 'bouncer':
                pages_to_visit = [PAGES[0]]
                total_duration = random.randint(5, 30)
                click_limit = random.randint(0, 1)
            elif profile == 'regular':
                k = random.randint(2, 4)
                pages_to_visit = random.sample(PAGES, min(k, len(PAGES)))
                total_duration = random.randint(45, 240)
                click_limit = random.randint(2, 7)
            else:
                k = random.randint(3, len(PAGES))
                pages_to_visit = random.sample(PAGES, k)
                total_duration = random.randint(180, 600)
                click_limit = random.randint(8, 16)

            session_dwell_remaining = total_duration

            for p_idx, (page_url, page_title) in enumerate(pages_to_visit):
                page_dwell = max(5, int(session_dwell_remaining / (len(pages_to_visit) - p_idx)))
                scroll = random.randint(20, 100) if profile != 'bouncer' else random.randint(10, 40)
                referrer = 'Direct' if p_idx == 0 else pages_to_visit[p_idx - 1][0]

                record_page_view(
                    session_id=session_id,
                    visitor_id=visitor_id,
                    page_url=page_url,
                    page_title=page_title,
                    referrer=referrer,
                    dwell_time=page_dwell,
                    scroll_depth=scroll
                )
                total_views_created += 1

            # Record clicks for this session
            for _ in range(click_limit):
                elem_id, tag, cls, text = random.choice(INTERACTIONS)
                page = random.choice(pages_to_visit)[0]
                record_click_event(
                    session_id=session_id,
                    visitor_id=visitor_id,
                    page_url=page,
                    element_id=elem_id,
                    element_tag=tag,
                    element_class=cls,
                    element_text=text,
                    x_pos=random.randint(100, 1200),
                    y_pos=random.randint(50, 1800)
                )
                total_clicks_created += 1

            # Record per-product behavioral tracking events
            num_prods_interacted = random.randint(1, 4) if profile != 'bouncer' else random.randint(0, 1)
            interacted_products = random.sample(PRODUCTS_CATALOG, min(num_prods_interacted, len(PRODUCTS_CATALOG)))

            for prod in interacted_products:
                # 1. Product view (impression)
                dwell = random.randint(10, 90) if profile != 'bouncer' else random.randint(3, 12)
                record_product_event(
                    session_id=session_id,
                    visitor_id=visitor_id,
                    product_id=prod['id'],
                    product_name=prod['name'],
                    category=prod['category'],
                    price=prod['price'],
                    event_type='view',
                    dwell_time=dwell
                )

                # 2. Detail click
                if profile in ['regular', 'power'] and random.random() > 0.35:
                    record_product_event(
                        session_id=session_id,
                        visitor_id=visitor_id,
                        product_id=prod['id'],
                        product_name=prod['name'],
                        category=prod['category'],
                        price=prod['price'],
                        event_type='click_details',
                        dwell_time=0
                    )

                # 3. Add to cart
                if profile in ['regular', 'power'] and random.random() > 0.55:
                    record_product_event(
                        session_id=session_id,
                        visitor_id=visitor_id,
                        product_id=prod['id'],
                        product_name=prod['name'],
                        category=prod['category'],
                        price=prod['price'],
                        event_type='add_to_cart',
                        dwell_time=0
                    )

                    # 4. Conversion / Purchase
                    if profile == 'power' and random.random() > 0.40:
                        record_product_event(
                            session_id=session_id,
                            visitor_id=visitor_id,
                            product_id=prod['id'],
                            product_name=prod['name'],
                            category=prod['category'],
                            price=prod['price'],
                            event_type='buy_now',
                            dwell_time=0
                        )

            update_session_heartbeat(session_id, total_duration)

    print(f"Seeding completed successfully!")
    print(f"Created: {num_visitors} Users, {total_sessions_created} Sessions, {total_views_created} PageViews, {total_clicks_created} Clicks.")

if __name__ == '__main__':
    seed_database()
