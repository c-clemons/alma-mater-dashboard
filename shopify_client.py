"""
Shopify API Client for Alma Mater Footwear
Fetches orders, products, and inventory data.
Caches results in session_state to avoid repeated API calls.
"""

import os
import ssl
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# SSL context for macOS Python (certifi fallback)
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE

# Load credentials from .env
_ENV_PATH = Path(__file__).parent / '.env'
_STORE = None
_TOKEN = None


def _load_env():
    global _STORE, _TOKEN
    if _STORE and _TOKEN:
        return
    # Try .env file
    if _ENV_PATH.exists():
        for line in _ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            if key.strip() == 'SHOPIFY_STORE':
                _STORE = val.strip()
            elif key.strip() == 'SHOPIFY_ACCESS_TOKEN':
                _TOKEN = val.strip()
    # Fallback to environment variables
    if not _STORE:
        _STORE = os.environ.get('SHOPIFY_STORE')
    if not _TOKEN:
        _TOKEN = os.environ.get('SHOPIFY_ACCESS_TOKEN')


def _api_get(endpoint: str, params: dict = None) -> dict:
    """Make authenticated GET request to Shopify Admin API."""
    _load_env()
    if not _STORE or not _TOKEN:
        raise RuntimeError("Shopify credentials not configured. Add .env file.")

    url = f"https://{_STORE}/admin/api/2024-01/{endpoint}"
    if params:
        qs = '&'.join(f'{k}={v}' for k, v in params.items())
        url = f"{url}?{qs}"

    req = urllib.request.Request(url)
    req.add_header('X-Shopify-Access-Token', _TOKEN)
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req, timeout=30, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ''
        raise RuntimeError(f"Shopify API error {e.code}: {body[:200]}")


def _fetch_all_orders(min_date: str, max_date: str) -> List[dict]:
    """Fetch all orders in a date range, handling pagination."""
    all_orders = []
    page_info = None
    _load_env()

    while True:
        if page_info:
            url = f"https://{_STORE}/admin/api/2024-01/orders.json?limit=250&page_info={page_info}"
        else:
            url = (f"https://{_STORE}/admin/api/2024-01/orders.json?"
                   f"status=any&created_at_min={min_date}&created_at_max={max_date}"
                   f"&limit=250&fields=id,name,created_at,financial_status,fulfillment_status,"
                   f"total_price,subtotal_price,total_tax,total_discounts,source_name,tags,"
                   f"discount_codes,line_items")

        req = urllib.request.Request(url)
        req.add_header('X-Shopify-Access-Token', _TOKEN)

        with urllib.request.urlopen(req, timeout=30, context=_SSL_CTX) as resp:
            data = json.loads(resp.read().decode())
            orders = data.get('orders', [])
            all_orders.extend(orders)

            # Check for next page
            link_header = resp.headers.get('Link', '')
            if 'rel="next"' in link_header:
                for part in link_header.split(','):
                    if 'rel="next"' in part:
                        page_info = part.split('page_info=')[1].split('>')[0]
                        break
            else:
                break

    return all_orders


def is_configured() -> bool:
    """Check if Shopify credentials are available."""
    _load_env()
    return bool(_STORE and _TOKEN)


def fetch_orders_for_month(year: int, month: int) -> List[dict]:
    """Fetch all orders for a specific month."""
    if month == 12:
        max_date = f"{year + 1}-01-01T00:00:00-08:00"
    else:
        max_date = f"{year}-{month + 1:02d}-01T00:00:00-08:00"
    min_date = f"{year}-{month:02d}-01T00:00:00-08:00"
    return _fetch_all_orders(min_date, max_date)


def fetch_orders_ytd(year: int = 2026) -> List[dict]:
    """Fetch all orders for the year to date."""
    min_date = f"{year}-01-01T00:00:00-08:00"
    max_date = datetime.now().strftime('%Y-%m-%dT23:59:59-08:00')
    return _fetch_all_orders(min_date, max_date)


