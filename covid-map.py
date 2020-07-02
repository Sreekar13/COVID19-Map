import folium
import requests
import pandas
import io
import datetime
import platform
import os

#https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases?force_layout=desktop
#Data is gathered from Johns Hopkins University's data source
confirmed_url='https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv'
recovered_url='https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_recovered_global.csv&filename=time_series_covid19_recovered_global.csv'
deaths_url='https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_deaths_global.csv&filename=time_series_covid19_deaths_global.csv'

#Getting the CSV content from the responses
confirmed=requests.get(confirmed_url).content
recovered=requests.get(recovered_url).content
deaths=requests.get(deaths_url).content

#Fields to look for to extract from the CSVs
fields=['Province/State','Country/Region','Lat','Long',(datetime.date.today()-datetime.timedelta(days=1)).strftime("%-m/%-d/%y")]

#Creating DataFrame for confirmed cases
confirmed_df=pandas.read_csv(io.StringIO(confirmed.decode('utf-8')),skipinitialspace=True,usecols=fields)
#To rename column names
confirmed_df.rename(columns={"Province/State":"State","Country/Region":"Country","Lat":"Latitude","Long":"Longitude","{}".format((datetime.date.today()-datetime.timedelta(days=1)).strftime("%-m/%-d/%y")):"Confirmed"},inplace=True)

#Creating DataFrame for recovered cases
recovered_df=pandas.read_csv(io.StringIO(recovered.decode('utf-8')),skipinitialspace=True,usecols=[fields[-1]])
#To rename column names
recovered_df.rename(columns={"{}".format((datetime.date.today()-datetime.timedelta(days=1)).strftime("%-m/%-d/%y")):"Recovered"},inplace=True)

#Creating DataFrame for death cases
deaths_df=pandas.read_csv(io.StringIO(deaths.decode('utf-8')),skipinitialspace=True,usecols=[fields[-1]])
#To rename column names
deaths_df.rename(columns={"{}".format((datetime.date.today()-datetime.timedelta(days=1)).strftime("%-m/%-d/%y")):"Deaths"},inplace=True)

#A collective DataFrame by concatinating
total_df=pandas.concat([confirmed_df,recovered_df,deaths_df],axis=1)

#Creating a Map object
map=folium.Map(location=[40.253825, -74.473181],default="Mapbox Bright",zoom_start=2)

#Creating Feature Group to add to the maps like components
fg=folium.FeatureGroup(name="COVID Map")

#For adding polygons to the countries from population info
fg.add_child(folium.GeoJson(data=(open('WebMap/world.json','r',encoding='utf-8-sig').read())))

html = """<h3> %s :: %s </h3>
<h4>Confirmed: %s</h4>
<h4>Recovered: %s </h4>
<h4>Deaths: %s </h4>
"""

for row in range(len(total_df)):
    iframe = folium.IFrame(html=html % (str(total_df.loc[row]["Country"]),
                                        str(total_df.loc[row]["State"]),
                                        str(total_df.loc[row]["Confirmed"]),
                                        str(total_df.loc[row]["Recovered"]),
                                        str(total_df.loc[row]["Deaths"])),
                                        width=200,
                                        height=150)
    if(total_df.loc[row]["Latitude"] and total_df.loc[row]["Longitude"]):
        fg.add_child(folium.CircleMarker(location=[total_df.loc[row]["Latitude"],total_df.loc[row]["Longitude"]],
        popup=folium.Popup(iframe),
        color='grey',
        fill_color='red',
        fill_opacity=0.7))

map.add_child(fg)
map.save("CovidMap.html")

if(platform.system()=='Windows'):
    os.system('CovidMap.html')
else:
    os.system('open CovidMap.html')