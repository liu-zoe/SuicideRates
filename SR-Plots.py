###### Project Name: SuicideRates
###### Program Name: SR-Plots.py
##### Purpose: To generates polished plots for data story
##### Date Created: Nov 8th 2019
#%%
# import libraries
import csv
import math
import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import seaborn as sns
import chart_studio.plotly as py
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import colorlover as cl

master=pd.read_excel('C:/Users/liuz2/Documents/Projects/SuicideRates/WHO_all.xlsx', \
    sheet_name='Sheet1', usecols='A:AM')    
master=master.rename(columns={'Countries':'country'})
# Remove rows that we don't have population or GDP data on
master=master[~master['country'].isin(['Rodrigues','Reunion','Occupied Palestinian Territory',\
    'Netherlands Antilles','Montserrat','Mayotte','Martinique','Anguilla','TFYR Macedonia',\
    'Saint Pierre and Miquelon','Falkland Islands (Malvinas)','French Guiana','Guadeloupe',\
    'Total reporting countries'])]
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

# Unemployment Rate Data
uem=pd.read_csv('C:/Users/liuz2/Documents/Projects/SuicideRates/UEM.csv')
uem=uem[uem['Indicator Code']=='SL.UEM.TOTL.NE.ZS']
country=uem[['Country Name', 'Country Code']]
country.columns=['country','iso3c']
not_country=["ARB","CEB", "CSS","EAP","EAR","EAS","ECA","ECS","EMU","EUU","FCS","HIC","HPC","IBD","IBT","IDA","IDB",
"IDX","INX","LAC","LCN","LDC","LIC","LMC","LMY","LTE","MEA","MIC","MNA","NAC","OED","OSS","PRE","PSS","PST","SAS","SSA","SSF","SST","TEA","TEC","TLA","TMN","TSA","TSS","UMC","WLD"]
country=country.assign(not_country=lambda x: x['iso3c'].isin(not_country))
def makelong(dat,varname):
    output_dat=dat.drop(['Indicator Name','Indicator Code','Country Name'],axis=1)
    output_dat=pd.melt(output_dat, id_vars=['Country Code'], var_name='year', value_name=varname)
    output_dat.columns=['iso3c','year',varname]
    return(output_dat)
uem=makelong(uem, 'Unemployment')
uem['year']=uem['year'].astype('int64')
master=pd.merge(master, country, how='left', on=['country'])
master=pd.merge(master, uem, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])

#Population
popu=pd.read_csv('C:/Users/liuz2/Documents/Projects/World Bank/Population/API_SP.POP.TOTL_DS2_en_csv_v2_10576638.csv', encoding="utf-8", skiprows=4)
popu=popu.drop(['Unnamed: 63','2018','Indicator Name','Indicator Code','Country Name'],axis=1)
populong=pd.melt(popu, id_vars=['Country Code'], var_name='year', value_name='pop')
populong.columns=['iso3c','year','population']
populong['year']=populong['year'].astype('int64')
master=pd.merge(master, populong, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])
del popu
#GDP
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
# Gini
gini=pd.read_csv('C:/Users/liuz2/Documents/Projects/World Bank/Gini/API_SI.POV.GINI_DS2_en_csv_v2_126296.csv', encoding='utf-8', nrows=264)
gini=gini.drop(['Indicator Name','Indicator Code','Country Name'], axis=1)
ginilong=pd.melt(gini, id_vars=['Country Code'], var_name='year', value_name='gini')
ginilong.columns=['iso3c','year','gini']
ginilong['gini']=pd.to_numeric(ginilong['gini'], errors='coerce') 
ginilong['year']=ginilong['year'].astype('int64')
master=pd.merge(master,ginilong, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])
del gini
#Consumer Price Index
cpi=pd.read_csv('C:/Users/liuz2/Documents/Projects/World Bank/ConsumerPriceIndex/API_FP.CPI.TOTL_DS2_en_csv_v2_315921.csv', \
    encoding='utf-8', skiprows=4, nrows=264)
cpi=cpi.drop(['Indicator Name','Indicator Code','Country Name', 'Unnamed: 63'], axis=1)
cpilong=pd.melt(cpi, id_vars=['Country Code'], var_name='year', value_name='cpi')
cpilong.columns=['iso3c','year','cpi']
cpilong['cpi']=pd.to_numeric(cpilong['cpi'], errors='coerce') 
cpilong['year']=cpilong['year'].astype('int64')
master=pd.merge(master,cpilong, how='left', left_on=['iso3c','year'], right_on=['iso3c','year'])
del cpi

master['SR']=master['suicides_no']/(master['population']/100000)
SR_country=master[(master['suicides_no']>=0) & (master['population']>0)]
SR_country['Top']=np.where(SR_country['country'].isin(['Lithuania', 'Hungary']), SR_country['country'], 'Other')
SR_country['country_yr']=SR_country.apply(lambda cat: cat.country+str(cat.year), axis=1)
allcountry=list(set(SR_country['country']))
allcountry.sort()

