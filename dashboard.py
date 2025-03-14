import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import os

# Konfigurasi halaman
st.set_page_config(page_title="E-Commerce Data Analysis", layout="wide")

# Sidebar dengan logo dan filter tanggal
with st.sidebar:
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        image = Image.open(logo_path)
        st.image(image, use_container_width=True)
    
    st.write("### Pilih Rentang Tanggal")
    date_range = st.date_input("Rentang Tanggal", value=(pd.to_datetime("2017-01-01"), pd.to_datetime("2018-01-01")), 
                               min_value=pd.to_datetime("2016-01-01"), max_value=pd.to_datetime("2018-12-31"))

# Set judul
st.title("📊 E-Commerce Data Analysis Dashboard")
st.write("## 🔍 Analisis Data E-Commerce")

# Load dataset
@st.cache_data
def load_data():
    geolocation = pd.read_csv("geolocation_dataset.csv")
    orders = pd.read_csv("orders_dataset.csv", parse_dates=["order_purchase_timestamp"])
    order_items = pd.read_csv("order_items_dataset.csv")
    order_payments = pd.read_csv("order_payments_dataset.csv")
    order_reviews = pd.read_csv("order_reviews_dataset.csv", parse_dates=["review_creation_date", "review_answer_timestamp"])
    products = pd.read_csv("products_dataset.csv")
    sellers = pd.read_csv("sellers_dataset.csv")
    
    return geolocation, orders, order_items, order_payments, order_reviews, products, sellers

# Load semua dataset
geolocation, orders, order_items, order_payments, order_reviews, products, sellers = load_data()

# Konversi ke datetime64[ns]
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])

# Filter orders berdasarkan tanggal
filtered_orders = orders[(orders['order_purchase_timestamp'] >= start_date) & 
                         (orders['order_purchase_timestamp'] <= end_date)]

# Filter order_payments berdasarkan order_id 
filtered_order_payments = order_payments[order_payments['order_id'].isin(filtered_orders['order_id'])]

# Menggunakan filtered_order_payments untuk analisis
payment_counts = filtered_order_payments['payment_type'].value_counts()

# Filter order_items berdasarkan order_id 
filtered_order_items = order_items[order_items['order_id'].isin(filtered_orders['order_id'])]

# Filter order_reviews berdasarkan order_id 
filtered_order_reviews = order_reviews[order_reviews['order_id'].isin(filtered_orders['order_id'])]

st.success("✅ Dataset telah difilter sesuai rentang tanggal yang dipilih!")

# 1️⃣ Distribusi Metode Pembayaran
st.write("## 💳 Distribusi Metode Pembayaran")
payment_counts = filtered_order_payments['payment_type'].value_counts()
st.bar_chart(payment_counts)

# 2️⃣ Distribusi Harga Produk
st.write("## 💰 Distribusi Harga Produk")
if 'price' in filtered_order_items.columns:
    fig, ax = plt.subplots()
    sns.histplot(filtered_order_items['price'], bins=30, kde=True, color="royalblue", ax=ax)
    ax.set_xlabel("Harga Produk")
    ax.set_ylabel("Frekuensi")
    ax.set_title("Distribusi Harga Produk")
    st.pyplot(fig)
else:
    st.warning("Kolom 'price' tidak ditemukan dalam dataset.")
    
# 3️⃣ Dampak Harga terhadap Jumlah Pesanan
st.write("## 📈 Dampak Harga terhadap Jumlah Pesanan")
order_count = filtered_order_items.groupby('price')['order_id'].nunique()
fig, ax = plt.subplots()
sns.scatterplot(x=order_count.index, y=order_count.values, alpha=0.5, color='red', ax=ax)
ax.set_xlabel("Harga Produk")
ax.set_ylabel("Jumlah Pesanan")
ax.set_title("Dampak Harga terhadap Jumlah Pesanan")
st.pyplot(fig)

# 4️⃣ Distribusi Waktu Respons Ulasan Pelanggan
st.write("## ⏳ Distribusi Waktu Respons Ulasan Pelanggan")
if 'review_creation_date' in filtered_order_reviews.columns and 'review_answer_timestamp' in filtered_order_reviews.columns:
    filtered_order_reviews['review_creation_date'] = pd.to_datetime(filtered_order_reviews['review_creation_date'])
    filtered_order_reviews['review_answer_timestamp'] = pd.to_datetime(filtered_order_reviews['review_answer_timestamp'])
    filtered_order_reviews['response_time'] = (filtered_order_reviews['review_answer_timestamp'] - filtered_order_reviews['review_creation_date']).dt.days
    
    fig, ax = plt.subplots()
    sns.histplot(filtered_order_reviews['response_time'].dropna(), bins=30, kde=True, color="seagreen", ax=ax)
    ax.set_xlabel("Hari Setelah Pengiriman")
    ax.set_ylabel("Frekuensi")
    ax.set_title("Distribusi Waktu Respons Ulasan Pelanggan")
    st.pyplot(fig)
else:
    st.warning("Kolom 'review_creation_date' atau 'review_answer_timestamp' tidak ditemukan dalam dataset.")

# 5️⃣ Hubungan Kategori Produk dengan Rating Ulasan
st.write("## ⭐ Hubungan Kategori Produk dengan Rating Ulasan")
merged_data = filtered_order_items.merge(products, on="product_id", how="left")
merged_data = merged_data.merge(filtered_order_reviews, on="order_id", how="left")
category_ratings = merged_data.groupby('product_category_name')['review_score'].mean()
fig, ax = plt.subplots()
sns.barplot(x=category_ratings.index[:10], y=category_ratings.values[:10], palette="coolwarm", ax=ax)
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Rata-rata Rating")
ax.set_title("Hubungan Kategori Produk dengan Rating Ulasan")
plt.xticks(rotation=90)
st.pyplot(fig)

# 6️⃣ Distribusi Jumlah Produk per Penjual
st.write("## 🛍️ Distribusi Jumlah Produk per Penjual")
seller_counts = filtered_order_items['seller_id'].value_counts()
fig, ax = plt.subplots()
sns.histplot(seller_counts, bins=30, kde=True, color="purple", ax=ax)
ax.set_xlabel("Jumlah Produk per Penjual")
ax.set_ylabel("Frekuensi")
ax.set_title("Distribusi Jumlah Produk per Penjual")
st.pyplot(fig)

# 7️⃣ Hubungan Jumlah Produk dalam Pesanan dan Biaya Pengiriman
st.write("## 📦 Hubungan Jumlah Produk dalam Pesanan dan Biaya Pengiriman")
order_shipping = filtered_order_items.groupby("order_id").agg(
    total_items=("order_item_id", "count"),
    total_freight=("freight_value", "sum")
).reset_index()
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(x=order_shipping['total_items'], y=order_shipping['total_freight'], alpha=0.5, color="orange", ax=ax)
ax.set_xlabel("Jumlah Produk dalam Pesanan")
ax.set_ylabel("Total Biaya Pengiriman")
ax.set_title("Hubungan Jumlah Produk dalam Pesanan dan Biaya Pengiriman")
st.pyplot(fig)
