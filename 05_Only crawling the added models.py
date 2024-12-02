########################################################################################################################
# Only crawling the added models
# 05 Extract specification cleanup for each model
# 2024.08.28
# Source constructors : Esketch Song (esketch@gmail.com)
########################################################################################################################


import csv
import json
import os
import requests
from bs4 import BeautifulSoup
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_existing_data():
    existing_data = {}
    for filename in os.listdir('brand_specs'):
        if filename.endswith('_specs.json'):
            brand = filename.replace('_specs.json', '')
            with open(f'brand_specs/{filename}', 'r', encoding='utf-8') as f:
                existing_data[brand] = json.load(f)
    logging.info(f"Loaded data for {len(existing_data)} brands from existing files.")
    return existing_data

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def read_csv_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        models = list(reader)
    
    if not models:
        raise ValueError("CSV file is empty or could not be read properly.")
    
    # 데이터 구조 확인
    required_keys = ['brand', 'model_name', 'fuel_type', 'engine_name', 'horsepower', 'image_url', 'sub_link']
    for key in required_keys:
        if key not in models[0]:
            raise KeyError(f"Required key '{key}' not found in CSV data.")
    
    return models

def extract_specs(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.autoevolution.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all engine blocks
    engine_blocks = soup.find_all('div', class_='engine-block')
    
    if not engine_blocks:
        # If no engine blocks found, try to extract general information
        return extract_general_info(soup)

    all_specs = []

    for engine_block in engine_blocks:
        specs = {}

        # Extract engine name
        engine_name = engine_block.find('h3')
        if engine_name:
            specs['engine_name'] = engine_name.text.strip()

        # Extract all spec tables
        tables = engine_block.find_all('table', class_='techdata')
        
        for table in tables:
            table_title = table.find('th', class_='title')
            if table_title:
                section_name = table_title.text.strip().lower().replace(' specs', '')
                specs[section_name] = {}
                
                for row in table.find_all('tr'):
                    header = row.find('td', class_='left')
                    value = row.find('td', class_='right')
                    if header and value:
                        key = header.text.strip().replace(':', '').lower()
                        specs[section_name][key] = value.text.strip()

        all_specs.append(specs)

    return all_specs

def extract_general_info(soup):
    general_info = {}
    
    # Try to extract information from the general description
    description = soup.find('div', class_='newstext')
    if description:
        general_info['description'] = description.text.strip()

    # Try to extract any visible specifications
    spec_boxes = soup.find_all('div', class_='sbox10')
    for box in spec_boxes:
        title = box.find('div', class_='tt')
        if title:
            section_name = title.text.strip().lower()
            general_info[section_name] = {}
            items = box.find_all('li')
            for item in items:
                general_info[section_name][item['id']] = item.text.strip()

def load_existing_data():
    existing_data = {}
    for filename in os.listdir('brand_specs'):
        if filename.endswith('_specs.json'):
            brand = filename.replace('_specs.json', '')
            with open(f'brand_specs/{filename}', 'r', encoding='utf-8') as f:
                existing_data[brand] = json.load(f)
    return existing_data

def identify_new_models(existing_data, new_models):
    new_models_to_crawl = []
    brands_checked = set()
    for model in new_models:
        brand = model['brand']
        model_name = model['model_name']
        engine_name = model['engine_name']
        
        if brand not in brands_checked:
            logging.info(f"Checking for new models in brand: {brand}")
            brands_checked.add(brand)
        
        if brand not in existing_data:
            new_models_to_crawl.append(model)
            logging.info(f"New brand found: {brand}, adding model {model_name} with engine {engine_name}")
        elif not any(m['model_name'] == model_name and m['engine_name'] == engine_name 
                     for m in existing_data[brand]):
            new_models_to_crawl.append(model)
            logging.info(f"New model found for {brand}: {model_name} with engine {engine_name}")
    
    logging.info(f"Identified {len(new_models_to_crawl)} new models across {len(brands_checked)} brands.")
    return new_models_to_crawl

def crawl_new_models(new_models, session):
    results = {}
    for model in new_models:
        brand = model['brand']
        if brand not in results:
            results[brand] = []
        
        full_url = f"https://www.autoevolution.com{model['sub_link']}"
        logging.info(f"Crawling: {brand} {model['model_name']} {model['engine_name']}")
        specs = extract_specs(full_url, session)
        
        if specs:
            model['specs'] = specs
            logging.info(f"Successfully extracted specs for {brand} {model['model_name']} {model['engine_name']}")
        else:
            logging.warning(f"Failed to extract specs for {brand} {model['model_name']} {model['engine_name']}")
        
        results[brand].append(model)
        
        time.sleep(random.uniform(3, 7))
    
    return results

def update_existing_data(existing_data, new_data):
    for brand, models in new_data.items():
        if brand not in existing_data:
            existing_data[brand] = models
            logging.info(f"Added new brand: {brand} with {len(models)} models")
        else:
            added_models = 0
            for new_model in models:
                existing_models = existing_data[brand]
                if not any(m['model_name'] == new_model['model_name'] and 
                           m['engine_name'] == new_model['engine_name'] for m in existing_models):
                    existing_models.append(new_model)
                    added_models += 1
            logging.info(f"Updated {brand}: added {added_models} new models")
    return existing_data

def save_updated_data(updated_data):
    for brand, models in updated_data.items():
        with open(f'brand_specs/{brand}_specs.json', 'w', encoding='utf-8') as f:
            json.dump(models, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved updated data for {brand}: {len(models)} models")

def main():
    logging.info("Starting the crawling process")

    # 기존 데이터 로드
    existing_data = load_existing_data()

    # 새 CSV 파일 읽기
    with open('detailed_model_info.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        new_models = list(reader)
    logging.info(f"Loaded {len(new_models)} models from the new CSV file")

    # 새로운 모델 식별
    new_models_to_crawl = identify_new_models(existing_data, new_models)

    if not new_models_to_crawl:
        logging.info("No new models to crawl.")
        return

    logging.info(f"Found {len(new_models_to_crawl)} new models to crawl.")

    # 새 모델 크롤링
    session = requests_retry_session()
    new_data = crawl_new_models(new_models_to_crawl, session)

    # 기존 데이터 업데이트
    updated_data = update_existing_data(existing_data, new_data)

    # 업데이트된 데이터 저장
    save_updated_data(updated_data)

    logging.info("Crawling and updating process completed.")

if __name__ == "__main__":
    main()