top5=dict() #Record the rank of the top 5 countries by year
top5_ctr=dict() #Tabulate the counts for each country
tmp=list()
for year in range(1979,2017):
    top5[year]=list(SR_country[SR_country['year']==year][['country', 'SR']].sort_values(by=['SR'],ascending=False).head(5)['country'])
    for country in top5[year]:
        SR=SR_country[(SR_country['year']==year) & (SR_country['country']==country)][['SR']].iloc[0,0]
        tmp.append([country, year, SR])
        if country in top5_ctr.keys():
            top5_ctr[country]=top5_ctr[country]+1
        else:
            top5_ctr[country]=1
top5_data=pd.DataFrame(tmp, columns=['country','year','SR'])
del tmp, SR
top5_count=pd.DataFrame(sorted(top5_ctr.items(), key=lambda kv: kv[1], reverse=True), columns=['country','count'])

top5_ctr2=dict()#Flip top5_ctr to have countries of the same frequency collapse into one entry
for k, v in top5_ctr.items():
    if v in top5_ctr2.keys():
        top5_ctr2[v]=top5_ctr2[v]+'; '+k
    else: 
        top5_ctr2[v]=k
top5_count2=pd.DataFrame(sorted(top5_ctr2.items(), key=lambda kv: kv[0]), columns=['count','country'])
top5_count2['x_lab']=np.where(top5_count2['count']==1, 'Luxembourg ...',
                    np.where(top5_count2['count']==2, 'Belgium ...',
                    np.where(top5_count2['count']==5, 'Austria ...',
                    np.where(top5_count2['count']==12, 'Estonia ...', 
                    np.where(top5_count2['count']==23, 'Russia', 
                    top5_count2['country'])))))
del k, v

USSR=['Armenia', 'Azerbaijan', 'Belarus', 'Estonia', 'Georgia','Kazakhstan',\
    'Kyrgyz Republic', 'Latvia', 'Lithuania', 'Moldova', 'Russian Federation',\
    'Tajikistan', 'Turkmenistan', 'Ukraine', 'Uzbekistan']
USSR1=['Lithuania','Russian Federation','Latvia','Belarus', 'Estonia', 'Kazakhstan', 'Ukraine']
USSR2=['Moldova','Kyrgyz Republic','Turkmenistan','Uzbekistan','Georgia','Tajikistan','Azerbaijan','Armenia']
USSR_dat=SR_country[SR_country['country'].isin(USSR)]
USSR_dat1=SR_country[SR_country['country'].isin(USSR1)]
USSR_dat2=SR_country[SR_country['country'].isin(USSR2)]
USSR_dat1_avg=USSR_dat1.groupby(['year'])[['SR','gdp']].mean().reset_index()
USSR_dat2_avg=USSR_dat2.groupby(['year'])[['SR','gdp']].mean().reset_index()

# Create a function to make line traces in batch
def make_line_trace(
    indat, #Input Data
    x, #x axis variable
    y, #y axis variable
    name='', #Name for the legend
    mode='lines+markers', #type of plot
    label='' #text label
):
    return(
    go.Scatter(
        x=indat[x],
        y=indat[y],
        name=name,
        mode=mode,
        text=label        
    )
)

def corrmat(country):
    tmp=SR_country[SR_country['country']==country]
    corr1=round(tmp[(tmp['gdp'].isnull()==0) & (tmp['SR'].isnull()==0)][['gdp','SR']].corr().iloc[0,1],3)
    corr2=round(tmp[(tmp['Unemployment'].isnull()==0) & (tmp['SR'].isnull()==0)][['Unemployment','SR']].corr().iloc[0,1],3)
    corr3=round(tmp[(tmp['cpi'].isnull()==0) & (tmp['SR'].isnull()==0)][['cpi','SR']].corr().iloc[0,1],3)
    corr4=round(tmp[(tmp['gini'].isnull()==0) & (tmp['SR'].isnull()==0)][['gini','SR']].corr().iloc[0,1],3)
    #print(corr1, corr2, corr3)
    maxval=' '
    maxcorr=0
    if (abs(corr1)==1):
        corr1=0
    if (abs(corr2)==1):
        corr2=0
    if (abs(corr3)==1):
        corr3=0
    if (abs(corr4)==1):
        corr4=0
    if (math.isnan(corr1)==False): 
        maxcorr=abs(corr1)
        maxval='GDP'
    if (math.isnan(corr2)==False):
        maxcorr=max(maxcorr, abs(corr2))
        if (maxcorr==abs(corr2)):
            maxval='UEM'
    if (math.isnan(corr3)==False):
        maxcorr=max(maxcorr, abs(corr3))
        if (maxcorr==abs(corr3)):
            maxval='CPI'
    if (math.isnan(corr4)==False):
        maxcorr=max(maxcorr, abs(corr4))
        if (maxcorr==abs(corr4)):
            maxval='GINI'
    corr=[country, corr1, corr2, corr3, corr4, maxcorr, maxval]
    del tmp,corr1,corr2, corr3, corr4, maxval, maxcorr
    return(corr)

SR_corr_mat=[]
allcountry=list(set(SR_country['country']))
allcountry.sort()
for country in allcountry:
    SR_corr_mat.append(corrmat(country))
