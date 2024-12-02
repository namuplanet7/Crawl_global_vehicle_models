########################################################################################################################
# Crawl once a month to update global vehicle information.
# 04 Extract specification cleanup for each model
# 2024.08.28
# Source constructors : Esketch Song (esketch@gmail.com)
########################################################################################################################

import csv
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

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

def process_brand(brand_models, session):
    results = []
    for model in brand_models:
        full_url = f"https://www.autoevolution.com{model['sub_link']}"
        specs = extract_specs(full_url, session)
        
        if specs:
            model['specs'] = specs
            print(f"Successfully extracted specs for {model['brand']} {model['model_name']}")
        else:
            print(f"Failed to extract specs for {model['brand']} {model['model_name']}")
        
        results.append(model)
        
        # Add a random delay between requests to avoid overloading the server
        time.sleep(random.uniform(3, 7))
    
    return results

    return [general_info] if general_info else None

# 메인 코드
try:
    # CSV 파일 읽기
    models = read_csv_file('detailed_model_info.csv')

    # 브랜드별로 모델 그룹화
    brands = {}
    for model in models:
        brand = model['brand']
        if brand not in brands:
            brands[brand] = []
        brands[brand].append(model)

    # 세션 생성
    session = requests_retry_session()

    # 브랜드별 JSON 파일을 저장할 디렉토리 생성
    os.makedirs('brand_specs', exist_ok=True)

    # 각 브랜드 처리
    for brand, brand_models in brands.items():
        print(f"Processing brand: {brand}")
        brand_results = process_brand(brand_models, session)
        
        # 이 브랜드의 결과 저장
        with open(f'brand_specs/{brand}_specs.json', 'w', encoding='utf-8') as f:
            json.dump(brand_results, f, indent=2, ensure_ascii=False)
        
        print(f"Completed processing for {brand}. Results saved to brand_specs/{brand}_specs.json")
        print("-" * 50)

    print("All brands processed.")

except Exception as e:
    print(f"An error occurred: {e}")
    # 여기에 추가적인 오류 처리 로직을 넣을 수 있습니다.

print("All brands processed.")