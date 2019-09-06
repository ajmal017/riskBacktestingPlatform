# encoding: UTF-8

import os
import sys

# 将根目录路径添加到环境变量中
ROOT_PATH =os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.append(ROOT_PATH)
import pandas as pd 

paramFilename='vnpy/trader/app/ctaStrategy/HedgeResult.csv'
path=os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
path=os.path.join(path,paramFilename)	
HedgeResult = pd.read_csv(path)
print type(HedgeResult)