SR_corr_mat=pd.DataFrame(SR_corr_mat, columns=['country','gdp','unemployment','cpi','gini', 'max', 'max_col'])
USSR1_corr=SR_corr_mat[SR_corr_mat['country'].isin(USSR1)][['country','gdp']].sort_values(by=['gdp'])
USSR2_corr=SR_corr_mat[SR_corr_mat['country'].isin(USSR2)][['country','gdp']].sort_values(by=['gdp'])

#Asia
Asia_ctr=['Japan', 'Hong Kong SAR, China', 'Korea, Rep.','Thailand','Malaysia','Philippines']
OthAsiaCtr=['Korea, Rep.','Thailand','Malaysia','Philippines']
Japan=SR_country[SR_country['country']=='Japan']
Hongkong=SR_country[SR_country['country']=='Hong Kong SAR, China']
Korea=SR_country[SR_country['country']=='Korea, Rep.']
Thailand=SR_country[SR_country['country']=='Thailand']
Malaysia=SR_country[SR_country['country']=='Malaysia']
Philippines=SR_country[SR_country['country']=='Philippines']

OtherAsia=SR_country[SR_country['country'].isin(OthAsiaCtr)]
Asia_corr1=SR_corr_mat[SR_corr_mat['country'].isin(['Japan','Hong Kong SAR, China'])]
Asia_corr2=SR_corr_mat[SR_corr_mat['country'].isin(OthAsiaCtr)]

# Correlation matrix
SR_corr_mat=SR_corr_mat[SR_corr_mat['max']>0]
corr_gdp=SR_corr_mat[SR_corr_mat['max_col']=='GDP'].reset_index()
corr_uem=SR_corr_mat[SR_corr_mat['max_col']=='UEM'].reset_index()
corr_cpi=SR_corr_mat[SR_corr_mat['max_col']=='CPI'].reset_index()
corr_gini=SR_corr_mat[SR_corr_mat['max_col']=='GINI'].reset_index()

#%%
# Plot 1 - Suicide Rates by Country across Time
#init_notebook_mode(connected=True)
All_ctr_trace=[]
for country in allcountry:
    tmp=SR_country[SR_country['country']==country]
    All_ctr_trace.append(
        go.Scatter(x=tmp['year'],y=tmp['SR'],
            mode='lines+markers',
            name=country,
            text=tmp['year'],
            hovertemplate='%{text}'+'<br>SR:%{y:1f}',
            )
        )
del tmp
fig = go.Figure(data=All_ctr_trace, 
    layout=dict(title = 'Suicide Rates from 1979 to 2016',
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                    gridcolor='rgba(255, 255, 255, 0.5)',
                ),
                xaxis = dict(zeroline = False,
                    title='Year',
                    gridcolor='rgba(255, 255, 255, 0.5)',
              ), 
                font=dict(family='Raleway', size=13, color='rgba(255, 255, 255, 0.5)')
             ))
#fig
py.iplot(fig)

#%%
# Plot 2 Top 5 Countries across Time
#init_notebook_mode(connected=True)
top5_trace=[]
for country in list(top5_count['country']):
    tmp=top5_data[top5_data['country']==country]

    if country in ['Lithuania', 'Hungary']:
        top5_trace.append(
            go.Scatter(
                x=tmp['year'],y=tmp['SR'],
                mode='lines+markers',
                name=country,
                text=tmp['year'],
                hovertemplate='%{text}'+'<br>SR:%{y:1f}',
            )
        )
    else:
        top5_trace.append(
            go.Scatter(
                x=tmp['year'],y=tmp['SR'],
                mode='markers',
                name=country,
                text=tmp['year'],
                hovertemplate='%{text}'+'<br>SR:%{y:1f}',
            )
        )
fig = go.Figure(data=top5_trace, 
    layout=dict(title = 'Top 5 Countries in Suicide Rates by Year',
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                    gridcolor='rgba(255, 255, 255, 0.5)',
                ),
                xaxis = dict(zeroline = False,
                    title='Year',
                    gridcolor='rgba(255, 255, 255, 0.5)',
              ), 
                font=dict(family='Raleway', size=13, 
                color='rgba(255, 255, 255, 0.5)'),
             )
    )
#fig
py.iplot(fig)
#%%
# Plot 3 - Bar chart of the top 5 countries
#init_notebook_mode(connected=True)
blues9=cl.scales['9']['seq']['Blues']
SR_blues=cl.interp(blues9, 12)
top5_trace_bar=go.Bar(
    x=top5_count2['count'],
    y=top5_count2['x_lab'],
    orientation='h',
    name='Top5 Count',
    text=list(top5_count2['country']),
    hovertemplate='%{text}: %{x}',
    marker=dict(color=SR_blues),
    marker_line_color='rgba(0,0,0,0)',
)
fig=go.Figure(data=[top5_trace_bar], 
            layout=dict(title='How Freqent a Country Ranks Top 5 in Suicide Rates',
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.5)',),
                    font=dict(family='Raleway', size=12, 
                            color='rgba(255, 255, 255, 0.5)')
))
#fig
py.iplot(fig)
#%%
dark=cl.scales['4']['qual']['Dark2']
# %% 
# Plot 4 - Scatterplots of SR and GDP
#init_notebook_mode(connected=True)
fig = go.Figure(data=go.Scatter(
                    x=SR_country['gdp'], y=SR_country['SR'], 
                    mode='markers', marker=dict(color=dark[0], size=3),
                    text=SR_country['country_yr'],name='GDP',
                    hovertemplate='%{text}'+'<br>SR: %{y:1f}'+'<br>GDP: %{x:1f}'),
    layout=dict(title = 'Suicide Rates and GDP',
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                    gridcolor='rgba(255, 255, 255, 0.5)',
                ),
                xaxis = dict(zeroline = False,
                    title='GDP per capita (PPP constant in 2011 international $)',
                    gridcolor='rgba(255, 255, 255, 0.5)',
              ), 
                font=dict(family='Raleway', size=12, 
                color='rgba(255, 255, 255, 0.5)')
             ))
