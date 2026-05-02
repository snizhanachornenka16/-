import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# ФУНКЦІЇ
# -----------------------------

def load_data(file):
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        st.error(f"Помилка завантаження файлу: {e}")
        return None


def preprocess_data(df):
    try:
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])

        # Тривалість сесії (в секундах)
        df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds()

        # Видалення пропущених значень
        df = df.dropna()

        return df
    except Exception as e:
        st.error(f"Помилка обробки даних: {e}")
        return None


def calculate_stats(df):
    stats = {
        "Кількість сесій": len(df),
        "Середня тривалість (сек)": df['duration'].mean(),
        "Сумарний трафік (MB)": df['data_volume'].sum(),
        "Унікальні IP": df['ip'].nunique()
    }
    return stats


def detect_anomalies(df):
    anomalies = df[
        (df['duration'] > df['duration'].mean() * 3) |
        (df['data_volume'] > df['data_volume'].mean() * 3)
    ]
    return anomalies


# -----------------------------
# ІНТЕРФЕЙС STREAMLIT
# -----------------------------

st.title("Аналіз мережевих сесій користувачів")

uploaded_file = st.file_uploader("Завантаж CSV файл", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        df = preprocess_data(df)

        if df is not None:

            # -----------------------------
            # ФІЛЬТРИ
            # -----------------------------
            st.sidebar.header("Фільтри")

            ip_filter = st.sidebar.multiselect("IP адреса", df['ip'].unique())
            protocol_filter = st.sidebar.multiselect("Протокол", df['protocol'].unique())

            if ip_filter:
                df = df[df['ip'].isin(ip_filter)]

            if protocol_filter:
                df = df[df['protocol'].isin(protocol_filter)]

            # -----------------------------
            # СТАТИСТИКА
            # -----------------------------
            st.header("Статистика")

            stats = calculate_stats(df)

            for key, value in stats.items():
                st.write(f"{key}: {value}")

            # -----------------------------
            # ВІЗУАЛІЗАЦІЯ
            # -----------------------------
            st.header("Візуалізація")

            fig1 = px.histogram(df, x="duration", title="Розподіл тривалості сесій")
            st.plotly_chart(fig1)

            fig2 = px.line(df.sort_values("start_time"),
                           x="start_time",
                           y="data_volume",
                           title="Трафік у часі")
            st.plotly_chart(fig2)

            fig3 = px.pie(df, names="protocol", title="Розподіл протоколів")
            st.plotly_chart(fig3)

            # -----------------------------
            # АНОМАЛІЇ
            # -----------------------------
            st.header("Аномальна активність")

            anomalies = detect_anomalies(df)

            if not anomalies.empty:
                st.write("Виявлено підозрілі сесії:")
                st.dataframe(anomalies)
            else:
                st.write("Аномалій не виявлено")