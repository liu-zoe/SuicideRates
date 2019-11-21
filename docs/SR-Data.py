###### Project Name: SuicideRates
###### Program Name: SR-Data.py
##### Purpose: To process the suicide rates data. 
##### Date Created: August 21st 2019

#%%[markdown]
# Import packages for data processing
import csv
import pandas as pd
import numpy as np
#%% [markdown]
#### Load in suicide data
master=pd.read_excel('C:/Users/liuz2/Documents/Projects/SuicideRates/WHO_all.xlsx', \
    sheet_name='Sheet1', usecols='A:AM')    
master=master.rename(columns={'Countries':'country'})
# Remove rows that we don't have population or GDP data on
master=master[~master['country'].isin(['Rodrigues','Reunion','Occupied Palestinian Territory',\
    'Netherlands Antilles','Montserrat','Mayotte','Martinique','Anguilla','TFYR Macedonia',\
    'Saint Pierre and Miquelon','Falkland Islands (Malvinas)','French Guiana','Guadeloupe',\
    'Total reporting countries'])]
#%%
# Revise country names to match up other datasets
master['country']=np.where(master['country']=='Bahamas', 'Bahamas, The', 
    np.where(master['country']=='Egypt', 'Egypt, Arab Rep.',
    np.where(master['country']=='Hong Kong SAR', 'Hong Kong SAR, China',
    np.where(master['country']=='Iran (Islamic Rep of)', 'Iran, Islamic Rep.',
    np.where(master['country']=='Kyrgyzstan', 'Kyrgyz Republic', 
    np.where(master['country']=='Macau', 'Macao SAR, China', 
    np.where(master['country']=='Republic of Moldova','Moldova',
    np.where(master['country']=='Republic of Korea', 'Korea, Rep.',
    np.where(master['country']=='Saint Kitts and Nevis', 'St. Kitts and Nevis',
    np.where(master['country']=='Saint Lucia', 'St. Lucia',
    np.where(master['country']=='Saint Vincent and Grenadines', 'St. Vincent and the Grenadines',
    np.where(master['country']=='Slovakia','Slovak Republic', 
    np.where(master['country']=='United States of America','United States',
    np.where(master['country']=='Venezuela (Bolivarian Republic of)','Venezuela, RB',
    np.where(master['country']=='Virgin Islands (USA)','Virgin Islands (U.S.)',   
    master['country'])))))))))))))))
# Transpose into long format
master=pd.melt(master, id_vars=['country'], var_name='year', value_name='suicides_no')
master['year']=master['year'].astype('int64')
master['suicides_no'] = pd.to_numeric(master['suicides_no'],errors='coerce')

#%% [markdown]
#### Unemployment data
##### The reason of choosing National Estimates instead of OIL estimates
# The national estimates series is based on ILO estimates series and is harmonized
# to ensure comparability across countries and over time by accounting for differences
# in data source, scope of coverage, methodology, and other country-specific
# factors.  
uem=pd.read_csv('C:/Users/liuz2/Documents/Projects/SuicideRates/UEM.csv')
#Total unemployment (% of total labor force) National Estimates
uem=uem[uem['Indicator Code']=='SL.UEM.TOTL.NE.ZS']
#Create a dataset with country code and country name
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
uem=makelong(uem, 'UEM_TOTL')
uem['year']=uem['year'].astype('int64')

#%% Merge unemployment data (national estimates) into the master dataset
master=pd.merge(master, country, how='left', on=['country'])
master=pd.merge(master, uem, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])

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
#%%
master['region']=np.where(master['iso3c']=='STP', 'Sub-Saharan Africa', master['region'])
master['region_id']=np.where(master['iso3c']=='STP', 'SSF', master['region_id'])

#%%[markdown]
#### Population data
popu=pd.read_csv('C:/Users/liuz2/Documents/Projects/World Bank/Population/API_SP.POP.TOTL_DS2_en_csv_v2_10576638.csv', encoding="utf-8", skiprows=4)
popu=popu.drop(['Unnamed: 63','2018','Indicator Name','Indicator Code','Country Name'],axis=1)
populong=pd.melt(popu, id_vars=['Country Code'], var_name='year', value_name='pop')
populong.columns=['iso3c','year','population']
populong['year']=populong['year'].astype('int64')
master=pd.merge(master, populong, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])
del popu
#%%[markdown]
#### GDP PPP 2011 constant International 
gdp=pd.read_csv('C:/Users/liuz2/Documents/Projects/World Bank/GDP/GDP-Per-Capita-PPP-Constant-2011-International/API_NY.GDP.PCAP.PP.KD_DS2_en_csv_v2_41408.csv',\
     encoding='utf-8', skiprows=4, nrows=264)
