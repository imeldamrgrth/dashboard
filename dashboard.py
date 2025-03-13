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
 
 # Sidebar untuk memilih rentang tanggal
st.sidebar.write("### Pilih Rentang Tanggal")
date_range = st.sidebar.date_input("Rentang Tanggal", [])

# Filter data berdasarkan rentang tanggal
if len(date_range) == 2:
    start_date, end_date = date_range
    orders = orders[(orders['order_purchase_timestamp'] >= pd.Timestamp(start_date)) & 
                    (orders['order_purchase_timestamp'] <= pd.Timestamp(end_date))]
    st.sidebar.write(f"Menampilkan data dari {start_date} hingga {end_date}")

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

# Sidebar untuk memilih pertanyaan bisnis
st.sidebar.title("Pilih Pertanyaan Bisnis")
questions = [
    "Semua visualisasi",
    "Apa metode pembayaran yang paling sering digunakan?",
    "Bagaimana distribusi harga produk?",
    "Apakah harga lebih rendah menyebabkan lebih banyak pesanan?",
    "Berapa rata-rata waktu pelanggan memberikan ulasan?",
    "Kategori produk mana yang memiliki rating tertinggi dan terendah?",
    "Bagaimana pola distribusi jumlah produk per penjual?",
    "Apakah semakin banyak produk dalam pesanan meningkatkan biaya pengiriman?"
]
question = st.sidebar.selectbox("Pilih pertanyaan untuk divisualisasikan:", questions)

# Fungsi untuk menampilkan visualisasi
def show_visualization(selected_question):
    if selected_question == "Apa metode pembayaran yang paling sering digunakan?":
        st.subheader(selected_question)
        payment_counts = order_payments['payment_type'].value_counts()
        st.bar_chart(payment_counts)

    elif selected_question == "Bagaimana distribusi harga produk?":
        st.subheader(selected_question)
        fig, ax = plt.subplots()
        sns.histplot(order_items['price'], bins=30, kde=True, color='blue', ax=ax)
        ax.set_xlabel("Harga Produk")
        ax.set_ylabel("Frekuensi")
        ax.set_title("Distribusi Harga Produk")
        st.pyplot(fig)

    elif selected_question == "Apakah harga lebih rendah menyebabkan lebih banyak pesanan?":
        st.subheader(selected_question)
        order_count = order_items.groupby('price')['order_id'].nunique()
        fig, ax = plt.subplots()
        sns.scatterplot(x=order_count.index, y=order_count.values, color='green', ax=ax)
        ax.set_xlabel("Harga Produk")
        ax.set_ylabel("Jumlah Pesanan")
        ax.set_title("Hubungan Harga Produk dan Jumlah Pesanan")
        st.pyplot(fig)

    elif selected_question == "Berapa rata-rata waktu pelanggan memberikan ulasan?":
        st.subheader(selected_question)
        order_reviews['review_creation_date'] = pd.to_datetime(order_reviews['review_creation_date'])
        order_reviews['review_answer_timestamp'] = pd.to_datetime(order_reviews['review_answer_timestamp'])
        order_reviews['response_time'] = (order_reviews['review_answer_timestamp'] - order_reviews['review_creation_date']).dt.days
        fig, ax = plt.subplots()
        sns.histplot(order_reviews['response_time'].dropna(), bins=30, kde=True, color='purple', ax=ax)
        ax.set_xlabel("Hari Setelah Pengiriman")
        ax.set_ylabel("Frekuensi")
        ax.set_title("Distribusi Waktu Respons Ulasan Pelanggan")
        st.pyplot(fig)

    elif selected_question == "Kategori produk mana yang memiliki rating tertinggi dan terendah?":
        st.subheader(selected_question)
        merged_data = order_items.merge(products, on='product_id', how='left')
        merged_data = merged_data.merge(order_reviews, on='order_id', how='left')
        avg_ratings = merged_data.groupby('product_category_name')['review_score'].mean().sort_values()
        st.bar_chart(avg_ratings)

    elif selected_question == "Bagaimana pola distribusi jumlah produk per penjual?":
        st.subheader(selected_question)
        seller_counts = order_items['seller_id'].value_counts()
        fig, ax = plt.subplots()
        sns.histplot(seller_counts, bins=30, kde=True, color='orange', ax=ax)
        ax.set_xlabel("Jumlah Produk per Penjual")
        ax.set_ylabel("Frekuensi")
        ax.set_title("Distribusi Jumlah Produk per Penjual")
        st.pyplot(fig)

    elif selected_question == "Apakah semakin banyak produk dalam pesanan meningkatkan biaya pengiriman?":
        st.subheader(selected_question)
        order_shipping = order_items.groupby("order_id").agg(
            total_items=("order_item_id", "count"),
            total_freight=("freight_value", "sum")
        ).reset_index()
        fig, ax = plt.subplots()
        sns.scatterplot(x=order_shipping['total_items'], y=order_shipping['total_freight'], color='red', ax=ax)
        ax.set_xlabel("Jumlah Produk dalam Pesanan")
        ax.set_ylabel("Total Biaya Pengiriman")
        ax.set_title("Hubungan Jumlah Produk dalam Pesanan dan Biaya Pengiriman")
        st.pyplot(fig)

# Menampilkan semua visualisasi jika memilih "Semua visualisasi"
if question == "Semua visualisasi":
    for q in questions[1:]:
        show_visualization(q)
else:
    show_visualization(question)

st.write("\n\n*Visualisasi data berdasarkan pertanyaan bisnis yang dipilih.*")