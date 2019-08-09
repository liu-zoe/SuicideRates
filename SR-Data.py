###### Project Name: SuicideRates
###### Program Name: SR-Data.py
##### Purpose: To process the suicide rates data. 
##### Date Created: July 22nd 2019

#%%[markdown]
# Import packages for data processing
import csv
import pandas as pd
import numpy as np
#import xlrd
#%% [markdown]
#### load in suicide data
# master data contains the suicide rates
master=pd.read_csv('C:/Users/liuz2/Documents/Projects/SuicideRates/master.csv')
#%%[markdown]
#Get a list of the variable names
vars_master=list(master)
#%% [markdown]
#### Unemployment data
##### The reason of choosing National Estimates instead of OIL estimates
# The national estimates series is based on ILO estimates series and is harmonized
# to ensure comparability across countries and over time by accounting for differences
# in data source, scope of coverage, methodology, and other country-specific
# factors.  
uem=pd.read_csv('C:/Users/liuz2/Documents/Projects/SuicideRates/UEM.csv')
#Total unemployment (% of total labor force) National Estimates
uem_totl=uem[uem['Indicator Code']=='SL.UEM.TOTL.NE.ZS']
#Male unemployment (% of total labor force) National Estimates
uem_ma=uem[uem['Indicator Code']=='SL.UEM.TOTL.MA.NE.ZS']
#Female unemployment (% of total labor force) National Estimates
uem_fe=uem[uem['Indicator Code']=='SL.UEM.TOTL.FE.NE.ZS']

#%% Create a dataset with country code and country name
country=uem[['Country Name', 'Country Code']]
country.drop_duplicates(keep='first',inplace=True)
country.columns=['country','iso3c']
#Identify data that's above country level
not_country=["ARB","CEB", "CSS","EAP","EAR","EAS","ECA","ECS","EMU","EUU","FCS","HIC","HPC","IBD","IBT","IDA","IDB",
"IDX","INX","LAC","LCN","LDC","LIC","LMC","LMY","LTE","MEA","MIC","MNA","NAC","OED","OSS","PRE","PSS","PST","SAS","SSA","SSF","SST","TEA","TEC","TLA","TMN","TSA","TSS","UMC","WLD"]
country=country.assign(not_country=lambda x: x['iso3c'].isin(not_country))

#%%Transpose uem datasets into long datasets
def makelong(dat,varname):
    output_dat=dat.drop(['Indicator Name','Indicator Code','Country Name'],axis=1)
    output_dat=pd.melt(output_dat, id_vars=['Country Code'], var_name='year', value_name=varname)
    output_dat.columns=['iso3c','year',varname]
    return(output_dat)
uem_totl=makelong(uem_totl, 'UEM_TOTL')
uem_ma=makelong(uem_ma, 'UEM_MA')
uem_fe=makelong(uem_fe, 'UEM_FE')
del uem
#%% Merge uem datasets into one
uem=pd.merge(uem_totl, uem_ma, how='left', on=['iso3c','year'])
uem=pd.merge(uem, uem_fe, how='left', on=['iso3c','year'])
uem['year']=uem['year'].astype('int64')
del uem_fe, uem_ma, uem_totl
#%% Merge unemployment data (national estimates) into the master dataset
master=pd.merge(master, country, how='left', on=['country'])
master=pd.merge(master, uem, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])

#%% Create a variable UEM that is gender specific using sex, UEM_MA, and UEM_FE
master['UEM']=np.where(master['sex']=='male', master['UEM_MA'], master['UEM_FE'])

#%% [markdown]
# Create a dataset with country code and region name
cdat=pd.read_csv("C:/Users/liuz2/Documents/Projects/World Bank/whatawaste/country_level_data_2.csv", encoding="utf-8")
region=cdat[['region_id','country_name','income_id']]
# Mapping Region Labels against Region ID
regions= {
    'ECS': 'Europe and Central Asia',
    'SSF': 'Sub-Saharan Africa',
    'LCN': 'Latin America and the Caribbean',
    'EAS': 'East Asia and Pacific',
    'MEA': 'Middle East and North Africa',
    'SAS': 'South Asia',
    'NAC': 'North America', 
}
region['region']=region['region_id'].map(regions)
# Mapping Income Labels against Income ID
incomes={
    'HIC': 'High-income',
    'UMC': 'Upper-middle income',
    'LMC': 'Lower-middle income',
    'LIC': 'Low-income'
}
region['income']=region['income_id'].map(incomes)
region.columns=['region_id','country','income_id','region','income']
master=pd.merge(master, region, how='left',left_on=['country'], right_on=['country'])
del cdat