#fig
py.iplot(fig)
#%%
# Plot 5 - Scatterplots of SR and Unemployment
#init_notebook_mode(connected=True)
fig = go.Figure(data=go.Scatter(
                    x=SR_country['Unemployment'], y=SR_country['SR'], 
                    mode='markers', marker=dict(color=dark[2], size=3),
                    text=SR_country['country_yr'],name='Unemployment',
                    hovertemplate='%{text}'+'<br>SR: %{y:1f}'+'<br>Unemployment: %{x:1f}'),
    layout=dict(title = 'Suicide Rates and Unemployment',
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                    gridcolor='rgba(255, 255, 255, 0.5)',
                ),
                xaxis = dict(zeroline = False,
                    title='Unemployment Rate (%)',
                    gridcolor='rgba(255, 255, 255, 0.5)',
              ), 
                font=dict(family='Raleway', size=12, 
                color='rgba(255, 255, 255, 0.5)')
             ))
#fig
py.iplot(fig)
#%%
# Plot 6 - Scatterplots of SR and CPI
#init_notebook_mode(connected=True)
fig = go.Figure(data=go.Scatter(
                    x=SR_country['cpi'], y=SR_country['SR'], 
                    mode='markers', marker=dict(color=dark[1], size=3),
                    text=SR_country['country_yr'],name='CPI',
                    hovertemplate='%{text}'+'<br>SR: %{y:1f}'+'<br>CPI: %{x:1f}'),
    layout=dict(title = 'Suicide Rates and Consumer Price Index',
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                    gridcolor='rgba(255, 255, 255, 0.5)',
                ),
                xaxis = dict(zeroline = False,
                    title='Consumer Price Index (2010=100)',
                    gridcolor='rgba(255, 255, 255, 0.5)',
              ), 
                font=dict(family='Raleway', size=12, 
                color='rgba(255, 255, 255, 0.5)')
             ))
#fig
py.iplot(fig)
#%%
# Plot 7 - Scatterplots of SR and Gini
#init_notebook_mode(connected=True)
fig = go.Figure(data=go.Scatter(x=SR_country['gini'], y=SR_country['SR'], 
                    mode='markers', marker=dict(color=dark[3], size=3),
                    text=SR_country['country_yr'],name='Gini',
                    hovertemplate='%{text}'+'<br>SR: %{y:1f}'+'<br>Gini: %{x:1f}'),
    layout=dict(title = 'Suicide Rates and Gini Coefficient',
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                    gridcolor='rgba(255, 255, 255, 0.5)',
                ),
                xaxis = dict(zeroline = False,
                    title='Gini Coefficient',
                    gridcolor='rgba(255, 255, 255, 0.5)',
              ), 
                font=dict(family='Raleway', size=12, 
                color='rgba(255, 255, 255, 0.5)')
             ))
