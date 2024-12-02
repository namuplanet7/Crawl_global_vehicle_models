########################################################################################################################
# Crawl once a month to update global vehicle information.
# 02 Crawl models for each brand
# 2024.08.28
# Source constructors : Esketch Song (esketch@gmail.com)
########################################################################################################################


import requests
from bs4 import BeautifulSoup
import re
import csv
import time

def get_html_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

def extract_manufacturers(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    manufacturers = []

    manufacturer_blocks = soup.find_all(['div', 'a'], class_=['col2width fl bcol-white carman', 'car-brand-logo'])
    
    for block in manufacturer_blocks:
        name_elem = block.find(['h5', 'img'])
        if not name_elem:
            continue
        
        if name_elem.name == 'img':
            name = name_elem['alt'].replace(' logo', '')
        else:
            name = name_elem.text.strip()
        
        link = block.find('a')['href'] if block.find('a') else ''
        
        manufacturers.append({
            'name': name,
            'link': link
        })

    return manufacturers

def extract_brand_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    brand_name = soup.find('h1', class_='newstitle').text.strip()
    brand_name = re.sub(r'Models & Brand History', '', brand_name).strip()
    
    info_div = soup.find('div', class_='brandinfo')
    production_models = info_div.find('b', class_='col-green2').text if info_div else '0'
    discontinued_models = info_div.find('b', class_='col-red').text if info_div else '0'
    
    return brand_name, int(production_models), int(discontinued_models)

def extract_models(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    models = []
    
    for model_div in soup.find_all('div', class_='carmod'):
        model_name = model_div.find('h4').text.strip()
        body_type = model_div.find('p', class_='body').text.strip() if model_div.find('p', class_='body') else ''
        fuel_types = [span.text.strip() for span in model_div.find('p', class_='eng').find_all('span')] if model_div.find('p', class_='eng') else []
        generations = model_div.find('b').text.strip() if model_div.find('b') else ''
        years = model_div.find('span').text.strip() if model_div.find('span') else ''
        
        # Extract production years
        production_years = re.search(r'\((\d{4})\s*-\s*(Present|\d{4})\)', years)
        if production_years:
            start_year = production_years.group(1)
            end_year = production_years.group(2)
            production_years = f"{start_year} - {end_year}"
        else:
            production_years = "N/A"
        
        # Determine if the model is in production or discontinued
        status = "PRODUCTION" if "Present" in years else "DISCONTINUED"
        
        img = model_div.find('img')
        image_url = img['src'] if img else ''
        
        link = model_div.find('a')['href'] if model_div.find('a') else ''
        
        models.append({
            'model_name': model_name,
            'body_type': body_type,
            'fuel_types': ', '.join(fuel_types),
            'generations': generations,
            'production_years': production_years,
            'status': status,
            'image_url': image_url,
            'model_link': link
        })
    
    return models

def save_to_csv(data, filename='all_brand_models.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['brand', 'production_models', 'discontinued_models', 'model_name', 'body_type', 'fuel_types', 'generations', 'production_years', 'status', 'image_url', 'model_link']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for brand in data:
            for model in brand['models']:
                writer.writerow({
                    'brand': brand['name'],
                    'production_models': brand['production_models'],
                    'discontinued_models': brand['discontinued_models'],
                    **model
                })

def main():
    base_url = "https://www.autoevolution.com/cars/"
    html_content = get_html_content(base_url)
    
    if html_content:
        manufacturers = extract_manufacturers(html_content)
        all_data = []
        
        for manufacturer in manufacturers:
            url = manufacturer['link']
            if not url.startswith('http'):
                url = f"https://www.autoevolution.com{url}"
            
            html_content = get_html_content(url)
            
            if html_content:
                brand_name, production_models, discontinued_models = extract_brand_info(html_content)
                models = extract_models(html_content)
                
                brand_data = {
                    'name': brand_name,
                    'production_models': production_models,
                    'discontinued_models': discontinued_models,
                    'models': models
                }
                all_data.append(brand_data)
                
                print(f"Processed {brand_name}:")
                print(f"Production models: {production_models}")
                print(f"Discontinued models: {discontinued_models}")
                print(f"Total models extracted: {len(models)}")
                print("-" * 50)
            
            time.sleep(2)  # 웹사이트에 과도한 요청을 보내지 않기 위한 지연
        
        save_to_csv(all_data)
        print("Data has been saved to all_brand_models.csv")
    else:
        print("Failed to retrieve the main webpage.")

if __name__ == "__main__":
    main()