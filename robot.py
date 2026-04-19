import streamlit as st
import yfinance as yf
import pandas as pd

# LEXA TERMINAL - CORE CONFIG
st.set_page_config(page_title="LEXA TERMINAL", layout="wide")

# Şık ve Ciddi Arayüz (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    [data-testid="stMetricValue"] { font-size: 24px; color: #00ffcc !important; }
    .stTextInput input { background-color: #1a1a1a; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# Üst Başlık
st.title("📊 LEXA ANALYTICS")
st.caption("Profesyonel Hisse Senedi Analiz Motoru")

# Kullanıcı Girişi
hisse_input = st.text_input("ANALİZ EDİLECEK HİSSE KODUNU YAZIN (Örn: KRDMD, THYAO, SASA):", "KRDMD").strip().upper()

if hisse_input:
    # BIST Uyumluluğu İçin Kod Düzenleme
    ticker_code = hisse_input if hisse_input.endswith(".IS") or hisse_input == "ALTIN.S1" else f"{hisse_input}.IS"
    
    try:
        hisse = yf.Ticker(ticker_code)
        # Analiz için 1 yıllık veri çekiyoruz
        df = hisse.history(period="1y")

        if df.empty:
            st.error(f"Hata: '{hisse_input}' koduna ait veri bulunamadı. Lütfen kodu kontrol edin.")
        else:
            # --- TEKNİK HESAPLAMALAR ---
            son_fiyat = df['Close'].iloc[-1]
            onceki_kapanis = df['Close'].iloc[-2]
            yuzde_degisim = ((son_fiyat - onceki_kapanis) / onceki_kapanis) * 100
            
            # Hareketli Ortalamalar (MA20 ve MA50)
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            
            # --- PANEL 1: METRİKLER ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} TL", f"{yuzde_degisim:.2f}%")
            m2.metric("20 GÜNLÜK ORT.", f"{df['MA20'].iloc[-1]:.2f} TL")
            m3.metric("52 HAFTA YÜKSEK", f"{df['High'].max():.2f} TL")
            m4.metric("GÜNLÜK HACİM", f"{df['Volume'].iloc[-1]:,.0f}")

            st.divider()

            # --- PANEL 2: GRAFİK ---
            st.subheader(f"📈 {hisse_input} Trend Analizi")
            # Fiyat ve Ortalamaları aynı grafikte gösteriyoruz
            chart_data = df[['Close', 'MA20', 'MA50']]
            st.line_chart(chart_data)

            # --- PANEL 3: ROBOT ANALİZİ ---
            st.subheader("🤖 LEXA STRATEJİ RAPORU")
            col_a, col_b = st.columns(2)
            
            with col_a:
                # Trend Durumu
                if son_fiyat > df['MA20'].iloc[-1]:
                    st.success("BÖLGE: Pozitif (Fiyat 20 günlük ortalamanın üzerinde)")
                else:
                    st.warning("BÖLGE: Negatif (Fiyat 20 günlük ortalamanın altında)")
                
                # Altın Kesişme (Golden Cross) Kontrolü
                if df['MA20'].iloc[-1] > df['MA50'].iloc[-1]:
                    st.info("SİNYAL: Kısa vadeli trend, uzun vadeyi yukarı kesti. Güçlü görünüm.")
            
            with col_b:
                # Destek/Direnç Tahmini
                st.write(f"**Günlük Aralık:** {df['Low'].iloc[-1]:.2f} - {df['High'].iloc[-1]:.2f}")
                st.write(f"**Haftalık Değişim:** %{((son_fiyat - df['Close'].iloc[-7]) / df['Close'].iloc[-7] * 100):.2f}")

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")

# Footer
st.divider()
st.caption("LEXA Terminal | Veriler Yahoo Finance üzerinden anlık çekilmektedir.")
# --- YATIRIM TAVSİYESİ UYARISI (YENİ) ---
st.error("""
⚠️ **YASAL UYARI:** Burada yer alan yatırım bilgi, yorum ve tavsiyeleri yatırım danışmanlığı kapsamında değildir. 
Bu bilgiler sadece bilgilendirme amaçlı olup, herhangi bir yatırım aracının alım-satım önerisi olarak kabul edilmemelidir. 
Yapacağınız işlemlerden doğabilecek zararlardan kullanıcı sorumludur.
""") 
# --- YAN MENÜ: PORTFÖY GİRİŞİ ---
with st.sidebar:
    st.header("💼 PORTFÖYÜM")
    st.write("Elinizdeki hisse bilgilerini girerek kâr/zarar durumunuzu takip edin.")
    
    maliyet = st.number_input("Ortalama Maliyet (TL):", min_value=0.0, value=0.0, step=0.01)
    adet = st.number_input("Hisse Adedi:", min_value=0, value=0, step=1)
    
    if maliyet > 0 and adet > 0:
        toplam_maliyet = maliyet * adet
        guncel_deger = son_fiyat * adet
        kar_zarar_tl = guncel_deger - toplam_maliyet
        kar_zarar_oran = (kar_zarar_tl / toplam_maliyet) * 100
        
        st.divider()
        st.subheader("Durum Özeti")
        
        # Renk Belirleme
        durum_rengi = "#2ecc71" if kar_zarar_tl >= 0 else "#e74c3c"
        durum_ikonu = "📈" if kar_zarar_tl >= 0 else "📉"
        
        st.markdown(f"""
            <div style="background-color:#1a1a1a; padding:20px; border-radius:10px; border: 2px solid {durum_rengi}; text-align:center;">
                <h2 style="color:{durum_rengi}; margin:0;">{durum_ikonu} {kar_zarar_oran:.2f}%</h2>
                <p style="color:white; font-size:18px; margin:10px 0 0 0;"><b>{kar_zarar_tl:,.2f} TL</b></p>
                <small style="color:#888;">Güncel Bakiyeniz: {guncel_deger:,.2f} TL</small>
            </div>
        """, unsafe_allow_html=True)

# --- HABERLER BÖLÜMÜ ---
st.subheader("📢 Şirket Haberleri & Gelişmeler")
try:
    haberler = hisse.news
    if haberler:
        for haber in haberler[:3]: # En güncel 3 haber
            with st.container():
                st.write(f"**{haber['title']}**")
                st.caption(f"Kaynak: {haber['publisher']} | Yayımlanma: {pd.to_datetime(haber['providerPublishTime'], unit='s')}")
                st.divider()
    else:
        st.write("Şu an için güncel bir gelişme bulunamadı.")
except:
    st.write("Haberler şu an yüklenemiyor.")