#fig
py.iplot(fig)
#%%
'''
# Plot 4-7 - subplot versions (file too big for online plots)
init_notebook_mode(connected=True)
fig = make_subplots(rows=2, cols=2, shared_yaxes=True,
                    subplot_titles=('GDP per capita (2011 PPP $)', 
                    'Unemployment Rate', 'Consumer Price Index (2010=100)', 'Gini Index'))
fig.add_trace(go.Scatter(x=SR_country['gdp'], y=SR_country['SR'], mode='markers', 
text=SR_country['country_yr'],name='GDP',
hovertemplate='%{text}'+'<br>SR: %{y:1f}'+'<br>GDP: %{x:1f}'), 1,1)

fig.add_trace(go.Scatter(x=SR_country['Unemployment'], y=SR_country['SR'],mode='markers', 
text=SR_country['country_yr'],name='Unemployment',
hovertemplate='%{text}'+'<br>SR: %{y:1f}'+'<br>Unemployment: %{x:1f}'),1,2)

fig.add_trace(go.Scatter(x=SR_country['cpi'], y=SR_country['SR'],mode='markers',
text=SR_country['country_yr'],name='CPI',
hovertemplate='%{text}'+'<br>SR: %{y:1f}'+'<br>CPI: %{x:1f}'), 2,1)

fig.add_trace(go.Scatter(x=SR_country['gini'], y=SR_country['SR'],mode='markers', 
text=SR_country['country_yr'],name='Gini',
hovertemplate='%{text}'+'<br>SR: %{y:1f}'+'<br>Gini: %{x:1f}'), 2,2)

fig.update_yaxes(title_text="SR per 100k", row=1, col=1)
fig.update_yaxes(title_text="SR per 100k", row=2, col=1)
fig.update_layout(template='plotly_dark', showlegend=False,
                    height=600, width=600,
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Raleway', size=10, 
                              color='rgba(255, 255, 255, 0.5)'))
'''
# %% 
# Plot 8 - USSR1 Average
#init_notebook_mode(connected=True)
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(
    x=USSR_dat1_avg['year'], 
    y=USSR_dat1_avg['SR'], 
    mode='lines+markers', 
    marker=dict(color=SR_blues[9]), 
    line=dict(color=SR_blues[9]),
    name='SR',
    text=USSR_dat1_avg['year'],
    hovertemplate='%{text}'+'<br>SR: %{y:1f}',
    )
)
fig.add_trace(go.Scatter(
    x=USSR_dat1_avg['year'], 
    y=USSR_dat1_avg['gdp'], 
    mode='lines+markers', 
    marker=dict(color=dark[0]), 
    line=dict(color=dark[0]),
    name='GDP',
    text=USSR_dat1_avg['year'], 
    hovertemplate='%{text}'+'<br>GDP: %{y:1f}',
    yaxis='y2'
    )
)
# Add text to the Rectangle
fig.add_trace(
    go.Scatter(
        x=[1990],
        y=[38.5],
        showlegend=False,
        hoverinfo='skip',
        mode='text',
        text=['Year 91-95'],
    )
)
# Add Rectangle 
fig.add_shape(
    go.layout.Shape(
        type='rect',
        x0=1991,
        y0=19,
        x1=1995,
        y1=37,
        line=dict(
            color='rgba(255, 255, 255, 0.5)', 
            width=1, dash='dot'
        )
    )
)
fig.update_shapes(dict(xref='x', yref='y'))
fig.update_layout(
    title_text='Average Suicide Rate and GDP in USSR Cohort 1:\
        <br>Ukraine, Belarus, Lithuania, Latvia, \
        <br>Kazakhstan, Estonia, Russia',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='GDP', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=11, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)
# %% 
# Plot 8b - USSR1
'''
init_notebook_mode(connected=True)
YGB9=cl.scales['9']['seq']['YlGnBu']
YOR9=cl.scales['9']['seq']['YlOrRd']
USSR1A_trace=[]
USSR1B_trace=[]
i=9
for country in USSR1:
    indat=USSR_dat1[(USSR_dat1['country']==country) & (USSR_dat1['year'].isin([1991,1992,1993,1994,1995]))]
    i=i-1
    USSR1A_trace.append(go.Scatter(
        x=indat['year'],
        y=indat['SR'],
        mode='lines+markers',
        marker=dict(color=YGB9[i]),
        line=dict(color=YGB9[i]),
        #legendgroup='USSR1SR',
        text=indat['country_yr'],
        name='SR-'+country,
        hovertemplate='%{text}'+'<br>SR: %{y:1f}'
            ),
        )
    USSR1B_trace.append(go.Scatter(
        x=indat['year'],
        y=indat['gdp'],
        mode='lines+markers',
        marker=dict(color=YOR9[i]),
        line=dict(color=YOR9[i]),
        #legendgroup='USSR1GDP',
        text=indat['country_yr'],
        name='GDP-'+country,
        hovertemplate='%{text}'+'<br>GDP: %{y:1f}',
        yaxis='y2'
            ),
        )
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_traces(USSR1A_trace)
fig.add_traces(USSR1B_trace)

fig.update_layout(
    title_text='Suicide and GDP in USSR Cohort 1',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='GDP', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=12, 
              color='rgba(255, 255, 255, 0.5)')
)
del indat, i
fig
#py.iplot(fig)
'''
# %%
# Plot 9 - USSR2 Average
#init_notebook_mode(connected=True)
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(
    x=USSR_dat2_avg['year'], 
    y=USSR_dat2_avg['SR'], 
    mode='lines+markers', 
    marker=dict(color=SR_blues[9]), 
    line=dict(color=SR_blues[9]),
    name='SR',
    text=USSR_dat2_avg['year'],
    hovertemplate='%{text}'+'<br>SR: %{y:1f}',
    )
)
fig.add_trace(go.Scatter(
    x=USSR_dat2_avg['year'], 
    y=USSR_dat2_avg['gdp'], 
    mode='lines+markers', 
    marker=dict(color=dark[0]), 
    line=dict(color=dark[0]),
    name='GDP',
    text=USSR_dat2_avg['year'], 
    hovertemplate='%{text}'+'<br>GDP: %{y:1f}',
    yaxis='y2'
    )
)
# Add text to the Rectangle
fig.add_trace(
    go.Scatter(
        x=[1990],
        y=[9.5],
        showlegend=False,
        hoverinfo='skip',
        mode='text',
        text=['Year 91-95'],
    )
)
# Add Rectangle 
fig.add_shape(
    go.layout.Shape(
        type='rect',
        x0=1991,
        y0=2,
        x1=1995,
        y1=9,
        line=dict(
            color='rgba(255, 255, 255, 0.5)',  
            width=1, dash='dot'
        )
    )
)
fig.update_shapes(dict(xref='x', yref='y'))
fig.update_layout(
    title_text='Average Suicide Rate and GDP in USSR Cohort 2:\
    <br>Armenia, Azerbaijan, Georgia, Kyrgyz Repulic, \
    <br>Moldova, Tajikistan, Turkmenistan, Uzbekistan',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='GDP', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=11, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)
