###### Project Name: SuicideRates
###### Program Name: SR-Explore.py
##### Purpose: To expore the suicide rates data 
##### Date Created: August 27th 2019

#%%
import plotly.plotly as py
import plotly.graph_objs as go
import colorlover as cl
from IPython.display import HTML
import scipy
import math

#%%[markdown]
#### Question 1. How did the suicide rate change across time on a global scale
# Sum up suicide count and population
SR_globe=master[master['suicides_no']>=0]
SR_globe=SR_globe.groupby(['year'])[['suicides_no','population']].sum(skipna=True).reset_index()
SR_globe['suicides/100kpop']=SR_globe['suicides_no']/(SR_globe['population']/100000)
#%%[markdown]
# Draw a simple time series based on global suicide rates
trace_globe=go.Scatter(
    x = SR_globe['year'],
    y = SR_globe['suicides/100kpop'],
    name = 'World',
    mode = 'lines+markers',
    text = SR_globe['year'],
    marker = dict(
        size = 10,
        color='#705772'
    )
)
layout = dict(title = 'Suicide Rates from 1979 to 2016',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Year',
              )
             )
#%% Plot the time series for aggregated global data
#fig=go.Figure()
#fig.add_trace(trace_globe)
#fig = go.Figure(data=[trace_globe], layout=layout)
#py.iplot(fig)

#%%[markdown]
#### Question 2. Which region has the highest suicide rate in the world?
# Melt the data down by region
SR_region=master[master['suicides_no']>=0]
SR_region=SR_region.groupby(['region','year'])[['suicides_no','population']].sum(skipna=True).reset_index()
SR_region['suicides/100kpop']=SR_region['suicides_no']/(SR_region['population']/100000)
#SR_region['region'].value_counts().sort_index()

#%%[markdown]
# Plot SR by region
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
#%% 
# Making traces for all regions
reg_trace=[]
for region in list(set(regions.values())):
    reg_trace.append(make_line_trace(SR_region[SR_region['region']==region],x='year',y='suicides/100kpop',\
        name=region,mode='lines+markers',label=SR_region[SR_region['region']==region]['year']))

#%% [markdown]
# Making the regional plot and then add the world trace on
#fig=go.Figure()
#fig = go.Figure(data=reg_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)
# There is a big jump in global suicide rates between 1989 and 1995. 
# The regional plot above seems to suggest the hike is related to European countires. 
# Now we plot the regional plots seperated against the world data

#%%[markdown]
#### Create SR data by country
SR_country=master[master['suicides_no']>=0]
SR_country=SR_country.groupby(['country','year'])[['suicides_no','population']].sum(skipna=True).reset_index()
SR_country['suicides/100kpop']=SR_country['suicides_no']/(SR_country['population']/100000)
#SR_country['country'].value_counts().sort_index()
#len(set(master['country']))
# Total number of country: 128
# Create a country to region correspondence 
country2region=master[['country','iso3c','region','region_id']]
country2region=country2region.drop_duplicates()
#country2region['region'].value_counts().sort_index()
# Merge the region data back into SR_country
SR_country=pd.merge(SR_country, country2region, how='left', left_on='country', right_on='country')
# Add in economic factors 
SR_country=pd.merge(SR_country,master[['country','year','income','income_id','gdp','loggdp','gdp2','loggdp2','UEM_TOTL','LifeLadder','gini']], how="left",on=['country','year'])
SR_country['country_year']=SR_country['country']+SR_country['year'].map(str)

#%% [markdown]
# To further investigate suicide rates in Europe, we create a list of European countries
ECS_ctr=country2region[country2region['region_id']=='ECS'][['country']]
ECS_ctr=list(ECS_ctr['country'])
#%% [markdown]
# Next, we create a list of traces of European and Central Asian countries
ECS_ctr_trace=[]
for country in ECS_ctr:
    ECS_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
#%%
#fig = go.Figure(data=ECS_ctr_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)
#%%[markdown]
# We see a few countries (Latvia, Lithuania) tend to stay on the top range of the chart. 
# Let's take a look a the top 5 countries by year and then tabulate the counts.
ESC_top5=dict() #Record the rank of the top 5 countries by year
ESC_top5_ctr=dict() #Tabulate the counts for each country
SR_ESC=SR_country[SR_country['region_id']=='ECS']
for year in range(1979,2017):
    ESC_top5[year]=list(SR_ESC[SR_ESC['year']==year][['country', 'suicides/100kpop']].sort_values(by=['suicides/100kpop'],ascending=False).head(5)['country'])
    for country in ESC_top5[year]:
        if country in ESC_top5_ctr.keys():
            ESC_top5_ctr[country]=ESC_top5_ctr[country]+1
        else:
            ESC_top5_ctr[country]=1
