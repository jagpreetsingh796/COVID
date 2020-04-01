from flask import  Flask,redirect,url_for,render_template,request,session
import os
import zipfile
import pandas as pd
import plotly.graph_objs as go
import json
import plotly
import plotly.graph_objs as go
import time
import schedule
from apscheduler.scheduler import Scheduler
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import atexit
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
import pickle


app = Flask(__name__)
cron = Scheduler(daemon=True)

cron.start()
df=pd.DataFrame()
df_grouped=pd.DataFrame()
df_new=pd.DataFrame()

os.environ['KAGGLE_USERNAME'] = "jagpreet796"
os.environ['KAGGLE_KEY'] = "d4f77b92179bfa82065bccfaa9c1dc54"
os.system("kaggle datasets download -d sudalairajkumar/novel-corona-virus-2019-dataset")
zf = zipfile.ZipFile('novel-corona-virus-2019-dataset.zip')
df = pd.read_csv(zf.open('covid_19_data.csv'))
df['ObservationDate']=pd.to_datetime(df['ObservationDate'])
df_grouped=df.groupby(['ObservationDate','Country/Region']).sum()

df_new=df_grouped.xs(df['ObservationDate'].max())
data= df.groupby(["ObservationDate"])['Confirmed','Deaths', 'Recovered'].sum().reset_index()
x_data=pd.DataFrame(data.index)
y_data=pd.DataFrame(data.Confirmed)
print(data.head())
# print(x_data.head())
# print(y_data.head())
# poly=PolynomialFeatures(degree=9)
# x_train,x_test,y_train,y_test=train_test_split(x_data,y_data,test_size=0.33,random_state=10)
# poly=PolynomialFeatures(degree=9)
# x_data=poly.fit_transform(x_data)
# lm=LinearRegression()
# lm.fit(x_data,y_data)
# lm.score(x_train,y_train)
# predicted=lm.predict(poly.fit_transform(x_test))
# error=np.sqrt(mean_squared_error(y_test,predicted))
# print(error)
# print(lm.score(poly.fit_transform(x_test),y_test))
# print(lm.predict(poly.fit_transform([[68]])))
# filename="finalized_model.pickle"
# filename_2="poly.pickle"
# pickle.dump(poly,open(filename_2,"wb"))
# pickle.dump(lm,open(filename,"wb"))
# model=pickle.load(open("finalized_model.pickle","rb"))
# poly_loaded=pickle.load(open("poly.pickle","rb"))
# model=pickle.load(open("finalized_model.pickle","rb"))
# poly_loaded=pickle.load(open("poly.pickle","rb"))
print(len(data))














@cron.interval_schedule(minutes=10)
def get_data():

    os.system("kaggle datasets download -d sudalairajkumar/novel-corona-virus-2019-dataset")
    zf = zipfile.ZipFile('novel-corona-virus-2019-dataset.zip')
    df_updated = pd.read_csv(zf.open('covid_19_data.csv'))
    df.update(df_updated)
    df['ObservationDate'] = pd.to_datetime(df['ObservationDate'])
    df_grouped_updated = df.groupby(['ObservationDate', 'Country/Region']).sum()
    df_grouped.update(df_grouped_updated)

    df_new_updated = df_grouped.xs(df['ObservationDate'].max())
    df_new.update(df_new_updated)
    data = df.groupby(["ObservationDate"])['Confirmed', 'Deaths', 'Recovered'].sum().reset_index()
    x_data = pd.DataFrame(data.index)
    y_data = pd.DataFrame(data.Confirmed)
    poly = pickle.load(open("poly.pickle", "rb"))
    lm = LinearRegression()
    x_data = poly.fit_transform(x_data)


    lm.fit(x_data, y_data)
    trial=len(data)
    print("Lets get this party started",lm.predict(poly.fit_transform([[trial+1]])))
    filename = "finalized_model.pickle"
    pickle.dump(lm, open(filename, "wb"))

    print("file updated")
@app.route('/')
def first():


    # data = [
    #     go.Bar(x=df['Country/Region'],y=df['Confirmed'])
    #
    # ]
    fig = go.Choropleth(
        locations=df_new.index.to_list(),  # Spatial coordinates
        z=df_new['Confirmed'],  # Data to be color-coded
        locationmode='country names',  # set of locations match entries in `locations`
        colorscale='Blues',

        text=df_new['Deaths'],
        hovertext=df_new['Recovered'],
        hovertemplate="<b>Confirmed<b>:%{z},Death:%{text},Recovered:%{hovertext}",
        colorbar_title='Confirmed<br>Cases',


    )

    data = [fig]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    schedule.every(1).minutes.do(get_data)
    return render_template('index.html',
                           graphJSON=graphJSON)

@app.route('/scatter')
def second():
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(y=data['Confirmed'].values, x=data['ObservationDate'].values, name='Confirmed'))
    # fig.add_trace(go.Scatter(y=data['Deaths'].values, x=data['ObservationDate'].values, name='Deaths'))
    # fig.add_trace(go.Scatter(y=data['Recovered'].values, x=data['ObservationDate'].values, name='Recovered'))
    fig=go.Scatter(y=data['Confirmed'], x=data['ObservationDate'])
    d = [fig]
    graphJSON_1 = json.dumps(d, cls=plotly.utils.PlotlyJSONEncoder)
    fig = go.Scatter(y=data['Deaths'], x=data['ObservationDate'])
    d1 = [fig]
    graphJSON_2 = json.dumps(d1, cls=plotly.utils.PlotlyJSONEncoder)
    fig = go.Scatter(y=data['Recovered'], x=data['ObservationDate'])
    d2 = [fig]
    graphJSON_3 = json.dumps(d2, cls=plotly.utils.PlotlyJSONEncoder)





    schedule.every(1).minutes.do(get_data)
    return render_template('index_2.html',
                           graphJSON=[graphJSON_1,graphJSON_2,graphJSON_3])

@app.route('/predict',methods=['POST','GET'])
def imp():
    if request.method =='POST':
        try:
            day=float(request.form['day'])
            filename = "finalized_model.pickle"
            load_model = pickle.load(open(filename, 'rb'))
            poly_loaded = pickle.load(open("poly.pickle", "rb"))
            prediction = load_model.predict(poly_loaded.fit_transform([[day]]))
            print("Inside the html",prediction[0][0])
            return render_template("result.html",prediction=round(prediction[0][0]))
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'


    else:
        return render_template("forecast.html")








if __name__=='__main__':
    app.run(debug=True)