#%% [markdown]
# whr19 data contains the world happiness data published in 2019 
whr19=pd.read_csv('C:/Users/liuz2/Documents/Projects/SuicideRates/WHR19.csv')
whr19.columns=['country','year','LifeLadder','LogGDPPC','Social_support','Healthy_life_expectancy',\
    'Freedom_to_make_life_choice','Generosity','Perceptions_of_corruption','positive_affect','negative_affect',\
        'Confidence_in_government','Democratic_quality','Delivery_quality',\
        'LifeLadder_std', 'LifeLadder_std_mean', 'gini', 'gini_avg', 'gini_house',\
        'trust', 'trust84', 'trust93', 'trust98', 'trust04', 'trust09', 'trust14']
master=pd.merge(master, whr19, how='left', left_on=['country','year'], right_on=['country','year'])

#%%[markdown]
#### Gallup World Poll
##### Access to Internet
# Do you have access to the Internet in any way, whether on a mobile phone, a computer, or some other device?
gallup=pd.read_excel('C:/Users/liuz2/Documents/Projects/SuicideRates/Gallup_20190806.xlsx', \
    sheet_name='Access to the Internet', skiprows=7, usecols='B:C, E:F')
# Pivot the data
gallup.columns=['country','year','gender','value']
gallup=gallup.pivot_table(values='value', index=['country','year'],columns='gender')
internet=gallup.reset_index()
internet.columns=['country','year','internet','internet_f','internet_m']
del gallup
# print(min(internet['year']), max(internet['year']))
# Unfortunately, the access to internet data from the Gallup World Poll 
# ranges from 2015 to 2018, which only overlap two years with the suicide 
# rate data, which ranges from 1985 to 2016.

# Merge the internet data (2015 and 2016) to the SR data
master=pd.merge(master, internet, how='left', left_on=['country','year'], right_on=['country','year'])
#%%[markdown] 
##### Happiness (Life Ladder)
# Please imagine a ladder with steps numbered from 0 at the bottom to 10 at the top. 
# Suppose we say that the top of the ladder represents the best possible life for you, 
# and the bottom of the ladder represents the worst possible life for you. 
# On which step of the ladder would you say you personally feel you stand at this time, 
# assuming that the higher the step the better you feel about your life, 
# and the lower the step the worse you feel about it? Which step comes closest to the way you feel?

# Load in data on Happiness
gallup=pd.read_excel('C:/Users/liuz2/Documents/Projects/SuicideRates/Gallup_20190806.xlsx', \
    sheet_name='Life Today', skiprows=7, usecols='B:C, E:F')
# Pivot the data by gender
gallup.columns=['country','year','gender','value']
gallup=gallup.pivot_table(values='value', index=['country','year'],columns='gender')
happy=gallup.reset_index()
happy.columns=['country','year','happy','happy_f','happy_m']
del gallup

# Merge the happiness data (2006 to 2016) to the SR data
master=pd.merge(master, happy, how='left', left_on=['country','year'], right_on=['country','year'])

#%%[markdown] 
#### Take a look at the key variabless
# Country
master['country'].value_counts()
#%%[markdown]
# Region
master['region'].value_counts().sort_index()
#%%[markdown]
# Year
master['year'].value_counts().sort_index()
#%%[markdown]
# Gender Groups
master['sex'].value_counts().sort_index()
#%%[markdown] 
# Age Groups
master['age'].value_counts().sort_index()
#%%[markdown] 
# Generation Groups
master['generation'].value_counts().sort_index()
#%%[markdown] 
# Suicide Counts
master['suicides_no'].describe()
#%%[markdown] 
# HDI
master['HDI for year'].describe()
#%%
