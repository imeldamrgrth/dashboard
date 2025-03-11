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
    # Tampilkan logo jika ada
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        image = Image.open(logo_path)
        st.image(image, use_container_width=True)
    
    # Filter tanggal
    st.write("### Pilih Rentang Tanggal")
    date_range = st.date_input("Rentang Tanggal", [])

# Set judul
st.title("📊 E-Commerce Data Analysis Dashboard")
st.write("## 🔍 Analisis Data E-Commerce")

# Load dataset
@st.cache_data
def load_data():
    geolocation = pd.read_csv("geolocation_dataset.csv")
    orders = pd.read_csv("orders_dataset.csv")
    order_items = pd.read_csv("order_items_dataset.csv")
    order_payments = pd.read_csv("order_payments_dataset.csv")
    order_reviews = pd.read_csv("order_reviews_dataset.csv")
    products = pd.read_csv("products_dataset.csv")
    product_translation = pd.read_csv("product_category_name_translation.csv")
    sellers = pd.read_csv("sellers_dataset.csv")
    
    return geolocation, orders, order_items, order_payments, order_reviews, products, product_translation, sellers

# Load semua dataset
geolocation, orders, order_items, order_payments, order_reviews, products, product_translation, sellers = load_data()

# Menampilkan daftar dataset yang berhasil dimuat
st.success("✅ Semua dataset berhasil dimuat!")

# ======================== ANALISIS DATA ========================

# 1️⃣ Distribusi Metode Pembayaran
st.write("## 💳 Distribusi Metode Pembayaran")
if 'payment_type' in order_payments.columns:
    payment_counts = order_payments['payment_type'].value_counts()
    st.bar_chart(payment_counts)
else:
    st.warning("Kolom 'payment_type' tidak ditemukan dalam dataset.")

# 2️⃣ Distribusi Harga Produk
st.write("## 💰 Distribusi Harga Produk")
if 'price' in order_items.columns:
    fig, ax = plt.subplots()
    sns.histplot(order_items['price'], bins=30, kde=True, color="royalblue", ax=ax)
    ax.set_xlabel("Harga Produk")
    ax.set_ylabel("Frekuensi")
    ax.set_title("Distribusi Harga Produk")
    st.pyplot(fig)
else:
    st.warning("Kolom 'price' tidak ditemukan dalam dataset.")

# 3️⃣ Dampak Harga terhadap Jumlah Pesanan
st.write("## 📈 Dampak Harga terhadap Jumlah Pesanan")
if 'price' in order_items.columns and 'order_id' in order_items.columns:
    order_count = order_items.groupby('price')['order_id'].nunique()
    fig, ax = plt.subplots()
    sns.scatterplot(x=order_count.index, y=order_count.values, alpha=0.5, color='red', ax=ax)
    ax.set_xlabel("Harga Produk")
    ax.set_ylabel("Jumlah Pesanan")
    ax.set_title("Dampak Harga terhadap Jumlah Pesanan")
    st.pyplot(fig)
else:
    st.warning("Kolom 'price' atau 'order_id' tidak ditemukan dalam dataset.")

# 4️⃣ Distribusi Waktu Respons Ulasan Pelanggan
st.write("## ⏳ Distribusi Waktu Respons Ulasan Pelanggan")
if 'review_creation_date' in order_reviews.columns and 'review_answer_timestamp' in order_reviews.columns:
    order_reviews['review_creation_date'] = pd.to_datetime(order_reviews['review_creation_date'])
    order_reviews['review_answer_timestamp'] = pd.to_datetime(order_reviews['review_answer_timestamp'])
    order_reviews['response_time'] = (order_reviews['review_answer_timestamp'] - order_reviews['review_creation_date']).dt.days
    fig, ax = plt.subplots()
    sns.histplot(order_reviews['response_time'].dropna(), bins=30, kde=True, color="seagreen", ax=ax)
    ax.set_xlabel("Hari Setelah Pengiriman")
    ax.set_ylabel("Frekuensi")
    ax.set_title("Distribusi Waktu Respons Ulasan Pelanggan")
    st.pyplot(fig)
else:
    st.warning("Kolom 'review_creation_date' atau 'review_answer_timestamp' tidak ditemukan dalam dataset.")

# 5️⃣ Hubungan Kategori Produk dengan Rating Ulasan
st.write("## ⭐ Hubungan Kategori Produk dengan Rating Ulasan")
if 'review_score' in order_reviews.columns and 'product_id' in order_items.columns and 'product_id' in products.columns:
    merged_data = order_items.merge(products, on="product_id", how="left")
    merged_data = merged_data.merge(order_reviews, on="order_id", how="left")
    category_ratings = merged_data.groupby('product_category_name')['review_score'].mean()
    
    fig, ax = plt.subplots()
    sns.barplot(x=category_ratings.index[:10], y=category_ratings.values[:10], palette="coolwarm", ax=ax)
    ax.set_xlabel("Kategori Produk")
    ax.set_ylabel("Rata-rata Rating")
    ax.set_title("Hubungan Kategori Produk dengan Rating Ulasan")
    plt.xticks(rotation=90)
    st.pyplot(fig)
else:
    st.warning("Kolom 'review_score' atau 'product_category_name' tidak ditemukan dalam dataset.")

# 6️⃣ Distribusi Jumlah Produk per Penjual
st.write("## 🛍️ Distribusi Jumlah Produk per Penjual")
if 'seller_id' in order_items.columns:
    seller_counts = order_items['seller_id'].value_counts()
    fig, ax = plt.subplots()
    sns.histplot(seller_counts, bins=30, kde=True, color="purple", ax=ax)
    ax.set_xlabel("Jumlah Produk per Penjual")
    ax.set_ylabel("Frekuensi")
    ax.set_title("Distribusi Jumlah Produk per Penjual")
    st.pyplot(fig)
else:
    st.warning("Kolom 'seller_id' tidak ditemukan dalam dataset.")

# 7️⃣ Hubungan Jumlah Produk dalam Pesanan dan Biaya Pengiriman
st.write("## 📦 Hubungan Jumlah Produk dalam Pesanan dan Biaya Pengiriman")
if 'freight_value' in order_items.columns and 'order_id' in order_items.columns:
    order_shipping = order_items.groupby("order_id").agg(
        total_items=("order_item_id", "count"),
        total_freight=("freight_value", "sum")
    ).reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(x=order_shipping['total_items'], y=order_shipping['total_freight'], alpha=0.5, color="orange", ax=ax)
    ax.set_xlabel("Jumlah Produk dalam Pesanan")
    ax.set_ylabel("Total Biaya Pengiriman")
    ax.set_title("Hubungan Jumlah Produk dalam Pesanan dan Biaya Pengiriman")
    st.pyplot(fig)
else:
    st.warning("Kolom 'freight_value' atau 'order_id' tidak ditemukan dalam dataset.")