gdp=gdp.drop(['Indicator Name', 'Indicator Code', 'Country Name', 'Unnamed: 63'], axis=1)
gdplong=pd.melt(gdp, id_vars=['Country Code'], var_name='year', value_name='gdp')
gdplong.columns=['iso3c','year','gdp']
gdplong.year=gdplong.year.str.slice(0,4)
gdplong['gdp']=pd.to_numeric(gdplong['gdp'], errors='coerce') 
gdplong['loggdp']=np.log(gdplong['gdp'])
gdplong['year']=gdplong['year'].astype('int64')
master=pd.merge(master,gdplong, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])
del gdp

#%%[markdown]
#### GDP PPP Current International 
gdp2=pd.read_csv('C:/Users/liuz2/Documents/Projects/World Bank/GDP/GDP-PPP-Current-International/API_NY.GDP.MKTP.PP.CD_DS2_en_csv_v2_10580622.csv', \
    encoding='utf-8', skiprows=4, nrows=264)
gdp2=gdp2.drop(['Indicator Name', 'Indicator Code', 'Country Name', 'Unnamed: 63'], axis=1)
gdplong2=pd.melt(gdp2, id_vars=['Country Code'], var_name='year', value_name='gdp_')
gdplong2.columns=['iso3c','year','gdp_']
gdplong2.year=gdplong2.year.str.slice(0,4)
gdplong2['gdp_']=pd.to_numeric(gdplong2['gdp_'], errors='coerce') 
gdplong2['year']=gdplong2['year'].astype('int64')
master=pd.merge(master,gdplong2, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])
master['gdp2']=master['gdp_']/master['population']
master['loggdp2']=np.log(master['gdp2'])
master=master.drop(['gdp_'],axis=1)
del gdp2
#%%[markdown]
#### Gini
gini=pd.read_csv('C:/Users/liuz2/Documents/Projects/World Bank/Gini/API_SI.POV.GINI_DS2_en_csv_v2_126296.csv', encoding='utf-8', nrows=264)
gini=gini.drop(['Indicator Name','Indicator Code','Country Name'], axis=1)
ginilong=pd.melt(gini, id_vars=['Country Code'], var_name='year', value_name='gini')
ginilong.columns=['iso3c','year','gini']
ginilong['gini']=pd.to_numeric(ginilong['gini'], errors='coerce') 
ginilong['year']=ginilong['year'].astype('int64')
master=pd.merge(master,ginilong, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])
del gini

#%%[markdown]
#### Consumer Price Index ###
cpi=pd.read_csv('C:/Users/liuz2/Documents/Projects/World Bank/ConsumerPriceIndex/API_FP.CPI.TOTL_DS2_en_csv_v2_315921.csv', \
    encoding='utf-8', skiprows=4, nrows=264)
cpi=cpi.drop(['Indicator Name','Indicator Code','Country Name', 'Unnamed: 63'], axis=1)
cpilong=pd.melt(cpi, id_vars=['Country Code'], var_name='year', value_name='cpi')
cpilong.columns=['iso3c','year','cpi']
cpilong['cpi']=pd.to_numeric(cpilong['cpi'], errors='coerce') 
cpilong['year']=cpilong['year'].astype('int64')
master=pd.merge(master,cpilong, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])
del cpi
#%% [markdown]
# whr19 data contains the world happiness data published in 2019 
whr19=pd.read_csv('C:/Users/liuz2/Documents/Projects/SuicideRates/WHR19.csv')
whr19.columns=['country','year','LifeLadder','LogGDPPC','Social_support','Healthy_life_expectancy',\
    'Freedom_to_make_life_choice','Generosity','Perceptions_of_corruption','positive_affect','negative_affect',\
        'Confidence_in_government','Democratic_quality','Delivery_quality',\
        'LifeLadder_std', 'LifeLadder_std_mean', 'gini_whr','gini_avg', 'gini_house',\
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
#%%
# Create suicide rates per 100k 
master['suicides/100kpop']=master['suicides_no']/(master['population']/100000)