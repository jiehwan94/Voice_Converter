import streamlit as st
import speech_recognition as sr
import numpy as np
import pandas as pd
from dateutil.parser import parse
from rake_nltk import Rake
import streamlit.components.v1 as components
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from geotext import GeoText
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout = "wide")

st.title("Creating a Dashboard from Voice Data")

col1,col2 = st.columns(2) 

# uploaded_file = st.file_uploader("Choose a file")

# Initialize recognizer class (For recognizing the speech)
r = sr.Recognizer()

with sr.AudioFile('C:/Users/82104/Desktop/Online Learning/Streamlit/Speech_Text_Converter/Voice 002.wav') as source:
    audio_text = r.record(source)
    
    try:
        txt = r.recognize_google(audio_text)
        #print(text)
        if st.button('Convert'):
            
            # st.write(txt)
            
            # Define keywords
            
            split_word = 'dropped'
            before_split, split_word, after_split = txt.partition(split_word)
            
            keyword = 'all right so'
            before_keyword, keyword, after_keyword = before_split.partition(keyword)
            
            # Extract pickup and dropoff time
            pu_time = parse(after_keyword, fuzzy=True)
            dropoff_time = parse(after_split, fuzzy=True)
            
            # Extract pickup and dropoff cities
            pickup_city = ''.join(GeoText(after_keyword).cities)
            dropoff_city = ''.join(GeoText(after_split).cities)
            
            # Calculate the percentile
            cust_rate = 340
            carrier_rate = 300
            
            mu = 310.0
            sigma = 20
            data = np.random.randn(800) * sigma + mu
            carrier_perc_val = percentileofscore(data, carrier_rate)
            cust_perc_val = percentileofscore(data, cust_rate)
            
            profit = cust_rate - carrier_rate
            
            # Create a Dataframe
            column_names = ["PickUp_City","PickUp_Datetime", 
                            "DropOff_City", "DropOff_DateTime",
                            "Cust_Rate","Carrier_Rate", "Profit", 
                            "Carrier_Percentile", "Customer_Percentile"]
            
            df = pd.DataFrame(columns = column_names)
            df.loc[len(df.index)] = [pickup_city, pu_time, 
                                     dropoff_city, dropoff_time,
                                     cust_rate, carrier_rate, profit,  
                                     carrier_perc_val, cust_perc_val] 
            
            # st.write(df.head())
            
            
            # Dispaly perctile distribution
            fig2 = plt.figure(figsize = (10, 5))

            hx, hy, _ = plt.hist(data, bins=50,color="lightblue")

            plt.ylim(0.0,max(hx)+0.05)
            plt.title('Price Distribution for the Lane (%s - %s)' %(pickup_city, dropoff_city))
            plt.grid()
            plt.axvline(x= carrier_rate, color='red', label='axvline - full height')
            plt.axvline(x= cust_rate, color='green', label='axvline - full height')
            
            # st.pyplot(fig2)
            
            
            # Display Spot Rate Trend
            df2 = pd.DataFrame()

            np.random.seed(42)
            df2['date'] = pd.date_range('2021-01-01', '2021-12-20', freq='D')
            df2['month'] = df2['date'].dt.month
            df2['spot_rate'] = np.random.randint(low=150, high=400, size=len(df2.index))

            df4 = df2[df2['month'] == 12].tail(15)

            fig = go.Figure()

            fig = make_subplots(rows=1, cols=2, column_widths=[0.9, 0.1])

            trendline = df2.groupby(['month']).spot_rate.median()
            x1,y1 = list(trendline.index), trendline.values
            stds = df2.groupby(['month']).spot_rate.std().values
            n_vals = df2.groupby(['month']).date.count().values

            ## construct a 0.95 CI using mean ± z*std/sqrt(n)
            y1_upper = list(y1 + 1.96*stds/np.sqrt(n_vals))
            y1_lower = list(y1 - 1.96*stds/np.sqrt(n_vals))
            y1_lower = y1_lower[::-1]

            x1_rev = x1[::-1]

            fig.add_trace(go.Scatter(x=x1, y=y1, line_shape="spline", line_color="blue", name="trendline"))

            fig.add_trace(go.Scatter(
                x=x1+x1_rev,
                y=y1_upper+y1_lower,
                line_shape="spline",
                fill='toself',
                fillcolor='rgba(255,192,203,0.5)',
                line_color='rgba(255,255,255,0)',
                showlegend=False,
                name="0.95 CI",
            ))

            fig.add_trace(go.Box(y = df2['spot_rate'],
                                x = df2['month'],
                                marker_color = '#6AF954',
                                name = 'Monthly'),
                        row=1, col=1)

            fig.add_trace(go.Box(y = df4['spot_rate'], 
                                x = df4['month'],
                                marker_color = "orange",
                                name = "Past 15 days"),
                        row=1, col=2)

            fig.update_layout(paper_bgcolor="black",
                            plot_bgcolor="black",#template="plotly_dark",
                            font_color="white",
                            title="Spot Rates Trend from %s to %s " %(pickup_city, dropoff_city),
                            xaxis_title="Month",
                            yaxis_title="Spot Rate",
                            xaxis = dict(tickmode='array', tickvals=x1),
                            yaxis2=dict(range=[140,410]))

            # st.plotly_chart(fig)
            
            # Dispaly overall trip route from pickup location to destination
            with col1:
                st.write(txt)
                st.write(df.head())
                st.pyplot(fig2)
                components.iframe(f"https://wego.here.com/directions/mix/{pickup_city}/{dropoff_city}l", height = 500)
            
            with col2:
                st.plotly_chart(fig)
            
            # components.iframe(f"https://wego.here.com/directions/mix/{pickup_city}/{dropoff_city}l", height = 500)
        
            
    except:
        print('Error... Try again...')

