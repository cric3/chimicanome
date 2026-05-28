# ⚗️ ChimicaNome — Nomenclatore Automatico di Composti Inorganici

> **Progetto "Capolavoro" per l'Esame di Stato**  
> Algoritmo puro basato su regole chimiche · Nessuna API esterna · Python 3 + Streamlit

---

## 📱 Accesso da smartphone

Dopo il deployment su Streamlit Cloud (vedi sotto), l'app sarà accessibile
da **qualsiasi dispositivo** — smartphone, tablet, PC — tramite un semplice link.

---

## 🚀 Guida al Deployment su Streamlit Community Cloud (GRATUITO)

Streamlit Community Cloud pubblica la tua app Python come sito web pubblico,
accessibile da qualsiasi browser e dispositivo, **gratuitamente**.

### Prerequisiti
- Un account **GitHub** (gratuito su [github.com](https://github.com))
- Un account **Streamlit Cloud** (gratuito su [share.streamlit.io](https://share.streamlit.io))

---

### Passo 1 — Crea un repository GitHub

1. Vai su [github.com](https://github.com) → **New repository**
2. Nomina il repo: `chimicanome` (o come preferisci)
3. Impostalo come **Public**
4. Clicca **Create repository**

---

### Passo 2 — Carica i file nel repository

Carica questi file nella root del repository:

```
chimicanome/
├── app.py                  ← il motore dell'app
├── requirements.txt        ← le dipendenze Python
└── .streamlit/
    └── config.toml         ← tema e configurazione
```

**Metodo A — da browser (più semplice):**
1. Nella pagina del repo → **Add file** → **Upload files**
2. Trascina `app.py` e `requirements.txt`
3. Clicca **Commit changes**
4. Per `.streamlit/config.toml`: clicca **Add file** → **Create new file**,
   scrivi `.streamlit/config.toml` nel campo nome, incolla il contenuto, salva.

**Metodo B — da terminale (se hai Git installato):**
```bash
git clone https://github.com/TUO_USERNAME/chimicanome.git
cd chimicanome
cp /percorso/app.py .
cp /percorso/requirements.txt .
mkdir -p .streamlit
cp /percorso/config.toml .streamlit/
git add .
git commit -m "Prima versione ChimicaNome"
git push
```

---

### Passo 3 — Pubblica su Streamlit Cloud

1. Vai su [share.streamlit.io](https://share.streamlit.io)
2. Clicca **Sign in with GitHub** e autorizza l'accesso
3. Clicca **New app**
4. Compila i campi:
   - **Repository:** `TUO_USERNAME/chimicanome`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Clicca **Deploy!**

⏳ Il deployment richiede ~1-2 minuti.  
Al termine ricevi un link del tipo:  
`https://TUO_USERNAME-chimicanome-app.streamlit.app`

---

### Passo 4 — Condividi il link

Copia il link e condividilo con chiunque.  
L'app funziona perfettamente su **smartphone** (Chrome, Safari, Firefox mobile).

---

## 💻 Avvio in locale (sviluppo)

```bash
# 1. Installa le dipendenze (solo la prima volta)
pip install streamlit pandas

# 2. Avvia l'app
streamlit run app.py
```

L'app si apre automaticamente su `http://localhost:8501`.

Per accedere dalla stessa rete WiFi con uno smartphone:
```bash
streamlit run app.py --server.address 0.0.0.0
```
Poi sul telefono apri: `http://IP_DEL_TUO_PC:8501`
(trovi l'IP con `ipconfig` su Windows o `ifconfig` / `ip addr` su Linux/Mac)

---

## 🏗️ Struttura del Codice

```
app.py
├── SEZIONE 1 — Database Chimico
│   ├── PREFISSI_GRECI          prefissi per nomenclatura IUPAC (mono, di, tri…)
│   ├── NUMERI_ROMANI           notazione di Stock (I, II, III…)
│   ├── DATI_ELEMENTI           proprietà di ogni elemento (tipo, stati ossid., nomi)
│   ├── NOMI_OSSIACIDI          nomi degli ossiacidi per (elemento, stato ossid.)
│   ├── NOMI_ANIDRIDI           aggettivi delle anidridi
│   ├── NOMI_IDRACIDI           nomi degli idracidi binari
│   └── NOMI_ANIONI             nomi degli anioni per i sali binari
│
├── SEZIONE 2 — Parsing con Regex
│   ├── parse_formula()         parser ricorsivo con gestione parentesi
│   └── valida_formula()        controllo sintattico pre-parsing
│
├── SEZIONE 3 — Classificazione
│   ├── is_metal()              lookup tipo elemento nel database
│   └── classifica_composto()   albero logico if/elif → 6 categorie
│
├── SEZIONE 4 — Numeri di Ossidazione
│   └── calcola_ossidazione()   regole priorità + equazione Σ(ox·n)=0
│
├── SEZIONE 5 — Nomenclatura
│   ├── _nome_iupac_metallo()   notazione di Stock con numero romano
│   ├── _nome_trad_metallo()    aggettivo -oso/-ico o "di [nome]"
│   └── genera_nomenclatura()   dispatcher per tipo → regole specifiche
│
└── SEZIONE 6 — Interfaccia Streamlit
    └── main()                  UI responsive con progressive disclosure
```

---

## 🧪 Composti Supportati

| Categoria      | Esempi                              |
|---------------|-------------------------------------|
| Ossidi Basici  | Fe₂O₃, CaO, Cu₂O, MnO₂, Na₂O     |
| Anidridi       | SO₃, SO₂, CO₂, N₂O₅, P₂O₅, CO    |
| Idrossidi      | NaOH, Ca(OH)₂, Fe(OH)₂, Fe(OH)₃  |
| Idracidi       | HCl, H₂S, HBr, HI, HF             |
| Ossiacidi      | H₂SO₄, HNO₃, HClO₄, H₃PO₄, HClO |
| Sali Binari    | NaCl, FeCl₂, FeCl₃, CaF₂, Cu₂S   |

---

## ⚙️ Tecnologie

| Libreria    | Versione | Uso                                      |
|------------|----------|------------------------------------------|
| Python     | 3.10+    | Linguaggio principale                    |
| Streamlit  | 1.32+    | Framework web app                        |
| Pandas     | 2.0+     | Tabelle DataFrame nell'interfaccia       |
| `re`       | stdlib   | Regex per il parsing della formula       |

---

## 📐 Algoritmo — Descrizione Sintetica

```
Formula (stringa)
      │
      ▼  [Regex: [A-Z][a-z]?(\d*)]
  parse_formula()  →  {elemento: n_atomi}
      │
      ▼  [albero logico H/O/metallo/non-metallo]
  classifica_composto()  →  tipo  +  log ragionamento
      │
      ▼  [regole priorità + equazione Σ(ox·n)=0]
  calcola_ossidazione()  →  {elemento: num_ossidazione}
      │
      ▼  [regole IUPAC e Tradizionale per tipo]
  genera_nomenclatura()  →  (nome_iupac, nome_tradizionale)
```

---

*Nessuna API esterna. Nessun modello di linguaggio per il nome.*  
*Ogni nome è il risultato deterministico di regole chimiche codificate in Python.*