#%%[markdown]
# Countries that make it to the top 5 list across time include: Russia, Lithuania, Hungary, Belarus, Kazakhstan, Latvia
print(sorted(ESC_top5_ctr.items(), key=lambda kv: kv[1], reverse=True))
#%%[markdown]
#### Finno Ugrian Suicide Hypothesis 
# https://en.wikipedia.org/wiki/Finno-Ugrian_suicide_hypothesis

#%% [markdown]
# Generates country level plots for Latin America
LCN_ctr=country2region[country2region['region_id']=='LCN'][['country']]
LCN_ctr=list(LCN_ctr['country'])
LCN_ctr_trace=[]
for country in LCN_ctr:
    LCN_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
#fig = go.Figure(data=LCN_ctr_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)

#%% [markdown]
# Generates country level plots for East Asia
EAS_ctr=country2region[country2region['region_id']=='EAS'][['country']]
EAS_ctr=list(EAS_ctr['country'])
EAS_ctr_trace=[]
for country in EAS_ctr:
    EAS_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
#fig = go.Figure(data=EAS_ctr_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)

#%% [markdown]
# Generates country level plots for Middle East
MEA_ctr=country2region[country2region['region_id']=='MEA'][['country']]
MEA_ctr=list(MEA_ctr['country'])
MEA_ctr_trace=[]
for country in MEA_ctr:
    MEA_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
#fig = go.Figure(data=MEA_ctr_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)

#%% [markdown]
# Generates country level plots for Sub-Saharan Africa
SSF_ctr=country2region[country2region['region_id']=='SSF'][['country']]
SSF_ctr=list(SSF_ctr['country'])
SSF_ctr_trace=[]
for country in SSF_ctr:
    SSF_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
#fig = go.Figure(data=SSF_ctr_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)

#%% [markdown]
# Generates country level plots for North America
NAC_ctr=country2region[country2region['region_id']=='NAC'][['country']]
NAC_ctr=list(NAC_ctr['country'])
NAC_ctr_trace=[]
for country in NAC_ctr:
    NAC_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
#fig = go.Figure(data=NAC_ctr_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)

#%% [markdown]
# Generates country level plots for South Asia
SAS_ctr=country2region[country2region['region_id']=='SAS'][['country']]
SAS_ctr=list(SAS_ctr['country'])
SAS_ctr_trace=[]
for country in SAS_ctr:
    SAS_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
#fig = go.Figure(data=SAS_ctr_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)

#%%[markdown]
# Now combine the country level plots into one plot
# East Asia Financial Crisis in 1997
# HK: big dip in 1997 and jump in 2004 
All_ctr=list(country2region['country'])
All_ctr_trace=[]
for country in All_ctr:
    All_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
#fig = go.Figure(data=All_ctr_trace, layout=layout)
#fig.add_trace(trace_globe)
#py.iplot(fig)

#%%[markdown]
# Create a time series for GDP per capita, PPP (constant 2011 international $)
All_ctr=list(country2region['country'])
All_ctr_trace=[]
for country in All_ctr:
    All_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='gdp',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
layout = dict(title = 'GDP per capita, PPP (Constant 2011 international $)',
              yaxis = dict(zeroline = False,
                    title='GDP per capita',
                ),
              xaxis = dict(zeroline = False,
                    title='Year',
              )
             )
fig = go.Figure(data=All_ctr_trace, layout=layout)
py.iplot(fig)

#%%[markdown]
# Create a time series for Unemployment Rate
All_ctr=list(country2region['country'])
All_ctr_trace=[]
for country in All_ctr:
    All_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='UEM_TOTL',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
layout = dict(title = 'Unemployment, total (% of total labor force) (national estimate)',
              yaxis = dict(zeroline = False,
                    title='Unemployment Rate',
                ),
              xaxis = dict(zeroline = False,
                    title='Year',
              )
             )
fig = go.Figure(data=All_ctr_trace, layout=layout)
py.iplot(fig)

#%%[markdown]
# Create a time series for Gini
All_ctr=list(country2region['country'])
All_ctr_trace=[]
for country in All_ctr:
    All_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='gini',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
