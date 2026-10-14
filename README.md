# தமிழ்ப் பேச்சு ➔ உரை (Tamil Speech-to-Type & Corrector Android App)

ஆண்டிராய்டு மொபைலில் (Android Mobile) தமிழில் பேசினால், அதனை சரியான தமிழ் வார்த்தைகளுடன் நிறுத்தற்குறிகளுடன் (Punctuation) முழுமையாக உரையாக மாற்றித் தரும் Fullstack Application.

---

## 🌟 முக்கிய அம்சங்கள் (Key Features)

1. **Android Continuous Speech Recognition (`ta-IN`)**:
   - ஆண்டிராய்டு மொபைலில் நீங்கள் தமிழில் பேசப் பேச, உடனுக்குடன் தமிழ் எழுத்துக்களாக திரையில் தோன்றும்.

2. **குரல் கட்டளை நிறுத்தற்குறிகள் (Voice Punctuation Commands)**:
   - **"நிறுத்து"** / **"முற்றுப்புள்ளி"** ➔ **`.`** (முற்றுப்புள்ளி சேர்க்கப்படும்)
   - **"தொடர்"** / **"காற்புள்ளி"** ➔ **`,`** (கமா குறியீடு சேர்க்கப்படும்)
   - **"புதிய வரி"** / **"அடுத்த வரி"** ➔ **`↵`** (New Line சேர்க்கப்படும்)
   - **"கேள்விக்குறி"** ➔ **`?`**
   - **"வியப்புக்குறி"** ➔ **`!`**

3. **பேச்சுத் தமிழ் ➔ எழுத்துத் தமிழ் தானியங்கி திருத்தம்**:
   - colloquial spoken words-ஐ சரியான இலக்கண எழுத்துத் தமிழாக மாற்றுகிறது.
   - எ.கா: `வர்றேன்` ➔ `வருகிறேன்`, `போறேன்` ➔ `போகிறேன்`, `பண்றேன்` ➔ `செய்கிறேன்`.

4. **Android PWA Support**:
   - Android Mobile Chrome-இல் திறந்து **"Add to Home Screen"** அழுத்தினால் Native App போல மொபைலில் இயங்கும்.

5. **கூடுதல் வசதிகள்**:
   - 📋 **Copy**: ஒரே கிளிக்கில் உரை நகலெடுப்பு.
   - 🔊 **Listen**: தமிழ் Text-to-Speech மூலம் உரையை ஒலி வடிவில் கேட்கலாம்.
   - 📲 **WhatsApp Share**: நேரடியாக வாட்ஸ்அப்பிற்கு அனுப்பலாம்.
   - 💾 **Save & History**: பதிவுகளைச் சேமித்து வைத்துப் பின்னர் பயன்படுத்தலாம்.

---

## 🚀 இயக்கும் முறை (How to Run)

### 1. தேவையானவைகளை நிறுவுதல் (Install Dependencies)
```bash
pip install -r requirements.txt
```

### 2. சர்வரைத் தொடங்குதல் (Start FastAPI Server)
```bash
python main.py
```
அல்லது:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. ஆண்டிராய்டு மொபைலில் பயன்படுத்துவது எப்படி?
1. கணினியும் மொபைலும் ஒரே Wi-Fi பிணையத்தில் (Same Wi-Fi network) இருக்க வேண்டும்.
2. கணினியின் IP முகவரியைக் கண்டறியவும் (எ.கா: `http://192.168.1.5:8000`).
3. மொபைல் Chrome உலாவியில் அந்த முகவரியைத் திறக்கவும்.
4. மைக் அனுமதி அளித்து தமிழில் பேசத் தொடங்கவும்!

---

## 📁 கோப்பு வடிவமைப்பு (Project Structure)

```
speachtotype/
├── main.py              # FastAPI Web & API Server
├── tamil_corrector.py   # Tamil NLP & Voice Commands Engine
├── requirements.txt     # Python Dependencies
├── README.md            # App Documentation
├── static/
│   ├── index.html       # Mobile-first Tamil App UI
│   ├── app.js           # Speech Recognition & Voice Commands Logic
│   ├── style.css        # Glassmorphism Android Styling
│   ├── manifest.json    # Android PWA Installation Manifest
│   └── sw.js            # Offline Service Worker
└── android/
    └── MainActivity.kt  # Android Studio WebView Wrapper (Optional Native APK)
```
