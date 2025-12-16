# Skóladagatal - Einföld útgáfa (Ókeypis)

Íslenskt skóladagatal app sem virkar á GitHub Pages án API kostnaðar.

## 🎯 Eiginleikar

- 📅 Sýnir skóladagatal með litakóðun
- 🔄 Skipta á milli vikna
- 📱 Mobile-friendly
- 🆓 100% ókeypis - enginn backend þarf
- ⚡ Opnar sjálfkrafa á núverandi viku

## 🚀 Uppsetning (3 mínútur)

### 1. Sækja skrárnar

Þú þarft bara tvær skrár:
- `skoladagatal-simple.html` - appið
- `lundarskoli-2025-26.json` - gögnin (45 vikur)

### 2. Setja á GitHub Pages

1. Búðu til nýtt GitHub repository
2. Hladdu upp `skoladagatal-simple.html` og endurnefndu í `index.html`
3. Farðu í Settings → Pages
4. Veldu "Deploy from a branch"
5. Veldu `main` branch og `/root` folder
6. Smelltu á "Save"

Appið verður aðgengilegt á: `https://[notandanafn].github.io/[repo-nafn]`

## 📝 Hvernig á að nota

### Aðferð 1: Beint í vafranum

1. Opnaðu `skoladagatal-simple.html` í vafra
2. Smelltu á "📋 Nota sýnigögn" til að sjá dæmi
3. Eða límdu þínum eigin JSON gögnum í textareitinn
4. Smelltu á "✅ Hlaða gögnum"

### Aðferð 2: Með þínum eigin gögnum

1. Opnaðu `lundarskoli-2025-26.json` og afritaðu innihaldið
2. Límdu það í textareitinn í appinu
3. Eða breyttu gögnunum til að passa þitt skóladagatal

## 📊 JSON Format

```json
{
  "weeks": [
    {
      "weekNumber": "32",
      "dates": "4.-8. ágúst",
      "year": "2025",
      "days": [
        {
          "dayLetter": "M",
          "date": "4",
          "events": ["Frídagur verslunarmanna"],
          "color": "beige"
        },
        {
          "dayLetter": "Þ",
          "date": "5",
          "events": []
        }
      ]
    }
  ]
}
```

### Litir

- `"beige"` - Sérstakir dagar (ljósbrúnn)
- `"brown"` - Frídagar (rauðbrúnn)
- `"blue"` - Starfsdagar (blár)
- `"lightblue"` - Viðburðir (ljósblár)
- Enginn litur - Venjulegur dagur

### Dagastafir

- `M` = Mánudagur
- `Þ` = Þriðjudagur
- `M` = Miðvikudagur
- `F` = Fimmtudagur
- `F` = Föstudagur

## 🔧 Breyta fyrir þitt skóladagatal

1. Opnaðu `lundarskoli-2025-26.json`
2. Breyttu viðburðum, dagsetningum, og litum
3. Vista skrána
4. Afrita JSON innihaldið
5. Líma í appið

## 💰 Kostnaður

**$0.00** - Alveg ókeypis! 

Engin API kall, enginn backend, bara hreinn HTML/JavaScript.

## ⚙️ Fyrir forritara

Appið er einn HTML skjal með:
- Bootstrap 5 CSS
- Vanilla JavaScript
- Engar dependencies

Þú getur:
- Breytt útliti með CSS
- Bætt við fleiri eiginleikum
- Tengt við eigin backend ef þú vilt

## 🆘 Algengar spurningar

**Q: Get ég notað þetta án internetsamband?**  
A: Já! Sæktu skrárnar og opnaðu í vafra. Bootstrap CSS er eina ytri dependency.

**Q: Hvernig breyti ég litum?**  
A: Breyttu `colorMap` í JavaScript kóðanum eða breyttu `color` gildunum í JSON.

**Q: Get ég bætt við fleiri vikum?**  
A: Já! Bara bættu við fleiri week objektum í JSON gögnin.

**Q: Virkar þetta á símanum?**  
A: Já! Responsive design með Bootstrap 5.

## 📄 Leyfi

MIT - Notaðu frjálst!