layout = dict(title = 'Gini Index',
              yaxis = dict(zeroline = False,
                    title='Gini',
                ),
              xaxis = dict(zeroline = False,
                    title='Year',
              )
             )
fig = go.Figure(data=All_ctr_trace, layout=layout)
py.iplot(fig)
#%% [markdown]
# Now that we have a plot for all countries, let's find the countries with the highest SR
top5=dict() #Record the rank of the top 5 countries by year
top5_ctr=dict() #Tabulate the counts for each country
for year in range(1986,2017):
    top5[year]=list(SR_country[SR_country['year']==year][['country', 'suicides/100kpop']].sort_values(by=['suicides/100kpop'],ascending=False).head(5)['country'])
    for country in top5[year]:
        if country in top5_ctr.keys():
            top5_ctr[country]=top5_ctr[country]+1
        else:
            top5_ctr[country]=1
#%%[markdown]
# Countries that make it to the top 5 list across time include: Russia, Lithuania, Hungary, Belarus, Kazakhstan, Latvia
print(sorted(top5_ctr.items(), key=lambda kv: kv[1], reverse=True))

#%%
top5_ctr_df=pd.DataFrame.from_dict(top5_ctr, orient='index', columns=['count'])
top5_ctr_df=top5_ctr_df.sort_values(by=['count'])
#%%[markdown]
# Making a bar chart of the top 5 country list
fig=go.Figure()
fig.add_trace(go.Bar(
    x=top5_ctr_df['count'],
    y=list(top5_ctr_df.index),
    orientation='h'
))
py.iplot(fig)
#%%
SR_GDP=go.Scatter(x=SR_country['gdp'],y=SR_country['suicides/100kpop'],\
        mode='markers', text=SR_country['country'])
layout = dict(title = 'Suicide Rates vs. GDP per capita ($)',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='GDP per capita ($)',
              )
             )
#fig = go.Figure(data=[SR_GDP], layout=layout)
#py.iplot(fig)
#%% [markdown]
#### Unemployment Rates
SR_UEM=go.Scatter(x=SR_country['UEM_TOTL'],y=SR_country['suicides/100kpop'],\
        mode='markers', text=SR_country['country'])
layout = dict(title = 'Suicide Rates vs. Unemployment',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Unemployment Rate',
              )
             )
#fig = go.Figure(data=[SR_UEM], layout=layout)
#py.iplot(fig)

#%%[markdown]
# Data seems to suggest that the higher gini is, the lower the suicide rate is. 
SR_gini=go.Scatter(x=SR_country['gini'],y=SR_country['suicides/100kpop'],\
        mode='markers', text=SR_country['country'])
layout = dict(title = 'Suicide Rates vs. Gini',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Gini',
              )
             )
#fig = go.Figure(data=[SR_gini], layout=layout)
#py.iplot(fig)

#%%[markdown]
#### What if we treat each country each year as a unique data?
# Every country is associated with a Gini data point, would we see the above trend when we mix all data from all years and 
# simply treat each data point a hypothetical entity (of course, ignoring the correlation each couountry has to their previous data)

#%%
SR_gini=go.Scatter(x=SR_country['gini'],y=SR_country['suicides/100kpop'],\
        mode='markers', text=SR_country['country_year'])
layout = dict(title = 'Suicide Rates vs. Gini',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Gini',
              )
             )
fig = go.Figure(data=[SR_gini], layout=layout)
py.iplot(fig)

#%%
#import matplotlib.pyplot as plt 
#plt.scatter(SR_country['LifeLadder'], SR_country['suicides/100kpop'],c=SR_country['suicides/100kpop'])
#plt.show()

#%%[markdown]
# Create an interactive plot to show SR against GDP of selected countries across all years
# More suicide as GDP grows: Australia; Brazil; Dominican Republic; Guatemala; 
# Guyana; Malta(?);Mexico; Moroco; Netherland; Paraguay; South Africa; United States; Uruguay; 
# Less suicide as GDP grows: Belaruse; Belgium; Chile; France; Hungary; Isreal; Japan; Kazakhstan; 
# Lithuania; Nicaragua; Panama; Poland; Puerto Rico; Romania; Russia; Serbia; Spain; Venezuala;
All_ctr=list(country2region['country'])
All_ctr_trace2=[]
for country in All_ctr:
    All_ctr_trace2.append(make_line_trace(SR_country[SR_country['country']==country],x='gdp',y='suicides/100kpop',\
        name=country,mode='markers',label=SR_country[SR_country['country']==country]['country_year']))
