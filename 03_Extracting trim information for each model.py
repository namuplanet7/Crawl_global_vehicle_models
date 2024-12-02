########################################################################################################################
# Crawl once a month to update global vehicle information.
# 03 Extracting trim information for each model
# 2024.08.28
# Source constructors : Esketch Song (esketch@gmail.com)
########################################################################################################################

import csv
import requests
from bs4 import BeautifulSoup
import time
import re

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

import logging

logging.basicConfig(filename='scraping_log.txt', level=logging.INFO)

def extract_model_info(html_content, brand):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    model_name_full = soup.find('h1', class_='padsides_20i mgtop_10 nomgbot newstitle innews').text.strip()
    # Remove brand name and extra text
    model_name = re.sub(r'^' + re.escape(brand) + r'\s+', '', model_name_full)
    model_name = re.sub(r'\s+Models/Series Timeline, Specifications & Photos$', '', model_name)
    
    image_container = soup.find('a', class_='mpic fr mgtop_20')
    if image_container and image_container.find('img'):
        image_url = image_container.find('img')['src']
    else:
        image_url = "N/A"
    
    engines = []
    engine_sections = soup.find_all('div', class_='mot clearfix')
    for section in engine_sections:
        fuel_type = section.find('strong').text.strip().replace(':', '').upper()
        fuel_type = re.sub(r'\s+ENGINES$', '', fuel_type)  # Remove 'ENGINES' from fuel type
        for engine in section.find_all('a', class_='engurl semibold'):
            engine_info = engine.text.strip()
            engine_info = re.sub(r'\s*/\s*', ' ', engine_info)  # Remove slashes
            
            # Remove brand and model name from engine info
            engine_info = re.sub(r'^' + re.escape(brand) + r'\s+' + re.escape(model_name) + r'\s+', '', engine_info)
            
            # More flexible pattern matching
            engine_match = re.search(r'(.*?)\s*\((\d+)\s*HP\)$', engine_info)
            if engine_match:
                engine_name = engine_match.group(1).strip()
                hp = engine_match.group(2) + " HP"
            else:
                # If the pattern doesn't match, use the whole string as engine name
                engine_name = engine_info
                hp = "N/A"
                logging.info(f"Unmatched engine info: {engine_info}")
            
            sub_link = engine['href']
            if sub_link.startswith('https://www.autoevolution.com'):
                sub_link = sub_link[len('https://www.autoevolution.com'):]
            
            engines.append({
                'fuel_type': fuel_type,
                'engine_name': engine_name,
                'horsepower': hp,
                'sub_link': sub_link
            })
    
    return {
        'model_name': model_name,
        'image_url': image_url,
        'engines': engines
    }
    
def process_models(input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = ['brand', 'model_name', 'fuel_type', 'engine_name', 'horsepower', 'image_url', 'sub_link']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            print(f"Processing: {row['brand']} {row['model_name']}")
            html_content = get_html_content(row['model_link'])
            if html_content:
                model_info = extract_model_info(html_content, row['brand'])
                for engine in model_info['engines']:
                    writer.writerow({
                        'brand': row['brand'],
                        'model_name': model_info['model_name'],
                        'fuel_type': engine['fuel_type'],
                        'engine_name': engine['engine_name'],
                        'horsepower': engine['horsepower'],
                        'image_url': model_info['image_url'],
                        'sub_link': engine['sub_link']
                    })
            time.sleep(1) 

def main():
    input_file = 'all_brand_models.csv'
    output_file = 'detailed_model_info.csv'
    process_models(input_file, output_file)
    print(f"Detailed information has been saved to {output_file}")

if __name__ == "__main__":
    main()