def fetch_products() -> List[dict]:
    """Fetch all products with inventory."""
    all_products = []
    since_id = 0

    while True:
        data = _api_get('products.json', {
            'limit': 250,
            'since_id': since_id,
            'fields': 'id,title,product_type,status,variants,tags',
        })
        products = data.get('products', [])
        if not products:
            break
        all_products.extend(products)
        since_id = products[-1]['id']
        if len(products) < 250:
            break

    return all_products


def classify_order(order: dict) -> str:
    """Classify an order as 'DTC', 'Wholesale', or 'Gifting'."""
    tags = (order.get('tags') or '').lower()
    subtotal = float(order.get('subtotal_price', 0))
    discount = float(order.get('total_discounts', 0))
    codes = [c.get('code', '').lower() for c in (order.get('discount_codes') or [])]

    # Gifting: $0 subtotal or GIFTING tag
    if subtotal == 0 and discount > 0:
        return 'Gifting'
    if any('gifting' in t for t in tags.split(',')):
        return 'Gifting'
    if any('gifting' in c for c in codes):
        return 'Gifting'

    # Wholesale
    if 'wholesale' in tags:
        return 'Wholesale'
    if any('wholesale' in c for c in codes):
        return 'Wholesale'

    return 'DTC'


def analyze_orders(orders: List[dict]) -> dict:
    """
    Comprehensive order analysis.
    Returns dict with summary metrics, monthly breakdown, product data, discount analysis.
    """
    MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    monthly = defaultdict(lambda: {
        'orders': 0, 'gross': 0, 'discounts': 0, 'net': 0, 'tax': 0,
        'units': 0, 'dtc_orders': 0, 'dtc_net': 0, 'dtc_units': 0,
        'ws_orders': 0, 'ws_net': 0, 'ws_units': 0,
        'gift_orders': 0, 'gift_units': 0,
    })
    products = defaultdict(lambda: {'units': 0, 'gross_revenue': 0, 'net_revenue': 0})
    discount_codes = defaultdict(lambda: {'count': 0, 'total': 0})
    daily = defaultdict(lambda: {'orders': 0, 'net': 0})
    channel_type = defaultdict(lambda: {'orders': 0, 'net': 0, 'units': 0})

    for o in orders:
        created = o.get('created_at', '')
        if not created:
            continue
        month_num = int(created[5:7])
        date_str = created[:10]
        subtotal = float(o.get('subtotal_price', 0))
        discount = float(o.get('total_discounts', 0))
        tax = float(o.get('total_tax', 0))
        gross = subtotal + discount

        order_type = classify_order(o)
        total_units = sum(li.get('quantity', 0) for li in o.get('line_items', []))

        m = monthly[month_num]
        m['orders'] += 1
        m['gross'] += gross
        m['discounts'] += discount
        m['net'] += subtotal
        m['tax'] += tax
        m['units'] += total_units

        if order_type == 'DTC':
            m['dtc_orders'] += 1
            m['dtc_net'] += subtotal
            m['dtc_units'] += total_units
        elif order_type == 'Wholesale':
            m['ws_orders'] += 1
            m['ws_net'] += subtotal
            m['ws_units'] += total_units
        else:
            m['gift_orders'] += 1
            m['gift_units'] += total_units

        channel_type[order_type]['orders'] += 1
        channel_type[order_type]['net'] += subtotal
        channel_type[order_type]['units'] += total_units

        daily[date_str]['orders'] += 1
        daily[date_str]['net'] += subtotal

        # Product breakdown
        for li in o.get('line_items', []):
            title = li.get('title', 'Unknown')
            qty = li.get('quantity', 0)
            line_price = float(li.get('price', 0)) * qty
            line_disc = float(li.get('total_discount', 0))
            products[title]['units'] += qty
            products[title]['gross_revenue'] += line_price
            products[title]['net_revenue'] += line_price - line_disc

        # Discount codes
        for c in (o.get('discount_codes') or []):
            code = c.get('code', '(automatic)')
            discount_codes[code]['count'] += 1
            discount_codes[code]['total'] += float(c.get('amount', 0))
        if discount > 0 and not o.get('discount_codes'):
            discount_codes['(automatic/no code)']['count'] += 1
            discount_codes['(automatic/no code)']['total'] += discount

    # Build monthly list (1-12)
    monthly_list = []
    for m in range(1, 13):
        d = monthly[m]
        d['month'] = m
        d['month_name'] = MONTHS[m - 1]
        d['aov'] = d['net'] / d['orders'] if d['orders'] > 0 else 0
        d['discount_rate'] = (d['discounts'] / d['gross'] * 100) if d['gross'] > 0 else 0
        monthly_list.append(d)

    # Top products
    top_products = sorted(products.items(), key=lambda x: x[1]['units'], reverse=True)

    # Top discount codes
    top_discounts = sorted(discount_codes.items(), key=lambda x: x[1]['total'], reverse=True)

    # Totals
    total_orders = sum(m['orders'] for m in monthly_list)
    total_gross = sum(m['gross'] for m in monthly_list)
    total_discounts = sum(m['discounts'] for m in monthly_list)
    total_net = sum(m['net'] for m in monthly_list)
    total_units = sum(m['units'] for m in monthly_list)

    return {
        'total_orders': total_orders,
        'total_gross': total_gross,
        'total_discounts': total_discounts,
        'total_net': total_net,
        'total_units': total_units,
        'discount_rate': (total_discounts / total_gross * 100) if total_gross > 0 else 0,
        'aov': total_net / total_orders if total_orders > 0 else 0,
        'monthly': monthly_list,
        'channel': dict(channel_type),
        'top_products': top_products[:30],
        'top_discounts': top_discounts[:20],
        'daily': dict(sorted(daily.items())),
    }


