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
fig=go.Figure()
#fig.add_trace(trace_globe)
fig = go.Figure(data=[trace_globe], layout=layout)
py.iplot(fig)

#%%[markdown]
# Melt the data down by region
SR_region=master.groupby(['region','year'])[['suicides_no','population']].sum(skipna=True).reset_index()
SR_region['suicides/100kpop']=SR_region['suicides_no']/(SR_region['population']/100000)
#%%[markdown]
# Plot SR by region
SR_region['region'].value_counts().sort_index()
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
# Test the function by making a few reginal traces 
SA_trace=make_line_trace(SR_region[SR_region['region']=='South Asia'],x='year',y='suicides/100kpop',\
    name='South Asia',mode='lines+markers',label=SR_region['year'])
ECS_trace=make_line_trace(SR_region[SR_region['region']=='Europe and Central Asia'],x='year',y='suicides/100kpop',\
        name='Europe and Central Asia',mode='lines+markers')
#%% 
# Making traces for all regions
reg_trace=[]
for region_id in regions.keys():
    print(region_id)
    reg_trace.append(make_line_trace(SR_region[SR_region['region']==regions[region_id]],x='year',y='suicides/100kpop',\
        name=regions[region_id],mode='lines+markers',label=SR_region['year']))

#%%
# Making the regional plot and then add the world trace on
fig=go.Figure()
fig = go.Figure(data=reg_trace, layout=layout)
fig.add_trace(trace_globe)
py.iplot(fig)

#%%[markdown]
###### Melt the data down by country
SR_country=master.groupby(['country','year'])[['suicides_no','population']].sum(skipna=True).reset_index()
SR_country['suicides/100kpop']=SR_country['suicides_no']/(SR_country['population']/100000)

#%%
