import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Налаштування сторінки
st.set_page_config(page_title="Network Session Analyzer", layout="wide")

def load_data(uploaded_file):
    """Завантаження та базова перевірка файлу."""
    try:
        df = pd.read_csv(uploaded_file)
        required_columns = ['ip_address', 'start_time', 'end_time', 'traffic_mb', 'protocol', 'status']
        
        # Перевірка наявності необхідних колонок
        if not all(col in df.columns for col in required_columns):
            st.error(f"Файл повинен містити колонки: {', '.join(required_columns)}")
            return None
        return df
    except Exception as e:
        st.error(f"Помилка при читанні файлу: {e}")
        return None

def preprocess_data(df):
    """Попередня обробка даних."""
    # Перетворення форматів часу
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    
    # Обчислення тривалості сесії в хвилинах
    df['duration_min'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60
    
    # Очищення пропущених значень
    df = df.dropna()
    return df

def show_statistics(df):
    """Відображення метрик."""
    st.subheader("📊 Основні статистичні показники")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Кількість сесій", len(df))
    with col2:
        st.metric("Унікальних IP", df['ip_address'].nunique())
    with col3:
        st.metric("Сер. тривалість (хв)", round(df['duration_min'].mean(), 2))
    with col4:
        st.metric("Сум. трафік (MB)", round(df['traffic_mb'].sum(), 2))

def detect_anomalies(df, traffic_threshold, duration_threshold):
    """Алгоритм виявлення аномальної активності."""
    st.subheader("🚨 Виявлення аномалій")
    
    # Аномалії за трафіком або тривалістю
    anomalies = df[(df['traffic_mb'] > traffic_threshold) | (df['duration_min'] > duration_threshold)]
    
    if not anomalies.empty:
        st.warning(f"Виявлено {len(anomalies)} потенційних аномалій!")
        st.write(anomalies)
    else:
        st.success("Аномалій не виявлено.")

def main():
    st.title("🛡️ Аналізатор мережевих сесій користувачів")
    st.markdown("Інтерактивний інструмент для моніторингу та аналізу мережевої активності.")

    # 1. Завантаження файлу
    uploaded_file = st.sidebar.file_uploader("Завантажте CSV-файл", type="csv")

    if uploaded_file is not None:
        raw_data = load_data(uploaded_file)
        if raw_data is not None:
            df = preprocess_data(raw_data)

            # 2. Фільтрація (Sidebar)
            st.sidebar.header("⚙️ Налаштування фільтрів")
            
            # Фільтр за протоколом
            protocols = st.sidebar.multiselect("Виберіть протоколи", 
                                               options=df['protocol'].unique(), 
                                               default=df['protocol'].unique())
            
            # Фільтр за IP
            ip_list = st.sidebar.multiselect("Пошук за IP-адресою", 
                                             options=df['ip_address'].unique())

            # Застосування фільтрів
            filtered_df = df[df['protocol'].isin(protocols)]
            if ip_list:
                filtered_df = filtered_df[filtered_df['ip_address'].isin(ip_list)]

            # 3. Відображення метрик
            show_statistics(filtered_df)

            # 4. Візуалізація
            st.subheader("📈 Візуалізація даних")
            tab1, tab2, tab3 = st.tabs(["Розподіл трафіку", "Активність за протоколами", "Тривалість сесій"])

            with tab1:
                fig1 = px.histogram(filtered_df, x="traffic_mb", nbins=20, title="Гістограма розподілу трафіку")
                st.plotly_chart(fig1, use_container_width=True)

            with tab2:
                fig2 = px.pie(filtered_df, names='protocol', title="Кругова діаграма протоколів")
                st.plotly_chart(fig2, use_container_width=True)

            with tab3:
                fig3 = px.line(filtered_df.sort_values('start_time'), x='start_time', y='duration_min', 
                               markers=True, title="Лінійний графік тривалості сесій у часі")
                st.plotly_chart(fig3, use_container_width=True)

            # 5. Аналіз аномалій (Інтерактивні слайдери)
            st.sidebar.header("⚠️ Параметри аномалій")
            t_thresh = st.sidebar.slider("Поріг трафіку (MB)", 0, 5000, 1000)
            d_thresh = st.sidebar.slider("Поріг тривалості (хв)", 0, 180, 60)
            
            detect_anomalies(filtered_df, t_thresh, d_thresh)

            # 6. Таблиця даних
            with st.expander("Переглянути повну таблицю даних"):
                st.dataframe(filtered_df)
    else:
        st.info("Будь ласка, завантажте CSV-файл у бічній панелі для початку роботи.")

if __name__ == "__main__":
    main()