layout = dict(title = 'Suicide Rates vs. GDP (all years)',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='GDP',
              )
             )
#fig = go.Figure(data=All_ctr_trace2, layout=layout)
#py.iplot(fig)

#%%[markdown]
# How about group the countries by income level
# High-income groups looks quite simiar to all income groups combined
# Upper-middle income and Lower-middle income groups show no obvious trend
All_income=['High-income','Upper-middle income','Lower-middle income','Low-income']
All_ctr_trace2a=[]
for income_level in All_income:
    All_ctr_trace2a.append(make_line_trace(SR_country[SR_country['income']==income_level],x='gdp',y='suicides/100kpop',\
        name=income_level,mode='markers',label=SR_country[SR_country['income']==income_level]['country_year']))
layout = dict(title = 'Suicide Rates vs. GDP (all years)',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='GDP',
              )
             )
#fig = go.Figure(data=All_ctr_trace2a, layout=layout)
#py.iplot(fig)

#%%[markdown]
# How about group the countries by Region
# Europe and Central Asia looks very similar to High-income groups
All_region=['Europe and Central Asia','Sub-Saharan Africa','Latin America and the Caribbean','East Asia and Pacific','Middle East and North Africa','South Asia','North America']
All_ctr_trace2b=[]
for region in All_region:
    All_ctr_trace2b.append(make_line_trace(SR_country[SR_country['region']==region],x='gdp',y='suicides/100kpop',\
        name=region,mode='markers',label=SR_country[SR_country['region']==region]['country_year']))
layout = dict(title = 'Suicide Rates vs. GDP by Region',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='GDP',
              )
             )
#fig = go.Figure(data=All_ctr_trace2b, layout=layout)
#py.iplot(fig)

#%%[markdown]
# Create an interactive plot to show SR against Unemployment Rate of selected countries
# Across all years 
All_ctr=list(country2region['country'])
All_ctr_trace3=[]
for country in All_ctr:
    All_ctr_trace3.append(make_line_trace(SR_country[SR_country['country']==country],x='gdp',y='suicides/100kpop',\
        name=country,mode='markers',label=SR_country[SR_country['country']==country]['country_year']))
layout = dict(title = 'Suicide Rates vs. Unemployment (all years)',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Unemployment', 
              )
             )
#fig = go.Figure(data=All_ctr_trace3, layout=layout)
#py.iplot(fig)

#%%[markdown]
# Create year-on-year change for SR and GDP
SR_country_prev=SR_country[['country','year','gdp','suicides/100kpop','UEM_TOTL']]
SR_country_prev['year']=SR_country_prev['year']+1
SR_country_prev.columns=['country','year','gdp_prev','SR_prev','UEM_prev']
SR_country_prev=pd.merge(SR_country_prev, SR_country, how='left', left_on=['country','year'], right_on=['country','year'])
SR_country_prev=SR_country_prev.assign(gdpchg=SR_country_prev['gdp']-SR_country_prev['gdp_prev'])
SR_country_prev=SR_country_prev.assign(srchg=SR_country_prev['suicides/100kpop']-SR_country_prev['SR_prev'])
SR_country_prev=SR_country_prev.assign(uemchg=SR_country_prev['UEM_TOTL']-SR_country_prev['UEM_prev'])
SR_country_prev2=SR_country_prev[SR_country_prev['gdpchg']<0]
#%%
All_ctr=list(country2region['country'])
All_ctr_trace4=[]
for country in All_ctr:
    All_ctr_trace4.append(make_line_trace(SR_country_prev[SR_country_prev['country']==country],x='gdpchg',y='srchg',\
        name=country,mode='markers',label=SR_country_prev[SR_country_prev['country']==country]['country_year']))
layout = dict(title = 'Year-on-year Change in Suicide Rates vs. GDP',
              yaxis = dict(zeroline = False,
                    title='Change in Suicide Count per 100k from last year',
                ),
              xaxis = dict(zeroline = False,
                    title='Change in GDP from last year', 
              )
             )
#fig = go.Figure(data=All_ctr_trace4, layout=layout)
#py.iplot(fig)

#%% [markdown]
# Now let's zoom in to cases where GDP decreases
All_ctr_trace5=[]
for country in All_ctr:
    All_ctr_trace5.append(make_line_trace(SR_country_prev2[SR_country_prev2['country']==country],x='gdpchg',y='srchg',\
        name=country,mode='markers',label=SR_country_prev2[SR_country_prev2['country']==country]['country_year']))
