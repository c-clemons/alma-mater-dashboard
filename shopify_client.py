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
