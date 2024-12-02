########################################################################################################################
# Crawl once a month to update global vehicle information.
# 01 Organise by brands
# 2024.08.28 PM 18:08
# Source constructors : Esketch Song (esketch@gmail.com)
########################################################################################################################

import requests
from bs4 import BeautifulSoup
import re
import csv

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

def extract_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    manufacturers = []

    # Extract update date
    update_date = soup.find('div', class_='breadcrumb2').find('div', class_='fr').text.strip()

    # Extract brand count
    brand_count = soup.find('div', id='newscol3', class_='col3width carbrnum').text.strip()
    brand_count = re.search(r'(\d+)', brand_count).group(1) if re.search(r'(\d+)', brand_count) else "Unknown"

    # Find all manufacturer blocks
    manufacturer_blocks = soup.find_all(['div', 'a'], class_=['col2width fl bcol-white carman', 'car-brand-logo'])
    
    for block in manufacturer_blocks:
        name_elem = block.find(['h5', 'img'])
        if not name_elem:
            continue
        
        if name_elem.name == 'img':
            name = name_elem['alt'].replace(' logo', '')
        else:
            name = name_elem.text.strip()
        
        logo_url = block.find('img')['src'] if block.find('img') else ''
        link = "https://www.autoevolution.com" + block.find('a')['href'] if block.find('a') else ''

        numbers_div = block.find_next_sibling('div', class_='col3width fl carnums')
        in_production = 0
        discontinued = 0
        
        if numbers_div:
            numbers = numbers_div.text
            in_production_match = re.search(r'(\d+)\s*in production', numbers)
            discontinued_match = re.search(r'(\d+)\s*discontinued', numbers)
            
            in_production = int(in_production_match.group(1)) if in_production_match else 0
            discontinued = int(discontinued_match.group(1)) if discontinued_match else 0

        manufacturers.append({
            'name': name,
            'logo_url': logo_url,
            'link': link,
            'in_production': in_production,
            'discontinued': discontinued
        })

    return update_date, brand_count, manufacturers

def save_to_csv(manufacturers, filename='manufacturers.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['name', 'logo_url', 'link', 'in_production', 'discontinued']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for manufacturer in manufacturers:
            writer.writerow(manufacturer)

def main():
    url = "https://www.autoevolution.com/cars/"
    html_content = get_html_content(url)
    
    if html_content:
        update_date, brand_count, manufacturers = extract_info(html_content)
        
        print(f"업데이트 날짜: {update_date}")
        print(f"브랜드 수: {brand_count}")
        print(f"추출된 제조사 수: {len(manufacturers)}")
        print("-" * 50)

        # Save manufacturers to CSV file
        save_to_csv(manufacturers)
        print(f"제조사 정보가 manufacturers.csv 파일로 저장되었습니다.")

        # Check for specific manufacturers
        specific_manufacturers = ['WIESMANN', 'Xpeng', 'ZENDER', 'Zenvo']
        for name in specific_manufacturers:
            if any(m['name'] == name for m in manufacturers):
                print(f"{name} 추출 성공")
            else:
                print(f"{name} 추출 실패")

    else:
        print("Failed to retrieve the webpage.")

if __name__ == "__main__":
    main()