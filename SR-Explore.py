###### Project Name: SuicideRates
###### Program Name: SR-Explore.py
##### Purpose: To expore the suicide rates data 
##### Date Created: August 9th 2019

#%%
import plotly.plotly as py
import plotly.graph_objs as go
#%%[markdown]
#### Question 1. How did the suicide rate change across time on a global scale
# Sum up suicide count and population
SR_globe=master.groupby(['year'])[['suicides_no','population']].sum(skipna=True).reset_index()
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
layout = dict(title = 'Suicide Rates from 1985 to 2015',
              yaxis = dict(zeroline = False,
                    title='Suicide Count per 100k',
                ),
              xaxis = dict(zeroline = False,
                    title='Year',
              )
             )
#%% Plot the time series for aggregated global data
fig=go.Figure()
#fig.add_trace(trace_globe)
fig = go.Figure(data=[trace_globe], layout=layout)
py.iplot(fig)

#%%[markdown]
#### Question 2. Which region has the highest suicide rate in the world?
# Melt the data down by region
SR_region=master.groupby(['region','year'])[['suicides_no','population']].sum(skipna=True).reset_index()
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
fig=go.Figure()
fig = go.Figure(data=reg_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)
# There is a big jump in global suicide rates between 1989 and 1995. 
# The regional plot above seems to suggest the hike is related to European countires. 
# Now we plot the regional plots seperated against the world data

#%%[markdown]
#### Melt the data down by country
SR_country=master.groupby(['country','year'])[['suicides_no','population']].sum(skipna=True).reset_index()
SR_country['suicides/100kpop']=SR_country['suicides_no']/(SR_country['population']/100000)
#SR_country['country'].value_counts().sort_index()
#len(set(master['country']))
# Total number of country: 101
#%%[markdown]
# Create a country to region correspondence 
country2region=master[['country','iso3c','region','region2','region_id']]
country2region=country2region.drop_duplicates()
country2region['region'].value_counts().sort_index()
#%%[markdown]
# Merge the region data back into SR_country
SR_country=pd.merge(SR_country, country2region, how='left', left_on='country', right_on='country')
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
fig = go.Figure(data=ECS_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)
#%%[markdown]
# We see a few countries (Latvia, Lithuania) tend to stay on the top range of the chart. 
# Let's take a look a the top 5 countries by year and then tabulate the counts.
ESC_top5=dict() #Record the rank of the top 5 countries by year
ESC_top5_ctr=dict() #Tabulate the counts for each country
SR_ESC=SR_country[SR_country['region_id']=='ECS']
for year in range(1986,2017):
    ESC_top5[year]=list(SR_ESC[SR_ESC['year']==year][['country', 'suicides/100kpop']].sort_values(by=['suicides/100kpop'],ascending=False).head(5)['country'])
    for country in ESC_top5[year]:
        if country in ESC_top5_ctr.keys():
            ESC_top5_ctr[country]=ESC_top5_ctr[country]+1
        else:
            ESC_top5_ctr[country]=1
#%%[markdown]
# Countries that make it to the top 5 list across time include: Russia, Lithuania, Hungary, Belarus, Kazakhstan, Latvia
print(sorted(ESC_top5_ctr.items(), key=lambda kv: kv[1]))
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
fig = go.Figure(data=LCN_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)

#%% [markdown]
# Generates country level plots for East Asia
EAS_ctr=country2region[country2region['region_id']=='EAS'][['country']]
EAS_ctr=list(EAS_ctr['country'])
EAS_ctr_trace=[]
for country in EAS_ctr:
    EAS_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
fig = go.Figure(data=EAS_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)

#%% [markdown]
# Generates country level plots for Middle East
MEA_ctr=country2region[country2region['region_id']=='MEA'][['country']]
MEA_ctr=list(MEA_ctr['country'])
MEA_ctr_trace=[]
for country in MEA_ctr:
    MEA_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
fig = go.Figure(data=MEA_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)

#%% [markdown]
# Generates country level plots for Sub-Saharan Africa
SSF_ctr=country2region[country2region['region_id']=='SSF'][['country']]
SSF_ctr=list(SSF_ctr['country'])
SSF_ctr_trace=[]
for country in SSF_ctr:
    SSF_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
fig = go.Figure(data=SSF_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)

#%% [markdown]
# Generates country level plots for North America
NAC_ctr=country2region[country2region['region_id']=='NAC'][['country']]
NAC_ctr=list(NAC_ctr['country'])
NAC_ctr_trace=[]
for country in NAC_ctr:
    NAC_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
fig = go.Figure(data=NAC_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)

#%% [markdown]
# Generates country level plots for North America
SAS_ctr=country2region[country2region['region_id']=='SAS'][['country']]
SAS_ctr=list(SAS_ctr['country'])
SAS_ctr_trace=[]
for country in SAS_ctr:
    SAS_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
fig = go.Figure(data=SAS_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)


#%%[markdown]
# Now combine the country level plots into one plot
All_ctr=list(country2region['country'])
All_ctr_trace=[]
for country in All_ctr:
    All_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country[SR_country['country']==country]['year']))
fig = go.Figure(data=All_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
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

#%%
