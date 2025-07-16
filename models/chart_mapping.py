import pandas as pd

def create_chart_data(data, dataset):
    df = data[dataset.get('used-cols', [])].copy()

    if "replaced-columns" in dataset.keys():
        for column_name, value in dataset.get('replaced-columns', {}).items():
            df[column_name] = value

    if "rename-columns" in dataset.keys():
        df = df.rename(columns=dataset.get('rename-columns', {}))
    
    if "wide_to_long" in dataset.keys():
        stubnames = list(dataset.get('wide_to_long', {}).get('stubnames', {}).keys())
        i = dataset.get('wide_to_long', {}).get('i-cols', [])
        j = dataset.get('wide_to_long', {}).get('j-col', '')

        df_new = pd.wide_to_long(
            df,
            stubnames=stubnames,
            i = i,
            j = j,
            sep='###',
            suffix='\\d+'
        )

        df_new = df_new.reset_index().drop(columns=[j])
    else:
        df_new = df.copy()
    
    if "stack" in dataset.keys():
        stack = dataset.get('stack', {})

        index_list = stack.get('group_by', [])  

        if "renamed_columns" in stack.keys():
            renamed_columns = stack.get('renamed_columns', {})

        df_new = df_new.set_index(index_list).stack().reset_index()
        df_new.columns = df_new.columns.map(str)
        df_new.rename(columns=renamed_columns, inplace=True)

        if "replaced_categories" in stack.keys():
            df_new = df_new.replace(stack.get('replaced_categories', {}))

    if "drop-na-columns" in dataset.keys():
        df_new = df_new.dropna(subset=dataset.get('drop-na-columns', []))

    return df_new

def calculate_nps_components(group, root_data, dataset):
    chart = dataset.get('chart', {})
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

def calculate_csat_components(group, root_data, dataset):
    chart = dataset.get('chart', {})
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    wave = group['Wave'].unique().tolist()[0]
    bank = group['Bank'].unique().tolist()[0]

    cur_month = wave[:3]
    cur_year = wave[-2:]

    if cur_month == 'Jan':
        cur_year -= 1
    
    previous_group = pd.DataFrame()

    if cur_month in months:
        previous_wave = f'{months[months.index(cur_month) - 1]}\'{cur_year}'

        previous_group = root_data[((root_data['Wave'] == previous_wave) & (root_data['Bank'] == bank))]

    prev_total = len(previous_group)

    categories = chart.get('yAxis', {}).get('categories', [])

    records = []
    
    for category in categories:
        category_group = group[group[chart.get('yAxis', {}).get('label')] == category]
        n = len(category_group) 
        valid = category_group[category_group[chart.get('xAxis', {}).get('label')].isin(['5', 5])] #['Not use in recent 1 month', 'I do not use this bank product']
        p = round(len(valid) / n * 100, 2) if n > 0 else 0.0
        change = 0.0
        direction = ""

        if not previous_group.empty:
            prev_category_group = previous_group[previous_group[chart.get('yAxis', {}).get('label')] == category]
            prev_n = len(prev_category_group)
            prev_valid = prev_category_group[prev_category_group[chart.get('xAxis', {}).get('label')].isin(['5', 5])]
            prev_p = round(len(prev_valid) / prev_n * 100, 2) if prev_n > 0 else 0.0

            change = round(p - prev_p, 1)
            direction = "up" if change > 0 else ("down" if change < 0 else "")

        records.append({
            "category" : category,
            "n" : n,
            "p" : p,
            "change" : change,
            "rank" : 0,
            "direction" : direction
        })

    return pd.DataFrame(records)

CHART_MAPPINGS = {
    "NPS" : create_chart_data,
    "CSAT" : create_chart_data
}

def map_chart_data(data, dataset):
    name = dataset.get('chart', {}).get('name', '')
    return CHART_MAPPINGS[name](data, dataset)

CALCULATE_CHART_MAPPINGS = {
    "NPS" : calculate_nps_components,
    "CSAT" : calculate_csat_components
}

def map_calculation_chart_components(data, dataset):
    name = dataset.get('chart', {}).get('name', '')
    data = data.groupby(dataset.get('group_by', [])).apply(lambda df: CALCULATE_CHART_MAPPINGS[name](df, data, dataset)).reset_index()
    return data