layout = dict(title = 'Year-on-year Change in Suicide Rates vs. GDP [GDP Drop]',
              yaxis = dict(zeroline = False,
                    title='Change in Suicide Count per 100k from last year',
                ),
              xaxis = dict(zeroline = False,
                    title='Change in GDP from last year', 
              )
             )
#fig = go.Figure(data=All_ctr_trace5, layout=layout)
#py.iplot(fig)

#%%[markdown]
# Now let's add in Gini index to the plot
SR_country_prev3=SR_country_prev[(SR_country_prev['gini'].isnull()==0) & (SR_country_prev['gdpchg'].isnull()==0) & (SR_country_prev['srchg'].isnull()==0)]
#%%
All_ctr_trace6=[]
for country in All_ctr:
    tmp=SR_country_prev3[SR_country_prev3['country']==country]
    if len(tmp)>0:
        trace=go.Scatter(x=tmp['gdpchg'], y=tmp['srchg'], name=country, mode='markers', text=tmp['country_year'], marker=dict(size=tmp['gini_scaled']))
        All_ctr_trace6.append(trace)
del tmp
del trace
layout = dict(title = 'Year-on-year Change in SR vs. GDP with Gini',
              yaxis = dict(zeroline = False,
                    title='Change in Suicide Count per 100k from last year',
                ),
              xaxis = dict(zeroline = False,
                    title='Change in GDP from last year', 
              )
             )
fig = go.Figure(data=All_ctr_trace6, layout=layout)
py.iplot(fig)


#%% [markdown]
# Create some color scale for the following step
blues = cl.scales['9']['seq']['Blues']
#HTML( cl.to_html(bupu) )
col_num=[0.246, 0.295, 0.343, 0.392, 0.44, 0.489, 0.537, 0.586, 0.634]
blue_scales=[list(elem) for elem in list(zip(col_num, blues))]
del col_num

#%%[markdown]
# Using size alone for the Gini index is not helpful in detecting any trend in terms of whether Gini moderate the year-on-year chage
# Let's now try to use both color and size on the Gini index
All_ctr_trace7=[]
All_year=[2010,2011,2012,2013,2014,2015,2016]
for year in All_year:
    tmp=SR_country_prev3[SR_country_prev3['year']==year]
    if len(tmp)>0:
        trace=go.Scatter(x=tmp['gdpchg'], y=tmp['srchg'], name=year, mode='markers', text=tmp['country_year'], \
            marker=dict(size=tmp['gini'], color=tmp['gini'], colorscale=blue_scales))
        All_ctr_trace7.append(trace)
del tmp
del trace
#%%
layout = dict(title = 'Year-on-year Change in SR vs. GDP with Gini',
              yaxis = dict(zeroline = False,
                    title='Change in Suicide Count per 100k from last year',
                ),
              xaxis = dict(zeroline = False,
                    title='Change in GDP from last year', 
              )
             )
fig = go.Figure(data=All_ctr_trace7, layout=layout)
py.iplot(fig)

#%%[markdown]
# SR vs Happiness
SR_Happy=go.Scatter(x=SR_country['LifeLadder'],y=SR_country['suicides/100kpop'],\
        mode='markers', text=SR_country['country_year'])
layout = dict(title = 'Suicide Rates vs. Happiness Index',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Happiness',
              )
             )
fig = go.Figure(data=[SR_Happy], layout=layout)
py.iplot(fig)

#%%[markdown]
# SR vs Happiness moderated by Gini
tmp=SR_country[(SR_country['LifeLadder'].isnull()==0) & (SR_country['gini'].isnull()==0)]
#%%
SR_Happy=go.Scatter(x=tmp['LifeLadder'],y=tmp['suicides/100kpop'],\
        mode='markers', text=tmp['country_year'], \
        marker=dict(color=tmp['gini'], colorscale='Greys'))
layout = dict(title = 'Suicide Rates vs. Happiness Index with Gini',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Happiness',
              )
             )
fig = go.Figure(data=[SR_Happy], layout=layout)
py.iplot(fig)
del tmp

#%%[markdown]
# Gini vs Happiness: It appears that there is clear association between Gini and Happiness
Gini_Happy=go.Scatter(x=SR_country['LifeLadder'],y=SR_country['gini'],\
        mode='markers', text=SR_country['country_year'])
layout = dict(title = 'Gini Index vs. Happiness Index',
              yaxis = dict(zeroline = False,
                    title='Gini Index',
                ),
              xaxis = dict(zeroline = False,
                    title='Happiness',
              )
             )
