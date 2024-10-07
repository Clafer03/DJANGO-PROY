import json
import urllib.request
from urllib.error import URLError, HTTPError, ContentTooShortError
from bs4 import BeautifulSoup

# Function to download the webpage content
def download(url, user_agent='wswp', num_retries=2, charset='utf-8'):
    print('Descargando: ', url)
    request = urllib.request.Request(url)
    request.add_header('User-agent', user_agent)
    try:
        resp = urllib.request.urlopen(request)
        cs = resp.headers.get_content_charset()
        if not cs:
            cs = charset
        html = resp.read().decode(cs)
    except (URLError, HTTPError, ContentTooShortError) as e:
        print('Error al descargar: ', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry for 5xx HTTP errors
                return download(url, num_retries - 1)
    return html

# Function to extract the data and return the list of items
def extract_data(url):
    data_list = []  # Initialize empty list to store product data
    html = download(url)
    soup = BeautifulSoup(html, features='html.parser')

    # Locate the script tag containing the preloaded state
    script_tag = soup.find('script', string=lambda t: t and '__PRELOADED_STATE__' in t)

    if script_tag:
        script_content = script_tag.string

        # Extract JSON data from the script
        start = script_content.find('window.__PRELOADED_STATE__ =') + len('window.__PRELOADED_STATE__ = ')
        end = script_content.find('};', start) + 1
        json_data = script_content[start:end]

        # Parse JSON content
        data = json.loads(json_data)
        items = data.get('data', {}).get('items', [])

        for item in items:
            components_dict = {comp['type']: comp for comp in item['components']}

            title = components_dict.get('title', {}).get('title', {}).get('text', 'Sin título')
            price = components_dict.get('price', {}).get('price', {}).get('current_price', {}).get('value', 0)
            prev_price = components_dict.get('price', {}).get('price', {}).get('previous_price', {}).get('value', 0)
            discount = components_dict.get('price', {}).get('price', {}).get('discount', {}).get('value', 0)
            pictures = item.get('pictures', {}).get('pictures', [])
            img = pictures[0].get('id', 'Sin id') if isinstance(pictures, list) and len(pictures) > 0 else 'Sin imagen'
            url_ = item['metadata']['url']

            # Append the extracted data into data_list
            data_list.append({
                'title': title,
                'price': price,
                'prev_price': prev_price,
                'discount': discount,
                'img': f'https://http2.mlstatic.com/D_Q_NP_{img}-O.webp',
                'site_url': url_
            })
    else:
        print("No se encontró el script con __PRELOADED_STATE__.")

    return data_list  # Return the list of extracted data

# Function to execute and get data from multiple pages
def execute():
    all_data = []  # List to collect data from all pages
    for i in range(1, 21):
        url = f'https://www.mercadolibre.com.pe/ofertas?page={i}'
        data = extract_data(url)
        all_data.extend(data)  # Append each page's data to all_data

    return all_data  # Return the full list of items
