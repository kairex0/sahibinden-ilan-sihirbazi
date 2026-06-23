import streamlit as st
from google import genai
from google.genai import types  # Güvenlik filtreleri için gerekli paketi ekledik
import os

# Gemini API Anahtarını Güvenli Şekilde Alıyoruz
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

# 1. Kategori Seçimi (Eğik çizgileri temizleyerek daha stabil hale getirdik)
kategori = st.selectbox(
    "Ürünün Kategorisi Nedir?",
    ["Otomobil", "Emlak", "Arsa ve Arazi", "Elektronik ve İkinci El Eşya"]
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
            
            ÖNEMLİ NOT: Eğer kategori Emlak ise, genel konum ve mülk özelliklerini ön plana çıkar. Kesinlikle hayali adres veya hayali kişi bilgisi uydurma.

            Çıktıyı hazırlarken ŞU KURALLARA KESİNLİKLE UYMALISIN:
            1. Başlığı en üste büyük ve dikkat çekici yaz (Örn: 🔥 TERTEMİZ / 2015 MODEL... 🔥 veya 🏢 KAÇIRILMAYACAK FIRSAT DAİRE... 🏢)
            2. Bilgileri gruplandır: "✨ ÖNE ÇIKAN ÖZELLİKLER", "🛠️ MEVCUT DURUMU" ve "📝 SATICI NOTLARI" gibi kalın (bold) başlıklar kullan.
            3. Her teknik özelliği maddeler halinde (bullet points) ve başına ilgili bir emoji koyarak yaz.
            4. Asla yapay zeka tarafından yazıldığı hissettiren yapay cümleler kurma (Örn: "Bu harika fırsatı kaçırmayın" gibi klişeler yerine, "Ev alacağım için acil satılıktır, araç başında usulünce pazarlık olur" gibi samimi/esnaf dili kullan).
            5. Eğer kullanıcı hasar/boya belirtmediyse, bu kısmı listeye ekleme veya "Detaylar için iletişime geçiniz" yaz.

            Kullanıcının Seçtiği Kategori: {kategori}
            Kullanıcının Girdiği Bilgiler: {bilgiler}
            """
            
            # Gemini'ın ticari kelimelere takılıp kilitlenmesini engellemek için filtreleri gevşetiyoruz
            guvenlik_ayari = [
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
            ]
            
            try:
                # 1. DENEME: En güncel gemini-2.5-flash modeli ile dene
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        safety_settings=guvenlik_ayari
                    )
                )
                
                st.success("Tebrikler! İlanınız Başarıyla Hazırlandı 🎉")
                st.markdown(response.text)
                
                st.subheader("📋 Kopyalamak İçin Aşağıyı Kullanın:")
                st.code(response.text, language="markdown")
                
            except Exception as e:
                # Eğer sunucu yoğunluğundan dolayı (503 hatası) çökerse otomatik yedek modele geçiyoruz
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    st.warning("Ana sunucu yoğun, yedek hat üzerinden bağlanılıyor... Lütfen bekleyin.")
                    try:
                        # 2. DENEME: Yedek model (gemini-1.5-flash) ile filtreleri koruyarak tekrar dene
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                safety_settings=guvenlik_ayari
                            )
                        )
                        st.success("Tebrikler! İlanınız Yedek Sunucuyla Hazırlandı 🎉")
                        st.markdown(response.text)
                        
                        st.subheader("📋 Kopyalamak İçin Aşağıyı Kullanın:")
                        st.code(response.text, language="markdown")
                    except Exception as e2:
                        st.error(f"Yedek sunucu da şu an yoğun, lütfen birkaç saniye sonra tekrar deneyin: {e2}")
                else:
                    st.error(f"Yapay zeka yanıt verirken bir hata oluştu: {e}")