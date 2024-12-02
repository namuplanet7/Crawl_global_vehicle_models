########################################################################################################################
# Information visualisation
# 06 Information visualisation
# 2024.08.28
# Source constructors : Esketch Song (esketch@gmail.com)
########################################################################################################################


# 데이터 로드

import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 데이터 로드
def load_all_data():
    all_data = []
    for filename in os.listdir('brand_specs'):
        if filename.endswith('_specs.json'):
            with open(f'brand_specs/{filename}', 'r', encoding='utf-8') as f:
                brand_data = json.load(f)
                all_data.extend(brand_data)
    return pd.DataFrame(all_data)

df = load_all_data()




plt.figure(figsize=(15, 8))
brand_counts = df['brand'].value_counts().head(20)
sns.barplot(x=brand_counts.index, y=brand_counts.values)
plt.title('Top 20 Brands by Number of Models')
plt.xlabel('Brand')
plt.ylabel('Number of Models')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()





# 연료 유형 분포

plt.figure(figsize=(10, 10))
fuel_type_counts = df['fuel_type'].value_counts()
plt.pie(fuel_type_counts.values, labels=fuel_type_counts.index, autopct='%1.1f%%')
plt.title('Distribution of Fuel Types')
plt.axis('equal')
plt.show()



import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import re

def load_all_data():
    all_data = []
    for filename in os.listdir('brand_specs'):
        if filename.endswith('_specs.json'):
            with open(f'brand_specs/{filename}', 'r', encoding='utf-8') as f:
                brand_data = json.load(f)
                all_data.extend(brand_data)
    return all_data

def clean_horsepower(hp_string):
    # 숫자만 추출
    match = re.search(r'\d+', hp_string)
    if match:
        return int(match.group())
    return None

def create_dataframe(data):
    df = pd.DataFrame(data)
    # 중첩된 'specs' 데이터를 평탄화
    df = pd.concat([df.drop(['specs'], axis=1), df['specs'].apply(pd.Series)], axis=1)
    
    # 마력 데이터 정제
    df['horsepower'] = df['horsepower'].apply(clean_horsepower)
    
    return df

def plot_brand_model_count(df):
    plt.figure(figsize=(12, 6))
    brand_counts = df['brand'].value_counts().head(20)
    sns.barplot(x=brand_counts.index, y=brand_counts.values)
    plt.title('Top 20 Brands by Number of Models')
    plt.xlabel('Brand')
    plt.ylabel('Number of Models')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('brand_model_count.png')
    plt.close()

def plot_fuel_type_distribution(df):
    plt.figure(figsize=(10, 6))
    fuel_counts = df['fuel_type'].value_counts()
    plt.pie(fuel_counts.values, labels=fuel_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Fuel Types')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('fuel_type_distribution.png')
    plt.close()

def plot_horsepower_distribution(df):
    plt.figure(figsize=(12, 6))
    sns.histplot(df['horsepower'].dropna(), kde=True)
    plt.title('Distribution of Horsepower')
    plt.xlabel('Horsepower')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('horsepower_distribution.png')
    plt.close()

def plot_horsepower_by_fuel_type(df):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='fuel_type', y='horsepower', data=df.dropna(subset=['horsepower', 'fuel_type']))
    plt.title('Horsepower Distribution by Fuel Type')
    plt.xlabel('Fuel Type')
    plt.ylabel('Horsepower')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('horsepower_by_fuel_type.png')
    plt.close()

def main():
    # 데이터 로드
    data = load_all_data()
    
    # DataFrame 생성
    df = create_dataframe(data)
    
    # 시각화
    plot_brand_model_count(df)
    plot_fuel_type_distribution(df)
    plot_horsepower_distribution(df)
    plot_horsepower_by_fuel_type(df)
    
    print("Data visualization completed. Check the generated PNG files.")

if __name__ == "__main__":
    main()





import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def load_all_data():
    all_data = []
    for filename in os.listdir('brand_specs'):
        if filename.endswith('_specs.json'):
            with open(f'brand_specs/{filename}', 'r', encoding='utf-8') as f:
                brand_data = json.load(f)
                all_data.extend(brand_data)
    return all_data

def clean_numeric(value):
    if isinstance(value, str):
        return float(''.join(filter(str.isdigit, value)))
    return value