def classify_product(p: dict) -> str:
    """Classify a Shopify product as 'Beta', 'Alpha', or 'Other'.
    Used for inventory aggregation aligned with the Excel model's
    Beta/Alpha tracking."""
    title = (p.get('title') or '').lower()
    product_type = (p.get('product_type') or '').lower()
    tags = (p.get('tags') or '').lower()
    haystack = f'{title} {product_type} {tags}'

    if 'beta' in haystack or 'v2' in haystack:
        return 'Beta'
    if 'alpha' in haystack:
        return 'Alpha'
    return 'Other'


def fetch_inventory_snapshot() -> dict:
    """Pull CURRENT inventory levels from Shopify, organized by product category.

    Shopify's REST API only exposes point-in-time inventory; there is no
    historical month-end balance endpoint. To capture monthly snapshots,
    run this function on the 1st of each month (or end of month) and save
    the result to a file.

    Returns:
        {
            'as_of': ISO-8601 timestamp,
            'by_category': {'Beta': int, 'Alpha': int, 'Other': int, 'TOTAL': int},
            'by_product': [
                {'title', 'category', 'sku_count', 'qty', 'product_type', 'status'},
                ...
            ],
        }
    """
    from datetime import datetime
    products = fetch_products()

    by_category = {'Beta': 0, 'Alpha': 0, 'Other': 0}
    by_product = []

    for p in products:
        category = classify_product(p)
        variants = p.get('variants', [])
        qty = sum((v.get('inventory_quantity') or 0) for v in variants)
        by_category[category] += qty
        by_product.append({
            'title': p.get('title', 'Unknown'),
            'category': category,
            'sku_count': len(variants),
            'qty': qty,
            'product_type': p.get('product_type', ''),
            'status': p.get('status', ''),
        })

    by_category['TOTAL'] = sum(by_category[c] for c in ('Beta', 'Alpha', 'Other'))
    by_product.sort(key=lambda x: x['qty'], reverse=True)

    return {
        'as_of': datetime.now().isoformat(timespec='seconds'),
        'by_category': by_category,
        'by_product': by_product,
    }


