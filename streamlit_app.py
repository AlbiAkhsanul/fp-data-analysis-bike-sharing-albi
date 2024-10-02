import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from PIL import Image, ImageDraw

sns.set(style='dark')

# Fungsi untuk membuat sudut gambar menjadi melengkung
def make_rounded_corners(image, radius):
    # Membuat masker
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Membuat kotak dengan sudut membulat
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    
    # Menambahkan alfa (transparansi) pada gambar agar sudut menjadi melengkung
    rounded_image = image.copy()
    rounded_image.putalpha(mask)
    
    return rounded_image

def find_season_with_highest_shares(df):
    # mengumpulkan data berdasarkan season
    count_by_season = df.groupby('season')['count'].sum()
    
    # Find the season with the maximum shares
    max_season = count_by_season.idxmax()
    max_shares = count_by_season.max()

    return max_season, max_shares

def calculate_weather_averages(df, grouping_col, value):
    # mengfilter data agar hanya menggunakan row yang dibutuhkan
    filtered_df = df[df[grouping_col] == value]
    
    # menghitung rata rata values of humidity, temp, dan windspeed
    avg_humidity = filtered_df['humidity'].mean()
    avg_temp = filtered_df['temp'].mean()
    avg_windspeed = filtered_df['windspeed'].mean()

    return avg_humidity, avg_temp, avg_windspeed

def find_hour_with_highest_shares(df):
    # mengumpulkan data berdasarkan jam
    count_by_hour = df.groupby('hour')['count'].sum()
    
    # mencari jam dengan jumlah sewa terbanyak
    max_hour = count_by_hour.idxmax()
    max_shares = count_by_hour.max()

    return max_hour, max_shares

daily_df = pd.read_csv("main_daily.csv")
hourly_df = pd.read_csv("main_hourly.csv")

daily_df.sort_values(by="dteday", inplace=True)
daily_df.reset_index(inplace=True)
# Mengubah tipedata dteday menjadi datetime
daily_df['dteday'] = pd.to_datetime(daily_df['dteday'])

st.header(':star: Bike Sharing Data Analysis :star:')

# Filter data
min_date = daily_df["dteday"].min()
max_date = daily_df["dteday"].max()

with st.sidebar:
    img = Image.open("logo_lfa.png")
    # Mengubah gambar menjadi ukuran kotak
    img = img.resize((300, 300)) 
    # Membuat gambar berbentuk lingkaran
    img_rounded = make_rounded_corners(img, radius=50)
    st.image(img_rounded)

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Date Range',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_daily_df = daily_df[(daily_df["dteday"] >= str(start_date)) & (daily_df["dteday"] <= str(end_date))]
main_hourly_df = hourly_df[(hourly_df["dteday"] >= str(start_date)) & (hourly_df["dteday"] <= str(end_date))]

min_date_str = min_date.strftime('%Y-%m-%d')
max_date_str = max_date.strftime('%Y-%m-%d')

st.subheader(f"From {min_date_str} to {max_date_str} there were :")

# Membuat colom agar rapi
col1, col2, col3 = st.columns(3)
with col1:
    total_orders = main_daily_df['count'].sum()
    st.metric("Total Users", value=total_orders)

with col2:
    total_sum = main_daily_df['registered'].sum()
    st.metric("Registered Users", value=total_sum)

with col3:
    total_sum = main_daily_df['casual'].sum()
    st.metric("Casual Users", value=total_sum)

st.subheader("The Distribution of Casual Vs Registered Users:")
# Membuat plot
fig, ax = plt.subplots()  # Membuat figure dan axes terlebih dahulu
main_daily_df[['casual', 'registered']].plot(kind='hist', bins=20, alpha=0.5, stacked=True, ax=ax)
ax.set_title('Distribution of Casual vs Registered Users')
ax.set_xlabel('Number Of Users')
ax.set_ylabel('Frequency')

# Menampilkan plot di Streamlit
st.pyplot(fig)

sum_casual = sum(main_daily_df['casual'])
sum_registered = sum(main_daily_df['registered'])

# Membuat pie chart
data = [sum_casual, sum_registered]
ax.set_xlabel('')
ax.set_ylabel('')
plt.pie(data, autopct='%1.1f%%')
plt.title('Total Users')
plt.legend()
st.pyplot(plt)

