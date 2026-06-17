import streamlit as st
from google import genai

# Gemini API Anahtarını Buraya Yaz
# (Güvenlik için ileride bunu st.secrets veya environment variable yapabilirsin)
# Gemini API Anahtarını Buraya Yaz
import os
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

# Gemini İstemcisini (Client) Başlatma
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Gemini Client başlatılamadı: {e}")

# Sayfa Ayarları
st.set_page_config(page_title="Sahibinden İlan Sihirbazı", page_icon="✍️", layout="centered")

st.title("✍️ Sahibinden İlan Açıklama Sihirbazı")
st.subheader("Bilgileri girin, yapay zeka ilanınızı süsleyip hazırlasın!")

# 1. Kategori Seçimi
kategori = st.selectbox(
    "Ürünün Kategorisi Nedir?",
    ["Otomobil / Vasıta", "Konut / Emlak", "Arsa / Arazi", "İkonik / İkinci El Eşya & Elektronik"]
)

# 2. Kullanıcıdan Bilgi Alma Alanı
bilgiler = st.text_area(
    label="Ürün bilgilerini aklınıza geldiği gibi yazın:",
    placeholder="Örn: golf 2015 dizel otomatik, 120binde, sağ çamurluk boyalı, muayene yeni, ev alacağım için satılık, pazarlık var...",
    height=150
)

# 3. İlanı Oluşturma Butonu
if st.button("✨ İlan Açıklamasını Oluştur ✨"):
    if bilgiler.strip() == "":
        st.warning("Lütfen önce ürün hakkında birkaç bilgi yazın!")
    else:
        with st.spinner("Yapay zeka ilanınızı hazırlıyor, lütfen bekleyin..."):
            
            # Yapay zekaya vereceğimiz detaylı komut şablonu (Prompt)
            prompt = f"""
            Sen sahibinden.com platformunda satış rekorları kıran, emlak ve vasıta ilanları konusunda uzman profesyonel bir satış danışmanısın. 

            Görevin: Sana karmaşık, düzensiz veya kısa verilen ürün bilgilerini; alıcıyı cezbedecek, güven verecek, bol emojili ve çok düzenli bir ilan açıklamasına dönüştürmek.

            Çıktıyı hazırlarken ŞU KURALLARA KESİNLİKLE UYMALISIN:
            1. Başlığı en üste büyük ve dikkat çekici yaz (Örn: 🔥 TERTEMİZ / 2015 MODEL... 🔥)
            2. Bilgileri gruplandır: "✨ ÖNE ÇIKAN ÖZELLİKLER", "🛠️ EKSPERTİZ & DURUMU" ve "📝 SATICI NOTLARI" gibi kalın (bold) başlıklar kullan.
            3. Her teknik özelliği maddeler halinde (bullet points) ve başına ilgili bir emoji koyarak yaz.
            4. Asla yapay zeka tarafından yazıldığı hissettiren yapay cümleler kurma (Örn: "Bu harika fırsatı kaçırmayın" gibi klişeler yerine, "Ev alacağım için acil satılıktır, araç başında usulünce pazarlık olur" gibi samimi/esnaf dili kullan).
            5. Eğer kullanıcı hasar/boya belirtmediyse, bu kısmı listeye ekleme veya "Detaylar için iletişime geçiniz" yaz.

            Kullanıcının Seçtiği Kategori: {kategori}
            Kullanıcının Girdiği Bilgiler: {bilgiler}
            """
            
            try:
                # En güncel ve hızlı model olan gemini-2.5-flash modelini kullanıyoruz
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                # Başarılı sonuç ekranı
                st.success("Tebrikler! İlanınız Başarıyla Hazırlandı 🎉")
                
                # Gelen süslü metni temiz bir şekilde ekranda gösteriyoruz
                st.markdown(response.text)
                
                # Kullanıcının kopyalamasını kolaylaştırmak için bir de kod bloğu içinde veriyoruz
                st.subheader("📋 Kopyalamak İçin Aşağıyı Kullanın:")
                st.code(response.text, language="markdown")
                
            except Exception as e:
                st.error(f"Yapay zeka yanıt verirken bir hata oluştu: {e}") 