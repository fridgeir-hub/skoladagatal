# 📚 Skóladagatal - School Calendar Viewer

Einfalt og fallegt web app til að skoða skóladagatal viku fyrir viku.

## ✨ Eiginleikar

- 📅 Sýnir skóladagatal viku fyrir viku
- 🎨 Falleg og viðkvæm hönnun (mobile-friendly)
- 🎯 Hoppar sjálfkrafa á núverandi viku
- 🏷️ Litakóðaðir viðburðir (starfsdagar, frídagar, sérstakir dagar)
- 🔄 Les **alla viðburði** beint úr PDF skjalinu

## 🚀 Uppsetning

### 1. Klóna repository

```bash
git clone https://github.com/yourusername/skoladagatal.git
cd skoladagatal
```

### 2. Setja upp Python umhverfi

```bash
pip install -r requirements.txt
```

### 3. Búa til dagatal úr PDF

```bash
python generate_calendar.py skoladagatal.pdf index.html
```

Þetta mun:
- ✅ Lesa PDF skjalið
- ✅ Draga út skólaheiti og ártal  
- ✅ **Lesa ALLA viðburði** úr dagatalinu (72 viðburðir fyrir Lundarskóla)
- ✅ Búa til vikugögn
- ✅ Framleiða `index.html` skjal sem þú getur opnað í vafra

**ENGIR harðkóðaðir hlutir** - allt er lesið beint úr PDF-inu!

## 📖 Notkun

### Opna dagatalið

Einfaldlega opnaðu `index.html` í vafra. Engin server þarf!

### Uppfæra með nýju PDF

Þegar þú færð nýtt PDF dagatal:

```bash
python generate_calendar.py nytt_dagatal.pdf index.html
```

Commitaðu og pushadu breytingunum á GitHub:

```bash
git add index.html
git commit -m "Uppfært dagatal"
git push
```

## 🌐 GitHub Pages

Til að hýsa á GitHub Pages:

1. Keyra `python generate_calendar.py dagatal.pdf index.html`
2. Commita `index.html`
3. Fara í **Settings** > **Pages**
4. Velja **main** branch og **/ (root)** folder
5. Smella á **Save**
6. Dagatalið verður aðgengilegt á: `https://yourusername.github.io/skoladagatal/`

## 📁 Skráarskipan

```
skoladagatal/
├── generate_calendar.py    # Python script til að búa til HTML
├── requirements.txt         # Python dependencies  
├── index.html              # Dagatal app (búið til sjálfkrafa)
├── skoladagatal.pdf        # PDF skjal með dagatali (þitt eigið)
└── README.md               # Þessi skrá
```

## 🔧 Hvernig það virkar

Python scriptið:
1. Opnar PDF skjalið með `pdfplumber`
2. Finnur skólaheiti (t.d. "Lundarskóli")
3. Finnur skólaár (t.d. "2025-2026")
4. Les í gegnum hverja línu í dagatalinu
5. Dregur út viðburði fyrir hvern dag og mánuð
6. Býr til 43 vikur með öllum viðburðum
7. Setur allt saman í eitt HTML skjal

**Allt er lesið úr PDF-inu** - engar harðkóðaðar upplýsingar!

## 🛠️ Fyrir hönnuði

### Breyta útliti

Allt CSS er í HTML template í `generate_calendar.py`. Þú getur breytt litum, leturgerðum, o.fl.

### Bæta við fleiri skólum

Bara keyra scriptið með nýju PDF:
```bash
python generate_calendar.py annar_skoli.pdf index.html
```

## 🤝 Framlag

Pull requests eru velkomin! Fyrir stórar breytingar, vinsamlegast opnaðu issue fyrst.

## 📝 Leyfi

MIT License - sjá LICENSE skrá fyrir nánari upplýsingar

## 👤 Höfundur

Búið til fyrir íslenska grunnskóla 🇮🇸

---

**Athugasemd:** Þetta project notar PDF skóladagatöl frá Sambandi íslenskra sveitarfélaga. Gakktu úr skugga um að þú hafir rétt til að nota PDF skjalið áður en þú hýsir það opinberlega.