total_users = sum(data)  # Total users
casual_percent = (sum_casual / total_users) * 100
registered_percent = (sum_registered / total_users) * 100

# menampilkan hasilnya
st.markdown(f"""
    These charts illustrates the proportion of bike sharing made by casual users versus registered users. From these charts we can see that from <span style='color:orange'><strong>{total_users}</strong></span> users, <span style='color:orange'><strong>{registered_percent:.2f}%</strong></span> are registered, and the <span style='color:orange'><strong>{casual_percent:.2f}%</strong></span> are casual
    """, unsafe_allow_html=True)

st.subheader("The Distribution of Bike Sharing By Season:")
# Grouping data berdasarkan season
count_by_season = main_daily_df.groupby('season')['count'].sum()

# Membuat bar chart
plt.figure(figsize=(12, 6))
plt.bar(count_by_season.index, count_by_season.values, color='skyblue')
plt.title('Total Bike Sharing by Season')
plt.xlabel('Season')
plt.ylabel('Total Bike Sharing')
plt.xticks(count_by_season.index)
plt.grid(axis='y')

# Menampilkan chart
st.pyplot(plt)

# Mencari season dengan count terbanyk
max_season, max_shares = find_season_with_highest_shares(main_daily_df)

# Mencari nilai rata rata setiap season
avg_humidity, avg_temp, avg_windspeed = calculate_weather_averages(main_daily_df,'season', max_season)
avg_windspeed *= 100

# Mengelompokkan berdasarkan season dan mengambil rata-rata untuk kolom windspeed, temp, atemp, humidity
weather_by_season = main_daily_df.groupby('season')[['humidity', 'temp', 'windspeed',]].mean()
weather_by_season['windspeed'] *= 100

# Membuat bar plot
weather_by_season.plot(kind='bar', figsize=(12, 6))

# Menambahkan judul dan label
plt.title('Average Temperature, Wind Speed, and Humidity by Season')
plt.xlabel('Musim')
plt.ylabel('Rata-rata Nilai')
plt.xticks(rotation=0)  # Rotasi label di sumbu x agar lebih mudah dibaca
plt.grid(axis='y')

# Menampilkan plot
st.pyplot(plt)
# menampilkan hasilnya
st.markdown(f"""
    <h4>The season with the most bike sharing is 
    <span style='color:orange'><strong>{max_season}</strong></span> 
    with a total of 
    <span style='color:orange'><strong>{max_shares}</strong></span> sharing.</h4>
    """, unsafe_allow_html=True)
st.write(f"During this season, the average humidity was **{avg_humidity:.2f}**, the average temperature was **{avg_temp:.2f}**, and the average windspeed was **{avg_windspeed:.2f}**.")

st.subheader("The Distribution of Bike Sharing By Hour:")
# penyewaan berdasarkan jam
count_by_hour = main_hourly_df.groupby('hour')['count'].sum()

# Membuat Bar Plot
plt.figure(figsize=(12, 6))
plt.bar(count_by_hour.index, count_by_hour.values, color='skyblue')
plt.title('Total Bike Sharing by Hour')
plt.xlabel('Hour')
plt.ylabel('Total Bike Sharing')
plt.xticks(count_by_hour.index) 
plt.grid(axis='y')
plt.show()

# menampilkan plot
st.pyplot(plt)

# Mencari jam dengan count terbanyak
max_hour, max_shares = find_hour_with_highest_shares(main_hourly_df)
avg_humidity_hourly, avg_temp_hourly, avg_windspeed_hourly = calculate_weather_averages(main_hourly_df,'hour', max_hour) 
avg_humidity_hourly *=100
avg_temp_hourly *= 100
avg_windspeed_hourly *=100
# Menampilkan hasil
st.markdown(f"""
    <h4>The hour with the most bike sharing is 
    <span style='color:orange'><strong>{max_hour}.00</strong></span> 
    with a total of 
    <span style='color:orange'><strong>{max_shares}</strong></span> sharing.</h4>
    """, unsafe_allow_html=True)
st.write(f"During this hour, the average humidity was **{avg_humidity_hourly:.2f}**, the average temperature was **{avg_temp_hourly:.2f}**, and the average windspeed was **{avg_windspeed_hourly:.2f}**.")