#%%
'''
# Plot 9b - USSR2
init_notebook_mode(connected=True)
YGB9=cl.scales['9']['seq']['YlGnBu']
YOR9=cl.scales['9']['seq']['YlOrRd']
USSR2A_trace=[]
USSR2B_trace=[]
i=9
for country in USSR2:
    indat=USSR_dat2[USSR_dat2['country']==country]
    i=i-1
    USSR2A_trace.append(go.Scatter(
        x=indat['year'],
        y=indat['SR'],
        mode='lines+markers',
        marker=dict(color=YGB9[i]),
        line=dict(color=YGB9[i]),
        #legendgroup='USSR1SR',
        text=indat['country_yr'],
        name='SR-'+country,
        hovertemplate='%{text}'+'<br>SR: %{y:1f}'
            ),
        )
    USSR2B_trace.append(go.Scatter(
        x=indat['year'],
        y=indat['gdp'],
        mode='lines+markers',
        marker=dict(color=YOR9[i]),
        line=dict(color=YOR9[i]),
        #legendgroup='USSR1GDP',
        text=indat['country_yr'],
        name='GDP-'+country,
        hovertemplate='%{text}'+'<br>GDP: %{y:1f}',
        yaxis='y2'
            ),
        )
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_traces(USSR2A_trace)
fig.add_traces(USSR2B_trace)

fig.update_layout(
    title_text='Suicide and GDP in USSR Cohort 2',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='GDP', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=12, 
              color='rgba(255, 255, 255, 0.5)')
)
del indat, i
fig
#py.iplot(fig)
'''
#%%
# Plot 9c Zoom in Year 91-95 in USSR countries
#init_notebook_mode(connected=True)
USSR1_trace=[]
USSR2_trace=[]
blues9=cl.scales['9']['seq']['Blues']
oranges9=cl.scales['9']['seq']['Oranges']
for country in USSR1:
    indat=USSR_dat1[USSR_dat1['country']==country]
    indat=indat[indat['year'].isin([1991,1992,1993,1994,1995])]
    USSR1_trace.append(go.Scatter(
        x=indat['year'],
        y=indat['SR'],
        mode='lines+markers',
        marker=dict(color=blues9[6]),
        line=dict(color=blues9[6]),
        legendgroup='USSR1',
        text=indat['year'],
        name=country,
        hovertemplate='%{text}'+'<br>SR: %{y:1f}'
            ),
        )
for country in USSR2:
    indat=USSR_dat2[USSR_dat2['country']==country]
    indat=indat[indat['year'].isin([1991,1992,1993,1994,1995])]
    USSR2_trace.append(go.Scatter(
        x=indat['year'],
        y=indat['SR'],
        mode='lines+markers',
        marker=dict(color=oranges9[6]),
        line=dict(color=oranges9[6]),
        legendgroup='USSR2',
        text=indat['year'],
        name=country,
        hovertemplate='%{text}'+'<br>SR: %{y:1f}'
            ),
        )
fig=go.Figure(USSR1_trace)
fig.add_traces(USSR2_trace)

fig.update_layout(
    title_text=' ',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(zeroline = False, title='Suicide Count per 100k', showgrid=False),
    font=dict(family='Raleway', size=12, 
              color='rgba(255, 255, 255, 0.5)')
)
del indat
#fig
py.iplot(fig)


