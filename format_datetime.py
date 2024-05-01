import pandas as pd
def format_datetime_columns(df):
    datetime_columns = ['RecievedDateTime', 'PrintDateTime']
    for col in datetime_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        df[col + '_Date'] = df[col].dt.strftime('%B %d, %Y')
        df[col + '_Time'] = df[col].dt.time.apply(lambda x: x.strftime('%I:%M:%S %p') if not pd.isnull(x) else '12:00:00 AM')
    return df