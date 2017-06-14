
# coding: utf-8

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')
import quandl
from pandas.tseries.offsets import *
import numpy as np
#import scipy ### DOESNT WORK ATM
import datetime


#Scrape the necessary data from the web
df_uncer = pd.read_excel("http://www.policyuncertainty.com/media/Global_Policy_Uncertainty_Data.xlsx")
df_vix = quandl.get("CBOE/VIX")

#Change the names of the columns in the Global Economic Policy Uncertainty index (GEPU index)
full_names = df_uncer.columns
df_uncer = df_uncer.rename(columns = {"Global EPU Index with Current Price GDP Weights": "EPU"})
df_uncer = df_uncer.rename(columns = {"Global EPU Index with   PPP-adjusted GDP Weights": "EPU_PPP"})
df_uncer = df_uncer[1:]

#Fix the index of the GEPU dataframe
idx = df_uncer.index.map(lambda x: '{}{}'.format(x[0], x[1]))
new_dates = pd.to_datetime(idx, format="%Y%m", dayfirst=False) + DateOffset(days = 14)
df_uncer = df_uncer.set_index(new_dates)
df_uncer.index.name = "Date"
df_uncer = df_uncer.drop(["EPU"], axis=1)

#Drop the bits we don't want in the VIX dataframe
df_vix = df_vix.drop(["VIX Open", "VIX High", "VIX Low"], axis=1)

#Combine the two dataframes
df_com = pd.merge(df_vix, df_uncer, left_index=True, right_index=True, how = "left")
df_com = df_com.astype(np.double)

#Plot the full graph with interpolated NaN
#df_com.interpolate().plot(linestyle="-", figsize=(16,10), secondary_y=["VIX Close"], mark_right=False)

#Rebase and combine in new dataframe and interpolate NaN
df_vix_i = df_vix / df_vix.ix["2004-01-15"]*100
df_uncer_i = df_uncer / df_uncer.ix["2004-01-15"]*100
df_com_i = pd.merge(df_vix_i, df_uncer_i, left_index=True, right_index=True, how = "left")
calc = df_com_i.interpolate()

#make master df
df_diff = pd.DataFrame({'Difference':[]})
df_diff["Difference"] = calc["EPU_PPP"]-calc["VIX Close"]

#Plot rebased dataframe
ax_i = df_com_i.interpolate().plot(linestyle="-", figsize=(16,10), mark_right=False)
ax_i.set_xlim([datetime.date(2004,1,1), datetime.date.today()])
ax_i.set_xlabel("Date")
ax_i.set_ylabel("Index (100 = 2004-01-15)")
ax_i.set_title("Global Economic Policy Uncertainty index vs VIX (Rebased)", fontsize=16)

ax_diff = df_diff.plot(linestyle="-", figsize=(16,10), mark_right=False)
ax_diff.set_xlabel("Date")
ax_diff.set_ylabel("Index (100 = 2004-01-15)")
plt.axhline(0, color='black')
ax_diff.set_title("Difference btw Global Economic Policy Uncertainty index and VIX (Rebased)", fontsize=16)
