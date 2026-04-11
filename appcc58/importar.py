import pandas as pd


df = pd.read_excel('c:/files/reporte.xlsx',sheet_name='detalle', usecols='A:B')  # Para archivos delimitados por punto y coma

print(df)
  
