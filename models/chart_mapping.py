import pandas as pd
import re
from models.dataset_transformer import DatasetTransformer

def calculate_nps_components(group, root_data, chart):
    
    nps_score = chart.get('xAxis', {}).get('label')

    total = len(group)

    promoters = ((group[nps_score] == 9) | (group[nps_score] == 10)).sum()
    detractors = ((group[nps_score] >= 0) & (group[nps_score] <= 6)).sum()
    passives = ((group[nps_score] >= 7) & (group[nps_score] <= 8)).sum()

    return pd.Series({
        "Promoter" : round(promoters / total * 100, 2),
        "Passive" : round(passives / total * 100, 2),
        "Detractor" : round(detractors / total * 100, 2),
        "NPS" : round((promoters - detractors) / total * 100, 2)
    })

def calculate_csat_components(group, root_data, chart):
    csat = {
        'CSAT_5' : 0,
        'CSAT_4' : 0,
        'CSAT_3' : 0,
        'CSAT_2' : 0,
        'CSAT_1' : 0,
    }
    csat_score = chart.get('xAxis', {}).get('label')
    
    col = group[csat_score].astype(str).str.strip()
    col = col.str.replace(r'\s+', ' ', regex=True)  # gom nhiều khoảng trắng thành 1
    col = col.str.lower()  # (tùy chọn) đồng bộ viết thường

    exclude_values = [
        'i do not use this bank product',
        'not use in recent 1 month',
        'not experience yet/ not remember'
    ]
    
    filtered = col[~col.isin(exclude_values)].dropna()
    filtered = filtered[filtered != 'nan']
    
    filtered = filtered.str.replace(r'\.0$', '', regex=True)
    filtered = pd.to_numeric(filtered, errors='coerce').dropna().astype(int)

    percentages = filtered.value_counts(normalize=True, dropna=True) * 100

    for key, value in percentages.items():
        if f"CSAT_{key}" in csat:
            csat[f"CSAT_{key}"] = round(value, 2)

    return pd.Series(csat)







# def calculate_csat_components(group, root_data, chart):
    
#     months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
#     wave = group['Wave'].unique().tolist()[0]
#     bank = group['Bank'].unique().tolist()[0]

#     cur_month = wave[:3]
#     cur_year = wave[-2:]

#     if cur_month == 'Jan':
#         cur_year -= 1
    
#     previous_group = pd.DataFrame()

#     if cur_month in months:
#         previous_wave = f'{months[months.index(cur_month) - 1]}\'{cur_year}'

#         previous_group = root_data[((root_data['Wave'] == previous_wave) & (root_data['Bank'] == bank))]

#     prev_total = len(previous_group)

#     categories = chart.get('yAxis', {}).get('categories', [])

#     records = []
    
#     for category in categories:
#         category_group = group[group[chart.get('yAxis', {}).get('label')] == category]
#         n = len(category_group) 
#         valid = category_group[category_group[chart.get('xAxis', {}).get('label')].isin(['5', 5])] #['Not use in recent 1 month', 'I do not use this bank product']
#         p = round(len(valid) / n * 100, 2) if n > 0 else 0.0
#         change = 0.0
#         direction = ""

#         if not previous_group.empty:
#             prev_category_group = previous_group[previous_group[chart.get('yAxis', {}).get('label')] == category]
#             prev_n = len(prev_category_group)
#             prev_valid = prev_category_group[prev_category_group[chart.get('xAxis', {}).get('label')].isin(['5', 5])]
#             prev_p = round(len(prev_valid) / prev_n * 100, 2) if prev_n > 0 else 0.0

#             change = round(p - prev_p, 1)
#             direction = "up" if change > 0 else ("down" if change < 0 else "")

#         records.append({
#             "category" : category,
#             "n" : n,
#             "p" : p,
#             "change" : change,
#             "rank" : 0,
#             "direction" : direction
#         })

#     return pd.DataFrame(records)

def map_chart_data(data: pd.DataFrame, dataset: dict) -> pd.DataFrame:
    transformer = DatasetTransformer(data, dataset)
    transformer_data = transformer.transform()
    return transformer_data

CALCULATE_CHART_MAPPINGS = {
    "NPS" : calculate_nps_components,
    "CSAT" : calculate_csat_components
}

def map_calculation_chart_components(data, chart, group_by):
    name = chart.get('name', '')

    data = data.groupby(group_by).apply(lambda df: CALCULATE_CHART_MAPPINGS[name](df, data, chart)).reset_index()
    
    dropped_column = f"level_{len(group_by)}"

    if dropped_column in list(data.columns):
        data.drop(columns=[f"level_{len(group_by)}"], inplace=True)

    return data
