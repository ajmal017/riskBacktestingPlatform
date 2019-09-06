import sqlalchemy
import pandas as pd
conn_LOCAL = sqlalchemy.create_engine(str(r"mssql+pymssql://sa:qwert!@#$%@10.3.135.32:1433/Tick_Data"))
df=pd.read_sql("SELECT * FROM [Tick_Data].[dbo].[FUTURE_REALTIME_QUOTATION]",conn_LOCAL).values[0][0]
df.head()