def create_dataframe(data):
    df = pd.DataFrame(data)
    # 중첩된 'specs' 데이터를 평탄화
    if 'specs' in df.columns:
        df = pd.concat([df.drop(['specs'], axis=1), df['specs'].apply(pd.Series)], axis=1)
    
    # 데이터 구조 확인
    print("Columns in the dataframe:", df.columns)
    
    # 엔진 크기와 연비 데이터 추출 (실제 컬럼 이름에 맞게 수정)
    if 'engine' in df.columns:
        df['engine_size'] = df['engine'].apply(lambda x: x.get('displacement') if isinstance(x, dict) else x)
    elif 'displacement' in df.columns:
        df['engine_size'] = df['displacement']
    else:
        print("Warning: No engine size data found")
        df['engine_size'] = np.nan

    if 'fuel economy' in df.columns:
        df['fuel_efficiency'] = df['fuel economy'].apply(lambda x: x.get('combined', {}).get('mpg') if isinstance(x, dict) else x)
    elif 'combined' in df.columns:
        df['fuel_efficiency'] = df['combined']
    else:
        print("Warning: No fuel economy data found")
        df['fuel_efficiency'] = np.nan

    # 데이터 정제
    df['engine'] = df['engine'].apply(lambda x: x.get('displacement') if isinstance(x, dict) else x)
    df['engine'] = df['engine'].apply(clean_numeric)
    
    # fuel_economy 열이 딕셔너리인 경우 처리
    df['fuel_economy'] = df['fuel_economy'].apply(lambda x: x.get('combined', {}).get('mpg') if isinstance(x, dict) else x)
    df['fuel_economy'] = pd.to_numeric(df['fuel_economy'].apply(clean_numeric), errors='coerce')
    
    # fuel_type이 비어있거나 NaN인 경우 제거
    df = df[df['fuel_type'].notna() & (df['fuel_type'] != '')]    
    return df

def plot_engine_size_vs_fuel_economy(df):
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='engine_size', y='fuel_efficiency', hue='fuel_type', data=df)
    plt.title('Engine Size vs Fuel Economy')
    plt.xlabel('Engine Size (L)')
    plt.ylabel('Fuel Economy (MPG)')
    plt.tight_layout()
    plt.savefig('engine_size_vs_fuel_economy.png')
    plt.close()

def plot_fuel_economy_distribution_by_fuel_type(df):
    plt.figure(figsize=(12, 6))
    # NaN 값을 제거하고 fuel_type이 비어있지 않은 행만 선택
    valid_data = df.dropna(subset=['fuel_type', 'fuel_economy'])
    valid_data = valid_data[valid_data['fuel_type'] != '']
    
    if len(valid_data) > 0:
        sns.boxplot(x='fuel_type', y='fuel_economy', data=valid_data)
        plt.title('Fuel Economy Distribution by Fuel Type')
        plt.xlabel('Fuel Type')
        plt.ylabel('Fuel Economy (MPG)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('fuel_economy_by_fuel_type.png')
    else:
        print("No valid data for fuel economy distribution plot")
    plt.close()

def plot_engine_size_distribution(df):
    plt.figure(figsize=(12, 6))
    sns.histplot(df['engine_size'].dropna(), kde=True, bins=30)
    plt.title('Distribution of Engine Sizes')
    plt.xlabel('Engine Size (L)')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('engine_size_distribution.png')
    plt.close()

def plot_fuel_economy_trend(df):
    if 'year' in df.columns:
        df['year'] = pd.to_datetime(df['year'], format='%Y')
        yearly_avg = df.groupby('year')['fuel_efficiency'].mean().reset_index()
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(x='year', y='fuel_efficiency', data=yearly_avg)
        plt.title('Average Fuel Economy Trend Over Years')
        plt.xlabel('Year')
        plt.ylabel('Average Fuel Economy (MPG)')
        plt.tight_layout()
        plt.savefig('fuel_economy_trend.png')
        plt.close()
    else:
        print("Warning: No 'year' column found for fuel economy trend analysis")

def main():
    # 데이터 로드
    data = load_all_data()
    
    # DataFrame 생성
    df = create_dataframe(data)
    
    # 데이터 확인
    print(df.head())
    print(df.columns)
    
    # 시각화
    plot_engine_size_vs_fuel_economy(df)
    plot_fuel_economy_distribution_by_fuel_type(df)
    plot_engine_size_distribution(df)
    plot_fuel_economy_trend(df)
    
    print("Data visualization completed. Check the generated PNG files.")

if __name__ == "__main__":
    main()









