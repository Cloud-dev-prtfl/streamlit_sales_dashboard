import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from PIL import Image

# --- Set Page Configuration ---
st.set_page_config(layout='wide')

# --- Load Data ---
@st.cache_data
def load_data():
    # Create synthetic data
    np.random.seed(42)
    n_rows = 1000
    data = pd.DataFrame({
        'OrderID': range(1, n_rows + 1),
        'Date': pd.to_datetime(np.random.choice(pd.date_range('2023-01-01', '2024-12-31'), size=n_rows)),
        'Region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], size=n_rows),
        'Category': np.random.choice(['Electronics', 'Clothing', 'Home Goods', 'Books'], size=n_rows),
        'Product': [f'Product_{i}' for i in np.random.randint(1, 51, size=n_rows)],
        'Quantity': np.random.randint(1, 10, size=n_rows),
        'UnitPrice': np.random.uniform(10, 100, size=n_rows),
        'CustomerID': np.random.randint(100, 500, size=n_rows)
    })
    data['TotalPrice'] = data['Quantity'] * data['UnitPrice']
    return data

df = load_data()

# --- Sidebar ---
st.sidebar.markdown("<div style='border: 1px solid #e6e6e6; padding: 10px;'>", unsafe_allow_html=True)

# Add Company Name
## st.sidebar.markdown("<h3 style='text-align: center;'>Your Company Name</h3>", unsafe_allow_html=True)

# Add Logo
try:
    logo = Image.open("logo.png")  # Ensure 'logo.png' is in the same directory
    st.sidebar.image(logo, width=150)
except FileNotFoundError:
    st.sidebar.markdown("Logo not found")

st.sidebar.header("Sales Performance Dashboard", divider=True)

with st.sidebar.expander("Filters", expanded=True):
    regions = st.multiselect("Select Region(s):", options=df['Region'].unique(), default=df['Region'].unique())
    categories = st.multiselect("Select Category(s):", options=df['Category'].unique(), default=df['Category'].unique())

st.sidebar.markdown("</div>", unsafe_allow_html=True)

df_filtered = df[(df['Region'].isin(regions)) & (df['Category'].isin(categories))]

# --- Main Dashboard ---
st.title("Sales Performance Dashboard")
st.markdown("Analyzing sales data to gain insights.")

# --- KPIs ---
st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns([1,1,1],border=True)

total_sales = df_filtered['TotalPrice'].sum()
avg_order_value = df_filtered['TotalPrice'].mean()
total_orders = df_filtered['OrderID'].nunique()

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Average Order Value", f"${avg_order_value:,.2f}")
col3.metric("Total Orders", total_orders)

st.markdown("---")

# --- Chart Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Time Series", "Regional Analysis", "Category Analysis", "Product Analysis", "Customer Insights"])

with tab1:
    st.subheader("Sales Trends Over Time")
    daily_sales = df_filtered.groupby(df_filtered['Date'].dt.date)['TotalPrice'].sum().reset_index()
    daily_sales.rename(columns={'Date': 'Sales Date'}, inplace=True)
    fig_daily_sales = px.line(daily_sales, x='Sales Date', y='TotalPrice', title="Daily Sales Trend")
    st.plotly_chart(fig_daily_sales, use_container_width=True)

    sales_trend_category = df_filtered.groupby([df_filtered['Date'].dt.date, 'Category'])['TotalPrice'].sum().reset_index()
    sales_trend_category.rename(columns={'Date': 'Sales Date'}, inplace=True)
    fig_trend_category = px.line(sales_trend_category, x='Sales Date', y='TotalPrice', color='Category',
                                 title="Sales Trend Over Time by Category")
    st.plotly_chart(fig_trend_category, use_container_width=True)

with tab2:
    st.subheader("Regional Sales Analysis")
    col_reg1, col_reg2 = st.columns(2, border=True)
    sales_by_region = df_filtered.groupby('Region')['TotalPrice'].sum().reset_index()
    fig_region_sales = px.bar(sales_by_region, x='Region', y='TotalPrice', title="Total Sales by Region")
    col_reg1.plotly_chart(fig_region_sales, use_container_width=True)

    sales_by_category_region = df_filtered.groupby(['Category', 'Region'])['TotalPrice'].sum().reset_index()
    fig_category_region = px.bar(sales_by_category_region, x='Category', y='TotalPrice', color='Region',
                                 title="Sales by Category and Region (Grouped)")
    col_reg2.plotly_chart(fig_category_region, use_container_width=True)

with tab3:
    st.subheader("Category Sales Analysis")
    sales_by_category = df_filtered.groupby('Category')['TotalPrice'].sum().reset_index()
    fig_category_sales = px.pie(sales_by_category, names='Category', values='TotalPrice', title="Sales Share by Category", hole=0.3)
    st.plotly_chart(fig_category_sales, use_container_width=True)

    # Placeholder for another category-related chart
    st.info("More category-specific charts can be added here.")

with tab4:
    st.subheader("Product Performance Analysis")
    col_prod1, col_prod2 = st.columns(2, border=True)
    product_sales = df_filtered.groupby('Product')['TotalPrice'].sum().nlargest(10).reset_index()
    fig_product_sales = px.bar(product_sales, x='Product', y='TotalPrice', title="Top 10 Products by Total Sales")
    col_prod1.plotly_chart(fig_product_sales, use_container_width=True)

    quantity_by_product = df_filtered.groupby('Product')['Quantity'].sum().nlargest(10).reset_index()
    fig_quantity_product = px.bar(quantity_by_product, y='Product', x='Quantity', orientation='h',
                                   title="Top 10 Products by Quantity Sold")
    col_prod2.plotly_chart(fig_quantity_product, use_container_width=True)

with tab5:
    st.subheader("Customer Insights")
    col_cust1, col_cust2 = st.columns(2, border=True)
    customer_spending = df_filtered.groupby('CustomerID').agg(
        TotalSpending=('TotalPrice', 'sum'),
        OrderCount=('OrderID', 'nunique')
    ).reset_index()
    fig_customer = px.scatter(customer_spending, x='OrderCount', y='TotalSpending', title="Customer Spending vs. Order Frequency",
                              labels={'OrderCount': 'Number of Orders', 'TotalSpending': 'Total Amount Spent'})
    col_cust1.plotly_chart(fig_customer,use_container_width=True)

    fig_price_distribution = px.histogram(df_filtered, x='UnitPrice', nbins=20, title="Distribution of Unit Prices")
    col_cust2.plotly_chart(fig_price_distribution, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("Developed with Streamlit and Plotly")