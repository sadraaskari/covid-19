import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import psycopg2

conn = psycopg2.connect(
	host="localhost",
	database="postgres",
	user="postgres",
	password="09128601494Sadra"
)

cur = conn.cursor()

url = "https://vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com/api/npm-covid-data/"

headers = {
	"X-RapidAPI-Key": "52f13d0799msh8be268620dee59ep1afb2bjsn98b054c808d0",
	"X-RapidAPI-Host": "vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com"
}
response = requests.request("GET", url, headers=headers)
data = response.json()
countries = []
cases = []
for i in data:
	if i['Country'] != 'Total:' and i['Country'] != 'World':
		if i['TotalCases'] >= 0.02 * data[0]['TotalCases']:
			countries.append(i['Country'])
			cases.append(i['TotalCases'])
countries.append('Others')
cases.append(data[0]['TotalCases'] - sum(cases))
plt.pie(cases, labels=countries, autopct='%1.1f%%')


start_date_str = '20200201'
end_date_str = '20230220'
start_date = datetime.strptime(start_date_str, '%Y%m%d').date()
end_date = datetime.strptime(end_date_str, '%Y%m%d').date()
url2 = "https://covid-19-statistics.p.rapidapi.com/reports/total"
confirmed = []
deaths = []
recovered = []
date = []
while start_date <= end_date:
	cur.execute("SELECT * FROM covid19 WHERE date = %s", (start_date.strftime('%Y-%m-%d'),))
	row = cur.fetchall()
	if row == []:
		querystring = {"date": start_date.strftime('%Y-%m-%d')}

		headers2 = {
			"X-RapidAPI-Key": "52f13d0799msh8be268620dee59ep1afb2bjsn98b054c808d0",
			"X-RapidAPI-Host": "covid-19-statistics.p.rapidapi.com"
		}

		response2 = requests.request("GET", url2, headers=headers2, params=querystring)

		data2 = response2.json()
		print(data2)

		confirmed.append(data2['data']['confirmed'])
		deaths.append(data2['data']['deaths'])
		recovered.append(data2['data']['recovered'])
		date.append(start_date.strftime('%Y-%m-%d'))
		confirm = data2['data']['confirmed']
		death = data2['data']['deaths']
		recover = data2['data']['recovered']
		date2 = start_date.strftime('%Y-%m-%d')
		cur.execute("INSERT INTO covid19 (date, confirmed, deaths, recovered) VALUES (%s, %s, %s, %s)", (date2, confirm, death, recover))
		conn.commit()

		start_date += timedelta(days=1)
	else:
		start_date += timedelta(days=1)
		continue

fig1, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
cur.execute("SELECT date, confirmed FROM covid19")
results = cur.fetchall()
dates = [result[0] for result in results]
confirmed = [result[1] for result in results]
line = ax1.plot(dates, confirmed, 'r')
ax1.set(xlabel='Date', ylabel='Confirmed Cases', title='Confirmed Cases')
ax1.tick_params(axis='x', rotation=45)


cur.execute("SELECT deaths FROM covid19")
results = cur.fetchall()
deaths = [result[0] for result in results]
ax2.plot(dates, deaths, 'b')
ax2.set(xlabel='Date', ylabel='Deaths', title='Deaths')
ax2.tick_params(axis='x', rotation=45)


cur.execute("SELECT recovered FROM covid19")
results = cur.fetchall()
recovered = [result[0] for result in results]
ax3.plot(dates, recovered, 'g')
ax3.set(xlabel='Date', ylabel='Recovered', title='Recovered')
ax3.tick_params(axis='x', rotation=45)

plt.subplots_adjust(hspace=0)

plt.show()
cur.close()
conn.close()