def reconstruct_historical_inventory(
    orders: List[dict],
    products: List[dict],
    current_snapshot: dict = None,
    po_arrivals: dict = None,
) -> dict:
    """Reconstruct month-END inventory balances by walking BACKWARDS from
    today's snapshot using order history + PO arrival data.

    Math: Beg_Inv[month N] = End_Inv[today] + Sales[N+1..today] - POs[N+1..today]
                           = End_Inv[N] - Sales[month N+1..today] + POs[N+1..today]

    Conversely, Ending Inventory for month M:
        End_Inv[M] = End_Inv[today] + Sales[M+1..today] - POs[M+1..today]

    Args:
        orders: list of orders fetched from Shopify (with line_items)
        products: list of products fetched from Shopify (for SKU → Beta/Alpha map)
        current_snapshot: result of fetch_inventory_snapshot() (or None to fetch fresh)
        po_arrivals: optional dict {(year, month): {'Beta': int, 'Alpha': int}}
                    of PO arrivals to subtract back. Without this, end-of-month
                    figures will be UNDERSTATED (PO arrivals not reversed).

    Returns:
        {(year, month): {'Beta': int, 'Alpha': int, 'Other': int}, ...}
        for every month present in the order data (running backwards from today).
    """
    from datetime import datetime
    from collections import defaultdict

    if current_snapshot is None:
        current_snapshot = fetch_inventory_snapshot()

    # SKU → product category map (built from product list)
    sku_to_cat = {}
    title_to_cat = {}
    for p in products:
        cat = classify_product(p)
        title_to_cat[(p.get('title') or '').lower()] = cat
        for v in p.get('variants', []):
            sku = (v.get('sku') or '').lower()
            if sku:
                sku_to_cat[sku] = cat

    def classify_line_item(li):
        """Best-effort classification of a line item to Beta/Alpha/Other."""
        sku = (li.get('sku') or '').lower()
        if sku and sku in sku_to_cat:
            return sku_to_cat[sku]
        title = (li.get('title') or '').lower()
        if 'beta' in title or 'v2' in title:
            return 'Beta'
        if 'alpha' in title:
            return 'Alpha'
        return 'Other'

    # Aggregate units shipped (sales) per month per category
    sales_by_month = defaultdict(lambda: {'Beta': 0, 'Alpha': 0, 'Other': 0})
    for o in orders:
        created = o.get('created_at', '')
        if not created:
            continue
        year = int(created[:4])
        month = int(created[5:7])
        for li in o.get('line_items', []):
            qty = li.get('quantity', 0) or 0
            cat = classify_line_item(li)
            sales_by_month[(year, month)][cat] += qty

    # Sort months ascending so we can iterate
    months = sorted(sales_by_month.keys())
    if not months:
        return {}

    # Walk BACKWARDS: starting from current_snapshot, undo each month
    # End_Inv[today's month] is approximately current_snapshot (assuming small intra-month variance)
    # End_Inv[prev_month] = End_Inv[current] + Sales[current_month] - POs[current_month]
    today = datetime.now()
    current_y, current_m = today.year, today.month

    # Initialize: end-of-CURRENT-month = current snapshot
    result = {}
    running = dict(current_snapshot['by_category'])
    running.pop('TOTAL', None)

    # End of current month is approximately what we have now
    result[(current_y, current_m)] = dict(running)

    # Walk back month-by-month
    months_desc = sorted([m for m in months if m <= (current_y, current_m)], reverse=True)
    for (y, m) in months_desc:
        if (y, m) == (current_y, current_m):
            continue  # already set
        # Get the month AFTER (y, m) — that's what consumed inventory to land here
        # Actually let's recompute: end_inv[y, m] = end_inv[y, m+1] + sales[y, m+1] - po_arrivals[y, m+1]
        # We walk backwards: starting from current, undo each subsequent month
        # i.e., for each month MORE RECENT than (y, m), add back sales and subtract POs
        pass

    # Simpler approach: build forward from earliest month using a known starting inventory
    # But we don't have a known starting inventory either. Use snapshot at month-end of CURRENT
    # and add sales (which left) and subtract POs (which arrived) to get prior month-ends.

    # Restart: walk explicitly
    # End_Inv[current_month] = current_snapshot
    # End_Inv[current_month - 1] = End_Inv[current_month] + sales_during_current_month - POs_during_current_month
    # Continue back...

    result = {}
    running = {c: current_snapshot['by_category'].get(c, 0) for c in ('Beta', 'Alpha', 'Other')}
    result[(current_y, current_m)] = dict(running)  # snapshot of "today"

    # Reverse-iterate from current month backward through every month with sales
    months_to_walk = sorted(
        [m for m in sales_by_month.keys() if m <= (current_y, current_m)],
        reverse=True
    )

    for ym in months_to_walk:
        y, m = ym
        # "Undo" the sales and PO arrivals of THIS month to get the PRIOR month-end
        sales_this_month = sales_by_month[ym]
        pos_this_month = (po_arrivals or {}).get(ym, {'Beta': 0, 'Alpha': 0, 'Other': 0})

        # Prior month-end = current running + sales_this_month - pos_this_month
        prior_running = {
            c: running[c] + sales_this_month.get(c, 0) - pos_this_month.get(c, 0)
            for c in ('Beta', 'Alpha', 'Other')
        }

        # Compute prior year/month
        if m == 1:
            prior_y, prior_m = y - 1, 12
        else:
            prior_y, prior_m = y, m - 1

        result[(prior_y, prior_m)] = dict(prior_running)
        running = prior_running

    return result