# %%
# Plot 10 - USSR Correlations
#init_notebook_mode(connected=True)
blues9=cl.scales['9']['seq']['Blues']
oranges9=cl.scales['9']['seq']['Oranges']
fig=go.Figure(go.Scatter(
    x=USSR1_corr['gdp'], 
    y=['USSR','USSR','USSR','USSR','USSR','USSR','USSR'], 
    mode='markers', 
    marker=dict(color=blues9[6], size=abs(40*USSR1_corr['gdp'])),
    name='USSR Cohort1',
    text=USSR1_corr['country'],
    hovertemplate='%{text}'+'<br>%{x}',
    )
)
fig.add_trace(go.Scatter(
    x=USSR2_corr['gdp'], 
    y=['USSR','USSR','USSR','USSR','USSR','USSR','USSR','USSR'], 
    mode='markers', 
    marker=dict(color=oranges9[6], size=abs(40*USSR2_corr['gdp'])),
    name='USSR Cohort2',
    text=USSR2_corr['country'],
    hovertemplate='%{text}'+'<br>%{x}',
    )
)
fig.update_layout(
    title_text='Correlation between SR and GDP',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis = dict(zeroline = False, 
                title='Correlation Coefficient',
                gridcolor='rgba(255, 255, 255, 0.5)',
                 ), 
    yaxis=dict(title='', showgrid=False),
    font=dict(family='Raleway', size=12, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)
# %%
# Plot 11 Japan
#init_notebook_mode(connected=True)
fig=go.Figure(go.Scatter(
    x=Japan['year'], 
    y=Japan['SR'], 
    mode='lines+markers', 
    marker=dict(color=SR_blues[9]), 
    line=dict(color=SR_blues[9]),
    name='SR',
    text=Japan['year'],
    hovertemplate='%{text}'+'<br>SR: %{y:1f}',
        )
    )
fig.add_trace(go.Scatter(
    x=Japan['year'], 
    y=Japan['Unemployment'], 
    mode='lines+markers', 
    marker=dict(color=dark[2]), 
    line=dict(color=dark[2]),
    name='Unemployment',
    text=Japan['year'], 
    hovertemplate='%{text}'+'<br>Unemployment: %{y:1f}%',
    yaxis='y2'
    )
)
# Add text to the Rectangle
fig.add_trace(
    go.Scatter(
        x=[1990, 1994],
        y=[15.5, 24],
        showlegend=False,
        hoverinfo='skip',
        mode='text',
        text=['Year 91-92','Year 97-98'],
    )
)
# Add Rectangle 
fig.add_shape(
    go.layout.Shape(
        type='rect',
        x0=1991,
        y0=16,
        x1=1992,
        y1=17,
        line=dict(
            color='rgba(255, 255, 255, 0.5)', 
            width=1, dash='dot'
        )
    )
)
fig.add_shape(
    go.layout.Shape(
        type='rect',
        x0=1997,
        y0=18.5,
        x1=1998,
        y1=25.5,
        line=dict(
            color='rgba(255, 255, 255, 0.5)', 
            width=1, dash='dot'
        )
    )
)
fig.update_shapes(dict(xref='x', yref='y'))
fig.update_layout(
    title_text='Suicide Rate and Unemployment Rate in Japan',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='Unemployment', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=12, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)

# %%
# Plot 12 Hong Kong
#init_notebook_mode(connected=True)
fig=go.Figure(go.Scatter(
    x=Hongkong['year'], 
    y=Hongkong['SR'], 
    mode='lines+markers', 
    marker=dict(color=SR_blues[9]), 
    line=dict(color=SR_blues[9]),
    name='SR',
    text=Hongkong['year'],
    hovertemplate='%{text}'+'<br>SR: %{y:1f}',
        )
    )
fig.add_trace(go.Scatter(
    x=Hongkong['year'], 
    y=Hongkong['Unemployment'], 
    mode='lines+markers', 
    marker=dict(color=dark[2]), 
    line=dict(color=dark[2]),
    name='Unemployment',
    text=Hongkong['year'], 
    hovertemplate='%{text}'+'<br>Unemployment: %{y:1f}%',
    yaxis='y2'
    )
)
# Add text to the Rectangle
fig.add_trace(
    go.Scatter(
        x=[1994],
        y=[14.5],
        showlegend=False,
        hoverinfo='skip',
        mode='text',
        text=['Year 97-98'],
    )
)
# Add Rectangle 
fig.add_shape(
    go.layout.Shape(
        type='rect',
        x0=1997,
        y0=9.5,
        x1=1999,
        y1=14,
        line=dict(
            color='rgba(255, 255, 255, 0.5)', 
            width=1, dash='dot'
        )
    )
)
fig.update_shapes(dict(xref='x', yref='y'))
fig.update_layout(
    title_text='Suicide Rate and Unemployment Rate in Hong Kong',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='Unemployment', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=12, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)

# %%
# Plot 13 Korea
#init_notebook_mode(connected=True)
fig=go.Figure(go.Scatter(
    x=Korea['year'], 
    y=Korea['SR'], 
    mode='lines+markers', 
    marker=dict(color=SR_blues[9]), 
    line=dict(color=SR_blues[9]),
    name='SR',
    text=Korea['year'],
    hovertemplate='%{text}'+',%{y:1f}',
        )
    )
fig.add_trace(go.Scatter(
    x=Korea['year'], 
    y=Korea['Unemployment'], 
    mode='lines+markers', 
    marker=dict(color=dark[2]), 
    line=dict(color=dark[2]),
    name='Unemployment',
    text=Korea['year'], 
    hovertemplate='%{text}'+',%{y:1f}%',
    yaxis='y2'
    )
)
fig.update_layout(
    title_text='South Korea',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='Unemployment', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=11, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)

# %%
# Plot 14 Thailand
#init_notebook_mode(connected=True)
fig=go.Figure(go.Scatter(
    x=Thailand['year'], 
    y=Thailand['SR'], 
    mode='lines+markers', 
    marker=dict(color=SR_blues[9]), 
    line=dict(color=SR_blues[9]),
    name='SR',
    text=Thailand['year'],
    hovertemplate='%{text}'+',%{y:1f}',
        )
    )
fig.add_trace(go.Scatter(
    x=Thailand['year'], 
    y=Thailand['Unemployment'], 
    mode='lines+markers', 
    marker=dict(color=dark[2]), 
    line=dict(color=dark[2]),
    name='Unemployment',
    text=Thailand['year'], 
    hovertemplate='%{text}'+',%{y:1f}%',
    yaxis='y2'
    )
)
fig.update_layout(
    title_text='Thailand',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='Unemployment', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=11, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)
# %%
# Plot 15 Malaysia
#init_notebook_mode(connected=True)
fig=go.Figure(go.Scatter(
    x=Malaysia['year'], 
    y=Malaysia['SR'], 
    mode='lines+markers', 
    marker=dict(color=SR_blues[9]), 
    line=dict(color=SR_blues[9]),
    name='SR',
    text=Malaysia['year'],
    hovertemplate='%{text}'+',%{y:1f}',
        )
    )
fig.add_trace(go.Scatter(
    x=Malaysia['year'], 
    y=Malaysia['Unemployment'], 
    mode='lines+markers', 
    marker=dict(color=dark[2]), 
    line=dict(color=dark[2]),
    name='Unemployment',
    text=Malaysia['year'], 
    hovertemplate='%{text}'+',%{y:1f}%',
    yaxis='y2'
    )
)
fig.update_layout(
    title_text='Malaysia',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='Unemployment', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=11, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)

# %%
# Plot 16 Philippines
#init_notebook_mode(connected=True)
fig=go.Figure(go.Scatter(
    x=Philippines['year'], 
    y=Philippines['SR'], 
    mode='lines+markers', 
    marker=dict(color=SR_blues[9]), 
    line=dict(color=SR_blues[9]),
    name='SR',
    text=Philippines['year'],
    hovertemplate='%{text}'+',%{y:1f}',
        )
    )
fig.add_trace(go.Scatter(
    x=Philippines['year'], 
    y=Philippines['Unemployment'], 
    mode='lines+markers', 
    marker=dict(color=dark[2]), 
    line=dict(color=dark[2]),
    name='Unemployment',
    text=Philippines['year'], 
    hovertemplate='%{text}'+',%{y:1f}%',
    yaxis='y2'
    )
)
fig.update_layout(
    title_text='Philippines',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    xaxis = dict(zeroline = False, title='Year', showgrid=False), 
    yaxis=dict(title='Suicide Count per 100k', showgrid=False),
    yaxis2=dict(title='Unemployment', overlaying='y', side='right', showgrid=False),
    font=dict(family='Raleway', size=11, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)
#%% 
'''
#Plot not used: Correlation of SR and Unemployment in Asian countries 
init_notebook_mode(connected=True)
Blues9=cl.scales['9']['seq']['Blues']
Oranges9=cl.scales['9']['seq']['Oranges']
fig=go.Figure(go.Scatter(
    x=Asia_corr1['unemployment'], 
    y=[' ',' '], 
    mode='markers', 
    marker=dict(color=Blues9[6], size=abs(40*Asia_corr1['unemployment'])),
    name='Group1',
    text=Asia_corr1['country'],
    hovertemplate='%{text}'+'<br>%{x}',
    )
)
fig.add_trace(
    go.Scatter(
    x=Asia_corr2['unemployment'], 
    y=[' ',' ',' ',' '], 
    mode='markers', 
    marker=dict(color=Oranges9[6], size=abs(40*Asia_corr2['unemployment'])),
    name='Group2',
    text=Asia_corr2['country'],
    hovertemplate='%{text}'+'<br>%{x}',
    )
)
fig.update_layout(
    title_text='Correlation between SR and Unemployment',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis = dict(zeroline = False, title='Correlation Coefficient'), 
    yaxis=dict(title='', showgrid=False),
    font=dict(family='Raleway', size=12, 
              color='rgba(255, 255, 255, 0.5)')
)
fig
#py.iplot(fig)
'''
# %%
# Plot 17 - Correlations
#dark=cl.scales['4']['qual']['Dark2']
#init_notebook_mode(connected=True)
fig=go.Figure(go.Scatter(
    x=corr_gini['gini'], 
    y=['Gini Coefficient']*15, 
    mode='markers', 
    marker=dict(color=dark[3], size=abs(40*corr_gini['gini'])),
    name='Gini Index',
    text=corr_gini['country'],
    hovertemplate='%{text}'+'<br>%{x}',
    )
)

fig.add_trace(go.Scatter(
    x=corr_cpi['cpi'], 
    y=['Consumer Price Index']*42, 
    mode='markers', 
    marker=dict(color=dark[1], size=abs(40*corr_cpi['cpi'])),
    name='Consumer Price Index',
    text=corr_cpi['country'],
    hovertemplate='%{text}'+'<br>%{x}',
    )
)

fig.add_trace(go.Scatter(
    x=corr_uem['unemployment'], 
    y=['Unemployment']*16, 
    mode='markers', 
    marker=dict(color=dark[2], size=abs(40*corr_uem['unemployment'])),
    name='Unemployment',
    text=corr_uem['country'],
    hovertemplate='%{text}'+'<br>%{x}',
    )
)

fig.add_trace(go.Scatter(
    x=corr_gdp['gdp'], 
    y=['GDP']*43, 
    mode='markers', 
    marker=dict(color=dark[0], size=abs(40*corr_gdp['gdp'])),
    name='GDP',
    text=corr_gdp['country'],
    hovertemplate='%{text}'+'<br>%{x}',
    )
)

fig.update_layout(
    title_text=' ',
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis = dict(zeroline = False, title='Correlation Coefficient'), 
    yaxis=dict(title='', showgrid=False),
    showlegend=False,
    font=dict(family='Raleway', size=13, 
              color='rgba(255, 255, 255, 0.5)')
)
#fig
py.iplot(fig)

# %%
