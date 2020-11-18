import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
According to the [Center for American Progress](https://www.americanprogress.org/issues/women/reports/2020/03/24/482141/quick-facts-gender-wage-gap/), the gender wage gap is the difference in pay between men and women. As of 2018, women on average earned 82 cents for every $1 men earned and this gap is larger for women of color. It is based on the median pay of men and women across all industries to capture the variety of factors that account for this difference. Factors incldue the different industries men and women are funneled into and the different years of experience and hours worked due to caregiving responabilities. The Center for American Progress advocates for increasing  more family paid and sick leave to address this gap.

The [GSS](http://www.gss.norc.org/About-The-GSS) is the General Social Survey which aims to capture American demographic data and trends and social attitudes. In addition to demographic and behavorial questions, they cover topics about demographics and cover topics like civil liberties, crimes, and social mobilitiy. They randomnly select households in the US that covers people living urban, suburban and rural areas to do an in-person interview.
'''

avgs = gss_clean.groupby("sex").agg({"income": "mean", "job_prestige": "mean", "socioeconomic_index": "mean", "education": "mean"}).round(2)
avgs = avgs.rename({'sex': "Sex", "income": "Income", "job_prestige": "Job Prestige", "socioeconomic_index": "Socioeconomic Index", "education": "Education"}, axis=1)
avgs = avgs.reset_index()

table_means = ff.create_table(avgs)

gss_clean.male_breadwinner = gss_clean.astype('category').male_breadwinner.cat.reorder_categories(['strongly disagree', 'disagree', 'agree', 'strongly agree'])
bars = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index().rename({'sex': 'Sex', 'male_breadwinner': 'Male Breadwinner?', 0:'Count'}, axis=1)

fig_bars = px.bar(bars, x="Male Breadwinner?", y="Count", color="Sex", barmode='group', labels={"Count?": "Number of Responses", "Male Breadwinner?": "Response"})

income_prestige_fig = px.scatter(gss_clean, x="job_prestige", y="income", color="sex", 
                 trendline='ols',
                  hover_data=['education', 'socioeconomic_index'],
                 labels={'job_prestige': 'Occupational Prestige', 'income':'Income'})

boxplot_inc = px.box(gss_clean, x='income', y='sex', color='sex', labels={'income': 'Income', 'sex':''})
boxplot_inc.update_layout(showlegend=False)

boxplot_job = px.box(gss_clean, x='job_prestige', y='sex', color='sex', labels={'job_prestige': 'Job Prestige', 'sex':''})
boxplot_job.update_layout(showlegend=False)

data = gss_clean[['income', 'sex', 'job_prestige']]
data['job_prestige_binned'] = pd.cut(data.job_prestige, bins=6, labels=['Very Low', 'Low', 'Medium-Low', 'Medium-High', 'High', 'Very High'])
data = data.dropna(axis=0, how='any')

fig4 = px.box(data,x='income', y='sex', color='sex', 
              labels={'income': 'Income', 'sex':''},
              facet_col='job_prestige_binned', 
              category_orders={'job_prestige_binned':['Very Low', 'Low', 'Medium-Low', 'Medium-High', 'High', 'Very High']}, facet_col_wrap=2)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div(    
    [        
        html.H1("Understanding the Gender Wage Gap"),
        dcc.Markdown(children = markdown_text),
        html.H2("Mean Statistics by Sex"),
        dcc.Graph(figure=table_means),
        html.H2("Responses to Male Breadwinner Question by Sex"),
        dcc.Graph(figure=fig_bars),
        html.H2("Income and Occupational Prestige by Sex"),
        dcc.Graph(figure=income_prestige_fig),
        html.Div([
            
            html.H2("Income By Sex"),
            
            dcc.Graph(figure=boxplot_inc)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            html.H2("Occupational Prestige By Sex"),
            dcc.Graph(figure=boxplot_job)
            
        ], style = {'width':'48%', 'float':'right'}), 
        html.H2("Grouped Occupational Prestige by Sex"),
        dcc.Graph(figure=fig4)
    ]
    )
if __name__ == '__main__':

    #app.run_server(debug=True, mode='inline', port=9004, host='127.0.0.1')
    app.run_server(debug=True)