def analyze_inventory(products: List[dict]) -> dict:
    """Analyze product inventory."""
    items = []
    total_inv = 0
    in_stock = 0
    out_of_stock = 0
    negative = 0

    for p in products:
        title = p.get('title', 'Unknown')
        variants = p.get('variants', [])
        inv = sum(v.get('inventory_quantity', 0) for v in variants)
        total_inv += inv

        if inv > 0:
            in_stock += 1
        elif inv == 0:
            out_of_stock += 1
        else:
            negative += 1

        items.append({
            'title': title,
            'variants': len(variants),
            'inventory': inv,
            'product_type': p.get('product_type', ''),
            'status': p.get('status', ''),
        })

    items.sort(key=lambda x: x['inventory'], reverse=True)

    return {
        'total_units': total_inv,
        'total_products': len(products),
        'in_stock': in_stock,
        'out_of_stock': out_of_stock,
        'negative': negative,
        'items': items,
    }


def get_shopify_data(year: int = 2026, use_cache: bool = True) -> Optional[dict]:
    """
    Fetch and analyze all Shopify data for the year.
    Caches in session_state for the session.
    Returns None if Shopify is not configured.
    """
    if not is_configured():
        return None

    # Check cache
    try:
        import streamlit as st
        cache_key = f'shopify_data_{year}'
        if use_cache and cache_key in st.session_state:
            cached = st.session_state[cache_key]
            # Refresh if older than 15 minutes
            cached_at = cached.get('_fetched_at', '')
            if cached_at:
                age = (datetime.now() - datetime.fromisoformat(cached_at)).seconds
                if age < 900:  # 15 min
                    return cached
    except ImportError:
        pass

    # Fetch fresh data
    orders = fetch_orders_ytd(year)
    products = fetch_products()

    order_analysis = analyze_orders(orders)
    inventory = analyze_inventory(products)

    result = {
        'orders': order_analysis,
        'inventory': inventory,
        'year': year,
        '_fetched_at': datetime.now().isoformat(),
    }

    # Cache in session_state
    try:
        import streamlit as st
        st.session_state[f'shopify_data_{year}'] = result
    except ImportError:
        pass

    return result
