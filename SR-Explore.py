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
             
#%%
fig=go.Figure()
#fig.add_trace(trace_globe)
fig = go.Figure(data=[trace_globe], layout=layout)
py.iplot(fig)

#%%[markdown]
# Melt the data down by region
SR_region=master.groupby(['region2','year'])[['suicides_no','population']].sum(skipna=True).reset_index()
SR_region['suicides/100kpop']=SR_region['suicides_no']/(SR_region['population']/100000)
#%%[markdown]
# Plot SR by region
SR_region['region2'].value_counts().sort_index()
#%%
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
# Test the function by making a few reginal traces 
SA_trace=make_line_trace(SR_region[SR_region['region2']=='Asia and Pacific'],x='year',y='suicides/100kpop',\
    name='Asia',mode='lines+markers',label=SR_region['year'])
ECS_trace=make_line_trace(SR_region[SR_region['region2']=='Europe and Central Asia'],x='year',y='suicides/100kpop',\
        name='Europe and Central Asia',mode='lines+markers',label=SR_region['year'])
fig=go.Figure()
fig = go.Figure(data=[SA_trace, ECS_trace], layout=layout)
py.iplot(fig)

#%% 
# Making traces for all regions
reg_trace=[]
for region in list(set(regions2.values())):
    print(region)
    reg_trace.append(make_line_trace(SR_region[SR_region['region2']==region],x='year',y='suicides/100kpop',\
        name=region,mode='lines+markers',label=SR_region['year']))

#%%
# Making the regional plot and then add the world trace on
fig=go.Figure()
fig = go.Figure(data=reg_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)

#%%[markdown]
# There is a big jump in global suicide rates between 1989 and 1995. 
# The regional plot above seems to suggest the hike is related to European countires. 
# Now we plot the regional plots seperated against the world data

##### North America
py.iplot(go.Figure(data=[reg_trace[0],trace_globe],layout=layout))
##### Latin America and Carribean 
py.iplot(go.Figure(data=[reg_trace[1],trace_globe],layout=layout))
##### Asia and Pacific 
py.iplot(go.Figure(data=[reg_trace[2],trace_globe],layout=layout))
##### Europe and Central Asia
py.iplot(go.Figure(data=[reg_trace[3],trace_globe],layout=layout))
##### Midle East & North Africa
# Increase between 87 and 89, probably contributed to the hike from 88 to 89; overall trend from 89 onawrds was a decrease
py.iplot(go.Figure(data=[reg_trace[4],trace_globe],layout=layout))
##### Sub-Saharan Africa
# Dramatic increase from 86 to 88, and 2016; dramatic drop in 1996
py.iplot(go.Figure(data=[reg_trace[5],trace_globe],layout=layout))
# The individual plots shows the that the jump in global suicide rates between 89 and 95 paralleled the trend in Europe and Central Asia

#%%[markdown]
#### Melt the data down by country
SR_country=master.groupby(['country','year'])[['suicides_no','population']].sum(skipna=True).reset_index()
SR_country['suicides/100kpop']=SR_country['suicides_no']/(SR_country['population']/100000)

#%% 
SR_country['country'].value_counts().sort_index()
len(set(master['country']))
# Total number of country: 101
#%%[markdown]
# Create a country to region correspondence 
country2region=master[['country','iso3c','region','region2','region_id']]
country2region=country2region.drop_duplicates()
country2region['region'].value_counts().sort_index()
#%% European suicide rates by country
ECS_ctr=country2region[country2region['region_id']=='ECS'][['country']]
ECS_ctr=list(ECS_ctr['country'])
#%%
ECS_ctr_trace=[]
for country in ECS_ctr:
    ECS_ctr_trace.append(make_line_trace(SR_country[SR_country['country']==country],x='year',y='suicides/100kpop',\
        name=country,mode='lines+markers',label=SR_country['year']))
fig = go.Figure(data=ECS_ctr_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)

#%%