fig = go.Figure(data=[Gini_Happy], layout=layout)
py.iplot(fig)

#%%[markdown]
# Now Let's run some correlations to quantify the associations of SR with GDP (and/or log GDP), Unemployment, Gini, Happiness

#%%[markdown]
# SR vs GDP: corr=0.050677
SR_country[(SR_country['suicides/100kpop'].isnull()==0) & (SR_country['gdp'].isnull()==0)][['suicides/100kpop','gdp']].corr()
#%%[markdown]
# SR vs GDP Log: corr=0.164734
SR_country[(SR_country['suicides/100kpop'].isnull()==0) & (SR_country['loggdp'].isnull()==0)][['suicides/100kpop','loggdp']].corr()
#%%[markdown]
# Year on year change in SR vs GDP: corr=-0.043162
SR_country_prev[(SR_country_prev['srchg'].isnull()==0) & (SR_country_prev['gdpchg'].isnull()==0)][['srchg','gdpchg']].corr()
#%%[markdown]
# SR vs Unemployment: corr=-0.030043
SR_country[(SR_country['suicides/100kpop'].isnull()==0) & (SR_country['UEM_TOTL'].isnull()==0)][['suicides/100kpop','UEM_TOTL']].corr()
#%%[markdown]
# SR vs Consumer Price Index: corr=-0.053825
#SR_country[(SR_country['SR'].isnull()==0) & (SR_country['cpi'].isnull()==0)][['SR','cpi']].corr()

#%%[markdown]
# SR vs Gini: corr=-0.489805
SR_country[(SR_country['suicides/100kpop'].isnull()==0) & (SR_country['gini'].isnull()==0)][['suicides/100kpop','gini']].corr()
#%%[markdown]
# SR vs Happiness: corr=0.045084
SR_country[(SR_country['suicides/100kpop'].isnull()==0) & (SR_country['LifeLadder'].isnull()==0)][['suicides/100kpop','LifeLadder']].corr()
#%%[markdown]
# Gini vs Happiness: corr=-0.120827
SR_country[(SR_country['gini'].isnull()==0) & (SR_country['LifeLadder'].isnull()==0)][['gini','LifeLadder']].corr()

#%%[markdown]
# Thought: Swap out the Gini data and use the World Bank Gini
gini_data=master[(master['gini'].isnull()==0) | (master['gini_whr'].isnull()==0)][['country','year','gini','gini_whr','suicides/100kpop']]
gini_data['SR']=gini_data['suicides/100kpop']
#gini_data['gini2']=gini_data['gini_whr']*100
#gini_data[gini_data['gini']!=gini_data['gini2']][['country','year','gini','gini2']]

#%%[markdown]
# Try to fit a linear regression model
from sklearn.linear_model import LinearRegression
gini_data2=gini_data[(gini_data['gini'].isnull()==0) & (gini_data['SR'].isnull()==0)]
x=pd.DataFrame(gini_data2['gini'])
y=pd.DataFrame(gini_data2['SR'])
model=LinearRegression()
model=model.fit(x, y)
print('Coefficient: ',model.coef_)
print('R-sq:', model.score(x,y))

import statsmodels.api as sm
x2=sm.add_constant(x)
model2=sm.OLS(y,x2)
fii=model2.fit()
print(fii.summary())

#%%[markdown]
# When comparing SR against GDP, gini, unemployment rates, we don't see a clear association 
# I wonder if there is a lag in SR? Meaning SR will not immediately increase after the economy plunge.
# Now what if we shift the SR data to reflect that lag? 
# For example, we examine 2016 SR in America against economy statistics in 2015.
SR_country_lag=SR_country[['country','year','suicides/100kpop']]
SR_country_lag['year']=SR_country_lag['year']-1
SR_country_lag=pd.merge(SR_country_lag, SR_country[['country','year','gdp','loggdp','UEM_TOTL','LifeLadder','gini']], \
        how='left', left_on=['country','year'], right_on=['country','year'])
#SR_country_lag[(SR_country_lag['gdp'].isnull()==0) & (SR_country_lag['suicides/100kpop'].isnull()==0)][['gdp','suicides/100kpop']].corr()
#SR_country_lag[(SR_country_lag['UEM_TOTL'].isnull()==0) & (SR_country_lag['suicides/100kpop'].isnull()==0)][['UEM_TOTL','suicides/100kpop']].corr()
#SR_country_lag[(SR_country_lag['gini'].isnull()==0) & (SR_country_lag['suicides/100kpop'].isnull()==0)][['gini','suicides/100kpop']].corr()

#%%
#plt.scatter(SR_country_lag['gini'], SR_country_lag['suicides/100kpop'],c=SR_country_lag['suicides/100kpop'])
#plt.show()
#%%[markdown]
# The correlation between GDP and SR seem to decrease as we increase the lags. 
# With no time lage: corr=0.050677
# With 1 year lag: corr=0.053547
# With 2 year lag: corr=0.048789
# With 3 year lag: corr=0.023181

#%%[markdown]
# The correlation between unemployment and SR seem to decrease as we increase the lags. 
# With no time lage: corr=-0.030043
# With 1 year lag: corr=-0.032545
# With 2 year lag: corr=-0.024164
# With 3 year lag: corr=-0.017208

#%%[markdown]
# The correlation between Gini and SR seem to hold at the same level regardless of the time lag
# With no time lage: corr=-0.489805
# With 1 year lag: corr=-0.483752
# With 2 year lag: corr=-0.488567
# With 3 year lag: corr=-0.494326

#%%[markdown]
# The two tiers of USSR
# Tier 1: Russia, Ukraine, Belarus, Lithuania, Latvia, Kazakstan, Estonia, 
# Tier 2: Armenia, Turkmenistan, Azerbaijian, Kyrgyzstan, Moldova, Tajikistan, Georgia, Uzbekistan
USSR=['Armenia', 'Azerbaijan', 'Belarus', 'Estonia', 'Georgia','Kazakhstan',\
    'Kyrgyz Republic', 'Latvia', 'Lithuania', 'Moldova', 'Russian Federation',\
    'Tajikistan', 'Turkmenistan', 'Ukraine', 'Uzbekistan']
USSR1=['Belarus', 'Estonia', 'Kazakhstan', 'Latvia', 'Lithuania', 'Russian Federation','Ukraine']
USSR2=['Armenia', 'Azerbaijan', 'Georgia', 'Kyrgyz Republic', 'Moldova', 'Tajikistan', 'Turkmenistan','Uzbekistan']
USSR_dat=SR_country[SR_country['country'].isin(USSR)]
USSR_dat1=SR_country[SR_country['country'].isin(USSR1)]
USSR_dat2=SR_country[SR_country['country'].isin(USSR2)]

#%%
USSR_dat[(USSR_dat['gdp'].isnull()==0) & (USSR_dat['suicides/100kpop'].isnull()==0)][['gdp','suicides/100kpop']].corr()
#%%
USSR_dat1[(USSR_dat1['gdp'].isnull()==0) & (USSR_dat1['suicides/100kpop'].isnull()==0)][['gdp','suicides/100kpop']].corr()
#%%
USSR_dat2[(USSR_dat2['gdp'].isnull()==0) & (USSR_dat2['suicides/100kpop'].isnull()==0)][['gdp','suicides/100kpop']].corr()


#%%[markdown]
#Zoom in on SR within the USSR countries
USSR_SR_trace=[]
for country in USSR:
    USSR_SR_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
layout = dict(title = 'Suicide Rates in USSR Countries',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Year',
              )
             )
fig = go.Figure(data=USSR_SR_trace, layout=layout)
py.iplot(fig)

#%%[markdown]
#Zoom in on SR within the USSR countries
USSR_GDP_trace=[]
for country in USSR:
    USSR_GDP_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='gdp',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
layout = dict(title = 'GDP in USSR Countries',
              yaxis = dict(zeroline = False,
                    title='GDP per capita, PPP (Constant 2011 international $)',
                ),
              xaxis = dict(zeroline = False,
                    title='Year',
              )
             )
fig = go.Figure(data=USSR_GDP_trace, layout=layout)
py.iplot(fig)

#%%[markdown]
# Create a time series of average GDP and SR within USSR cohort 1 vs cohort 2
USSR1_SR=USSR_dat1.groupby(['year'])['suicides/100kpop','gdp'].mean().reset_index()
USSR2_SR=USSR_dat2.groupby(['year'])['suicides/100kpop','gdp'].mean().reset_index()
USSR1_SR_trace=go.Scatter(
    x = USSR1_SR['year'],
    y = USSR1_SR['suicides/100kpop'],
    mode = 'lines+markers',
    name='Suicide Rates per 100k',
    text = USSR1_SR['year'],
    marker = dict(
        size = 10,
        color='#364156'
    )
)
USSR1_GDP_trace=go.Scatter(
    x = USSR1_SR['year'],
    y = USSR1_SR['gdp'],
    mode = 'lines+markers',
    name='GDP per capita, PPP (Constant 2011 international $)',
    yaxis='y2',
    text = USSR1_SR['year'],
    marker = dict(
        size = 10,
        color='#D66853'
    )
)
USSR2_SR_trace=go.Scatter(
    x = USSR2_SR['year'],
    y = USSR2_SR['suicides/100kpop'],
    mode = 'lines+markers',
    name='Suicide Rates per 100k',
    text = USSR2_SR['year'],
    marker = dict(
        size = 10,
        color='#364156'
    )
)
USSR2_GDP_trace=go.Scatter(
    x = USSR2_SR['year'],
    y = USSR2_SR['gdp'],
    mode = 'lines+markers',
    name='GDP per capita, PPP (Constant 2011 international $)',
    yaxis='y2',
    text = USSR2_SR['year'],
    marker = dict(
        size = 10,
        color='#D66853'
    )
)
#%%
layout=go.Layout(title = 'Suicide Rates and GDP in USSR Cohort 1',
              yaxis = dict(title='Suicide Count per 100k',side='left'
                ),
              yaxis2 = dict(title='GDP',overlaying='y', side='right'
                ),
              xaxis = dict(title='Year',
              )
             )          
fig=go.Figure(data=[USSR1_SR_trace, USSR1_GDP_trace], layout=layout)
py.iplot(fig)

#%%
layout=go.Layout(title = 'Suicide Rates and GDP in USSR Cohort 2',
              yaxis = dict(title='Suicide Count per 100k',side='left',zeroline = False,
                ),
              yaxis2 = dict(title='GDP',overlaying='y', side='right',zeroline = False,
                ),
              xaxis = dict(title='Year',
              )
             )          
fig=go.Figure(data=[USSR2_SR_trace, USSR2_GDP_trace], layout=layout)
py.iplot(fig)

#%%[markdown]
#### Asking a different question
# Instead of asking which one economic predictor best predict suiside rates for all countries, 
# how about asking for each country, which economic index associate with suicidal rates the strongest? 
def corrmat(country):
    tmp=SR_country[SR_country['country']==country]
    corr1=tmp[(tmp['gdp'].isnull()==0) & (tmp['suicides/100kpop'].isnull()==0)][['gdp','suicides/100kpop']].corr().iloc[0,1]
    corr2=tmp[(tmp['UEM_TOTL'].isnull()==0) & (tmp['suicides/100kpop'].isnull()==0)][['UEM_TOTL','suicides/100kpop']].corr().iloc[0,1]
    corr3=tmp[(tmp['gini'].isnull()==0) & (tmp['suicides/100kpop'].isnull()==0)][['gini','suicides/100kpop']].corr().iloc[0,1]
    #print(corr1, corr2, corr3)
    maxval=' '
    maxcorr=-2
    if (abs(corr1)==1):
        corr1=-2
    if (abs(corr2)==1):
        corr2=-2
    if (abs(corr3)==1):
        corr3=-2
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
            maxval='GINI'
    corr=[country, corr1, corr2, corr3, maxcorr, maxval]
    del tmp,corr1,corr2, corr3, maxval, maxcorr
    return(corr)
#corrmat('Cuba')
#%%
SR_corr_mat=[]
for country in list(country2region['country']):
    SR_corr_mat.append(corrmat(country))
SR_corr_mat=pd.DataFrame(SR_corr_mat, columns=['country','gdp','uem','gini', 'max', 'max_col'])
#%%
SR_country[(SR_country['suicides/100kpop'].isnull()==0) & (SR_country['gdp'].isnull()==0)][['suicides/100kpop','gdp']].corr().iloc[0,1]
#%%
SR_corr_mat[SR_corr_mat['country'].isin(USSR1)]
#%%
master[master['country']=='Hong Kong SAR, China'][['year','suicides/100kpop']]

#%%
SR_corr_mat[SR_corr_mat['country'].isin(['Malaysia', 'Philippines', 'Korea, Rep.', 'Singapore', 'Thailand'])]

#%%
SR_corr_mat[(SR_corr_mat['max']>0.5) & (SR_corr_mat['max']<1)]

#%%
SR_country[SR_country['country']=='Turks and Caicos Islands'][['year','gdp','UEM_TOTL','gini']]

#%%
#%%
