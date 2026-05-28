"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         ⚗️  ChimicaNome — Nomenclatore di Composti Inorganici              ║
║         Progetto "Capolavoro" per l'Esame di Stato                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  DESCRIZIONE:                                                               ║
║    Applicazione web interattiva che implementa un algoritmo PURO basato     ║
║    su regole logico-chimiche per assegnare automaticamente i nomi IUPAC     ║
║    e Tradizionali ai principali composti inorganici binari e ternari.       ║
║                                                                             ║
║   Python 3                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import re

# =============================================================================
# CONFIGURAZIONE PAGINA E DESIGN SYSTEM RETTIFICATO (ANTI-SOVRAPPOSIZIONE)
# =============================================================================
st.set_page_config(
    page_title="ChimicaNome — Nomenclatore Automatico",
    page_icon="⚗️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Iniezione CSS Avanzata per prevenire sovrapposizioni e adattare i box su Mobile
st.markdown("""
<style>
    .stApp { background-color: #f8f9fc; }
    
    /* Forza l'andata a capo automatica di qualsiasi testo per evitare sovrapposizioni */
    .stMarkdown, p, h1, h2, h3, span, div, .stAlert, .stExpander {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e1b4b;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4338ca;
        text-align: center;
        margin-bottom: 25px;
        font-weight: 500;
    }
    
    /* Card dei Risultati stabili e leggibili su smartphone */
    .results-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .chemical-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 6px solid #6366f1;
    }
    .card-trad { border-left-color: #10b981; }
    .card-stock { border-left-color: #f59e0b; }
    
    .card-label {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .card-value {
        font-size: 1.5rem;
        color: #111827;
        font-weight: 800;
        margin-top: 4px;
        line-height: 1.3;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# TUA MAPPA ORIGINALE COMPLETA DEI DATI CHIMICI
# =============================================================================
DATI_ELEMENTI = {
    # METALLI ALCALINI (Gruppo 1) -> Ox: +1
    "Na": {"nome": "Sodio", "tipo": "metallo", "ox_states": [1], "valenza_fissa": True},
    "K":  {"nome": "Potassio", "tipo": "metallo", "ox_states": [1], "valenza_fissa": True},
    "Ag": {"nome": "Argento", "tipo": "metallo", "ox_states": [1], "valenza_fissa": True},
    
    # METALLI ALCALINO-TERROSI (Gruppo 2) -> Ox: +2
    "Ca": {"nome": "Calcio", "tipo": "metallo", "ox_states": [2], "valenza_fissa": True},
    "Mg": {"nome": "Magnesio", "tipo": "metallo", "ox_states": [2], "valenza_fissa": True},
    "Ba": {"nome": "Bario", "tipo": "metallo", "ox_states": [2], "valenza_fissa": True},
    "Zn": {"nome": "Zinco", "tipo": "metallo", "ox_states": [2], "valenza_fissa": True},
    
    # METALLI TERROSI (Gruppo 13) -> Ox: +3
    "Al": {"nome": "Alluminio", "tipo": "metallo", "ox_states": [3], "valenza_fissa": True},
    
    # METALLI DI TRANSIZIONE (Valenze Variabili)
    "Fe": {"nome": "Ferro", "tipo": "metallo", "ox_states": [2, 3], "valenza_fissa": False, "tradizionale": {2: "ferroso", 3: "ferrico"}},
    "Cu": {"nome": "Rame", "tipo": "metallo", "ox_states": [1, 2], "valenza_fissa": False, "tradizionale": {1: "rameoso", 2: "rameico"}},
    "Hg": {"nome": "Mercurio", "tipo": "metallo", "ox_states": [1, 2], "valenza_fissa": False, "tradizionale": {1: "mercurioso", 2: "mercurico"}},
    "Pb": {"nome": "Piombo", "tipo": "metallo", "ox_states": [2, 4], "valenza_fissa": False, "tradizionale": {2: "piomboso", 4: "piombico"}},
    "Sn": {"nome": "Stagno", "tipo": "metallo", "ox_states": [2, 4], "valenza_fissa": False, "tradizionale": {2: "stagnoso", 4: "stagnico"}},
    "Cr": {"nome": "Cromo", "tipo": "metallo", "ox_states": [2, 3, 6], "valenza_fissa": False, "tradizionale": {2: "cromoso", 3: "cromico", 6: "cromico"}},
    "Mn": {"nome": "Manganese", "tipo": "metallo", "ox_states": [2, 3, 4, 6, 7], "valenza_fissa": False, "tradizionale": {2: "manganoso", 3: "manganico"}},
    
    # NON METALLI DI RIFERIMENTO COSTRUTTIVO
    "H":  {"nome": "Idrogeno", "tipo": "non-metallo", "ox_states": [1, -1], "valenza_fissa": False},
    "O":  {"nome": "Ossigeno", "tipo": "non-metallo", "ox_states": [-2], "valenza_fissa": True},
    
    # ALOGENI (Gruppo 17) -> Ox negativo nei sali/idracidi: -1
    "F":  {"nome": "Fluoro", "tipo": "non-metallo", "ox_states": [-1], "valenza_fissa": True, "radice": "fluor", "anione_ox": -1},
    "Cl": {"nome": "Cloro", "tipo": "non-metallo", "ox_states": [-1, 1, 3, 5, 7], "valenza_fissa": False, "tradizionale": {1: "ipoclorosa", 3: "clorosa", 5: "clorica", 7: "perclorica"}, "radice": "clor", "anione_ox": -1},
    "Br": {"nome": "Bromo", "tipo": "non-metallo", "ox_states": [-1, 1, 3, 5, 7], "valenza_fissa": False, "tradizionale": {1: "ipobromosa", 3: "bromosa", 5: "bromica", 7: "perbromica"}, "radice": "brom", "anione_ox": -1},
    "I":  {"nome": "Iodio", "tipo": "non-metallo", "ox_states": [-1, 1, 3, 5, 7], "valenza_fissa": False, "tradizionale": {1: "ipoiodosa", 3: "iodosa", 5: "iodica", 7: "periodica"}, "radice": "iod", "anione_ox": -1},
    
    # CALCOGENI (Gruppo 16) -> Ox negativo nei sali/idracidi: -2
    "S":  {"nome": "Zolfo", "tipo": "non-metallo", "ox_states": [-2, 4, 6], "valenza_fissa": False, "tradizionale": {4: "solforosa", 6: "solforica"}, "radice": "solf", "anione_ox": -2},
    
    # GRUPPO AZOTO (Gruppo 15)
    "N":  {"nome": "Azoto", "tipo": "non-metallo", "ox_states": [-3, 3, 5], "valenza_fissa": False, "tradizionale": {3: "nitroso", 5: "nitrico"}, "radice": "nitr", "anione_ox": -3},
    "P":  {"nome": "Fosforo", "tipo": "non-metallo", "ox_states": [-3, 3, 5], "valenza_fissa": False, "tradizionale": {3: "fosforoso", 5: "fosforico"}, "radice": "fosfor", "anione_ox": -3},
    
    # GRUPPO CARBONIO (Gruppo 14)
    "C":  {"nome": "Carbonio", "tipo": "non-metallo", "ox_states": [-4, 2, 4], "valenza_fissa": False, "tradizionale": {2: "carboniosa", 4: "carbonica"}, "radice": "carbon", "anione_ox": -4},
    "Si": {"nome": "Silicio", "tipo": "non-metallo", "ox_states": [4], "valenza_fissa": True, "tradizionale": {4: "silicica"}, "radice": "silic"},
    
    # GRUPPO BORO (Gruppo 13)
    "B":  {"nome": "Boro", "tipo": "non-metallo", "ox_states": [3], "valenza_fissa": True, "tradizionale": {3: "borica"}, "radice": "bor"}
}

PREFISSI_IUPAC = {1: "mono", 2: "di", 3: "tri", 4: "tetra", 5: "penta", 6: "esa", 7: "epta"}
NUMERI_ROMANI = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}

# =============================================================================
# FUNZIONI CORE DELL'ALGORITMO CHIMICO REALE
# =============================================================================
def parse_formula(formula: str, log_list: list) -> list:
    log_list.append("📌 **Fase 1: Analisi della stringa molecolare (Lexing/Parsing Regex)**")
    pattern = r"([A-Z][a-z]*)(\d*)"
    matches = re.findall(pattern, formula)
    if not matches:
        log_list.append("❌ Errore: La stringa immessa non corrisponde a un pattern molecolare valido.")
        return None
        
    elementi = []
    for el, ind in matches:
        if el not in DATI_ELEMENTI:
            log_list.append(f"❌ Errore: L'elemento **{el}** non è censito nel database dell'applicazione.")
            return None
        q = int(ind) if ind else 1
        elementi.append((el, q))
        log_list.append(f" - Rilevato simbolo chimico: **{el}** con indice stechiometrico = {q}")
    return elementi

def classifica_composto(elementi: list, formula_str: str, log_list: list) -> str:
    log_list.append("📌 **Fase 2: Classificazione strutturale della specie chimica**")
    if formula_str in ["H2O", "H2O1"]:
        return "acqua"
        
    if len(elementi) == 2:
        el1, _ = elementi[0]
        el2, _ = elementi[1]
        
        if el2 == "O":
            if DATI_ELEMENTI[el1]["tipo"] == "metallo":
                log_list.append(f" - Accoppiamento Metallo ({el1}) + Ossigeno. Classe: **Ossido Basico**.")
                return "ossido_basico"
            else:
                log_list.append(f" - Accoppiamento Non-metallo ({el1}) + Ossigeno. Classe: **Anidride (Ossido Acido)**.")
                return "anidride"
        if el1 == "H" and DATI_ELEMENTI[el2]["tipo"] == "non-metallo":
            if el2 in ["F", "Cl", "Br", "I", "S"]:
                log_list.append(f" - Accoppiamento Idrogeno + Alogeno/Calcogeno ({el2}). Classe: **Idracido**.")
                return "idracido"
        if DATI_ELEMENTI[el1]["tipo"] == "metallo" and DATI_ELEMENTI[el2]["tipo"] == "non-metallo":
            log_list.append(f" - Accoppiamento Metallo ({el1}) + Non-metallo ({el2}). Classe: **Sale Binario**.")
            return "sale_binario"
            
    elif len(elementi) == 3:
        el1, _ = elementi[0]
        el2, _ = elementi[1]
        el3, _ = elementi[2]
        if el1 == "H" and el3 == "O":
            log_list.append(f" - Struttura ternaria H + Non-metallo ({el2}) + O. Classe: **Ossiacido**.")
            return "ossiacido"
            
    log_list.append("❌ Classe di composto non identificata o non supportata dall'albero decisionale.")
    return "non_supportato"

def calcola_stati_ossidazione(tipo: str, elementi: list, log_list: list) -> dict:
    log_list.append("📌 **Fase 3: Risoluzione del sistema lineare delle cariche (Elettroneutralità)**")
    ox_map = {}
    
    if tipo == "acqua":
        return {"H": 1, "O": -2}
        
    if tipo == "idracido":
        el1, _ = elementi[0]
        el2, _ = elementi[1]
        ox_map[el1] = 1
        ox_map[el2] = -2 if el2 == "S" else -1
        log_list.append(f" - Regola idracidi fissa: {el1} = +1, di conseguenza {el2} = {ox_map[el2]}")
        return ox_map

    # --- CORREZIONE REALE PER I SALI BINARI (Risolve Cu2S) ---
    if tipo == "sale_binario":
        m_el, m_q = elementi[0]
        nm_el, nm_q = elementi[1]
        
        # L'anione (destra) nei sali binari prende sempre il suo stato negativo stabile fisso
        nm_ox = DATI_ELEMENTI[nm_el].get("anione_ox", -1)
        ox_map[nm_el] = nm_ox
        log_list.append(f" - Regola Anione: Il non-metallo a destra '{nm_el}' assume stato d'ossidazione negativo fisso = {nm_ox}")
        
        # Equazione: (m_q * X) + (nm_q * nm_ox) = 0  => X = -(nm_q * nm_ox) / m_q
        carica_negativa_totale = nm_q * nm_ox
        if (-carica_negativa_totale) % m_q == 0:
            ox_map[m_el] = int(-carica_negativa_totale / m_q)
            log_list.append(f" - Equazione risolta per il metallo '{m_el}': ({m_q} * X) + ({carica_negativa_totale}) = 0 ➔ X = +{ox_map[m_el]}")
            return ox_map
        return None

    if tipo in ["ossido_basico", "anidride"]:
        el1, q1 = elementi[0]
        el2, q2 = elementi[1]
        ox_map[el2] = -2
        log_list.append(" - Regola Ossigeno fissa: O = -2")
        if (2 * q2) % q1 == 0:
            ox_map[el1] = int((2 * q2) / q1)
            log_list.append(f" - Equazione bilancio: ({q1} * X) + ({q2} * -2) = 0 ➔ {el1} = +{ox_map[el1]}")
            return ox_map
        return None

    if tipo == "ossiacido":
        h_el, h_q = elementi[0]
        nm_el, nm_q = elementi[1]
        o_el, o_q = elementi[2]
        ox_map[h_el] = 1
        ox_map[o_el] = -2
        log_list.append(" - Regole fisse assegnate: H = +1, O = -2")
        
        lato_positivo = h_q * 1
        lato_negativo = o_q * (-2)
        differenza = -(lato_positivo + lato_negativo)
        
        if differenza % nm_q == 0:
            ox_map[nm_el] = int(differenza / nm_q)
            log_list.append(f" - Bilancio atomo centrale '{nm_el}': ({h_q}*1) + ({nm_q}*X) + ({o_q}*-2) = 0 ➔ X = +{ox_map[nm_el]}")
            return ox_map
        return None

    return None

def genera_nomi_completi(tipo: str, elementi: list, ox: dict) -> dict:
    res = {"iupac": "", "tradizionale": "", "stock": ""}
    
    if tipo == "acqua":
        return {"iupac": "Ossido di diidrogeno", "tradizionale": "Acqua", "stock": "Ossido di idrogeno"}

    if tipo in ["ossido_basico", "anidride"]:
        el1, q1 = elementi[0]
        q2 = elementi[1][1]
        ox_val = ox[el1]
        
        # IUPAC
        p_o = PREFISSI_IUPAC.get(q2, "")
        p_m = f"di {PREFISSI_IUPAC.get(q1, '')}" if q1 > 1 else "di "
        base = "ossido" if p_o == "mono" else f"{p_o}ossido"
        if base.endswith("ao"): base = base.replace("ao", "o")
        res["iupac"] = f"{base.capitalize()} {p_m}{DATI_ELEMENTI[el1]['nome'].lower()}".strip()
        
        # STOCK
        res["stock"] = f"Ossido di {DATI_ELEMENTI[el1]['nome'].lower()} ({NUMERI_ROMANI.get(ox_val, str(ox_val))})"
        
        # TRADIZIONALE
        if tipo == "ossido_basico":
            if DATI_ELEMENTI[el1]["valenza_fissa"]:
                res["tradizionale"] = f"Ossido di {DATI_ELEMENTI[el1]['nome'].lower()}"
            else:
                suff = DATI_ELEMENTI[el1]["tradizionale"].get(ox_val, "")
                res["tradizionale"] = f"Ossido {suff}"
        else: # Anidride
            if DATI_ELEMENTI[el1]["valenza_fissa"]:
                res["tradizionale"] = f"Anidride {DATI_ELEMENTI[el1]['tradizionale'].get(ox_val, DATI_ELEMENTI[el1]['nome'].lower() + 'ica')}"
            else:
                suff = DATI_ELEMENTI[el1]["tradizionale"].get(ox_val, "")
                res["tradizionale"] = f"Anidride {suff}"

    elif tipo == "idracido":
        q1 = elementi[0][1]
        el2 = elementi[1][0]
        rad = DATI_ELEMENTI[el2]["radice"]
        res["iupac"] = f"{rad.capitalize()}uro di {PREFISSI_IUPAC.get(q1, '')}idrogeno".strip()
        res["tradizionale"] = f"Acido {rad}idrico"
        res["stock"] = res["iupac"]

    elif tipo == "sale_binario":
        m_el, m_q = elementi[0]
        nm_el, nm_q = elementi[1]
        ox_m = ox[m_el]
        rad = DATI_ELEMENTI[nm_el]["radice"]
        
        res["iupac"] = f"{PREFISSI_IUPAC.get(nm_q, '')}{rad}uro di {PREFISSI_IUPAC.get(m_q, '')}{DATI_ELEMENTI[m_el]['nome'].lower()}".replace("di mono", "di ").strip()
        res["stock"] = f"{rad.capitalize()}uro di {DATI_ELEMENTI[m_el]['nome'].lower()} ({NUMERI_ROMANI.get(ox_m, str(ox_m))})"
        
        if DATI_ELEMENTI[m_el]["valenza_fissa"]:
            res["tradizionale"] = f"{rad.capitalize()}uro di {DATI_ELEMENTI[m_el]['nome'].lower()}"
        else:
            suff = DATI_ELEMENTI[m_el]["tradizionale"].get(ox_m, "")
            if suff.endswith("ica"): suff = suff[:-3] + "ico"
            if suff.endswith("osa"): suff = suff[:-3] + "oso"
            res["tradizionale"] = f"{rad.capitalize()}uro {suff}"

    elif tipo == "ossiacido":
        nm_el = elementi[1][0]
        q3 = elementi[2][1]
        ox_nm = ox[nm_el]
        rad = DATI_ELEMENTI[nm_el]["radice"]
        
        res["iupac"] = f"Acido {PREFISSI_IUPAC.get(q3, '')}osso{rad}ico".lower().capitalize()
        res["stock"] = f"Acido {PREFISSI_IUPAC.get(q3, '')}osso{rad}ico ({NUMERI_ROMANI.get(ox_nm, str(ox_nm))})".lower().capitalize()
        suff = DATI_ELEMENTI[nm_el]["tradizionale"].get(ox_nm, "ossiacido")
        res["tradizionale"] = f"Acido {suff}"

    return res

def gestisci_idrossidi(formula: str) -> dict:
    pattern = r"([A-Z][a-z]*)\(OH\)(\d+)|([A-Z][a-z]*)OH"
    match = re.match(pattern, formula)
    if not match:
        return None
    g1, g2, g3 = match.groups()
    metallo = g3 if g3 else g1
    carica = 1 if g3 else int(g2)
    
    if metallo not in DATI_ELEMENTI:
        return None
        
    pref = PREFISSI_IUPAC.get(carica, "")
    iupac = f"{pref}idrossido di {DATI_ELEMENTI[metallo]['nome'].lower()}".replace("monoidrossido", "idrossido").strip()
    stock = f"Idrossido di {DATI_ELEMENTI[metallo]['nome'].lower()} ({NUMERI_ROMANI.get(carica, str(carica))})"
    
    if DATI_ELEMENTI[metallo]["valenza_fissa"]:
        trad = f"Idrossido di {DATI_ELEMENTI[metallo]['nome'].lower()}"
    else:
        suff = DATI_ELEMENTI[metallo]["tradizionale"].get(carica, "")
        if suff.endswith("ica"): suff = suff[:-3] + "ico"
        if suff.endswith("osa"): suff = suff[:-3] + "oso"
        trad = f"Idrossido {suff}"
        
    return {"iupac": iupac, "tradizionale": trad, "stock": stock, "metallo": metallo, "carica": carica}

# =============================================================================
# INTERFACCIA STREAMLIT COERENTE E AGGIORNATA AD ATTIVAZIONE ISTANTANEA
# =============================================================================
st.markdown('<div class="main-title">⚗️ ChimicaNome</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Nomenclatore Inorganico Digitale per l\'Esame di Stato</div>', unsafe_allow_html=True)

# 1. Inizializzazione stabile della chiave del widget nel session_state
if "casella_formula" not in st.session_state:
    st.session_state.casella_formula = ""

# 2. Callback strategica: Scatta istantaneamente appena tocchi un esempio dalla lista
def applica_esempio_rapido():
    if st.session_state.esempio_scelto != "Scegli un composto di esempio...":
        # Estrae la formula pura prima dello spazio (es. "Cu2S") e la inietta nel text_input
        st.session_state.casella_formula = st.session_state.esempio_scelto.split(" ")[0]

# 3. Selectbox salvaspazio legata alla funzione di attivazione
st.selectbox(
    "🔬 Seleziona una formula rapida per il test istantaneo:",
    [
        "Scegli un composto di esempio...",
        "Cu2S (Solfuro Rameoso)",
        "Fe2O3 (Ossido Ferrico)",
        "HCl (Acido Cloridrico)",
        "H2SO4 (Acido Solforico)",
        "NaOH (Idrossido di Sodio)",
        "CO2 (Anidride Carbonica)",
        "H2O (Acqua)"
    ],
    key="esempio_scelto",
    on_change=applica_esempio_rapido
)

# 4. Campo di testo agganciato alla chiave globale del session state
formula_utente = st.text_input(
    "Formula Chimica Molecolare:",
    key="casella_formula",
    placeholder="Es: Cu2S, Fe2O3, HCl, H2SO4..."
)

# Esecuzione automatica se la stringa è presente (per caricamento da selectbox o click invio)
if formula_utente:
    formula_pulita = formula_utente.strip().replace(" ", "")
    log_totali = ["Inizializzazione modulo chimico."]
    
    # Controllo se si tratta di un idrossido ternario
    idrossido_data = gestisci_idrossidi(formula_pulita)
    
    if idrossido_data:
        st.success("Analisi Molecolare Terminata!")
        
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="chemical-card"><div class="card-label">Nomenclatura IUPAC</div><div class="card-value">{idrossido_data["iupac"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chemical-card card-trad"><div class="card-label">Nomenclatura Tradizionale</div><div class="card-value">{idrossido_data["tradizionale"]}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chemical-card card-stock"><div class="card-label">Notazione di Stock</div><div class="card-value">{idrossido_data["stock"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("🔍 Mostra tutti i passaggi logici e i dati dell'algoritmo", expanded=False):
            st.write("- **Fase 1: Parsing molecolare:** Rilevato gruppo funzionale ossidrilico poliatomico `(OH)` tramite espressione regolare dedicata.")
            st.write(f"- **Fase 2: Classificazione:** Identificato come **Idrossido Ternario**.")
            st.write(f"- **Fase 3: Calcolo delle Cariche:** Il gruppo `OH` ha carica complessiva fissa pari a `-1`. Essendoci {idrossido_data['carica']} gruppi, la carica bilanciata del metallo centrale (**{DATI_ELEMENTI[idrossido_data['metallo']]['nome']}**) è pari a **+{idrossido_data['carica']}**.")
            
    else:
        # Analisi ordinaria binari e ternari
        elementi_correnti = parse_formula(formula_pulita, log_totali)
        
        if elementi_correnti:
            tipo_composto = classifica_composto(elementi_correnti, formula_pulita, log_totali)
            
            if tipo_composto != "non_supportato":
                ox_calcolati = calcola_stati_ossidazione(tipo_composto, elementi_correnti, log_totali)
                
                if ox_calcolati:
                    nomi = genera_nomi_completi(tipo_composto, elementi_correnti, ox_calcolati)
                    st.success("Analisi Molecolare Terminata!")
                    
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.markdown(f'<div class="chemical-card"><div class="card-label">Nomenclatura IUPAC</div><div class="card-value">{nomi["iupac"]}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="chemical-card card-trad"><div class="card-label">Nomenclatura Tradizionale</div><div class="card-value">{nomi["tradizionale"]}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="chemical-card card-stock"><div class="card-label">Notazione di Stock</div><div class="card-value">{nomi["stock"]}</div></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # RIPRISTINO INTEGRALE DI TUTTI I PASSAGGI DIDATTICI RICHIESTI
                    with st.expander("🔍 Mostra tutti i passaggi logici e i dati dell'algoritmo", expanded=False):
                        st.subheader("Registro analitico delle operazioni:")
                        for riga_log in log_totali:
                            st.write(riga_log)
                            
                        st.subheader("Matrice vettoriale degli Stati di Ossidazione:")
                        tabella_vettori = {
                            "Elemento Chimico": [el for el, _ in elementi_correnti],
                            "Atomi nella formula": [q for _, q in elementi_correnti],
                            "Stato di Ossidazione Calcolato": [ox_calcolati[el] for el, _ in elementi_correnti]
                        }
                        st.dataframe(pd.DataFrame(tabella_vettori), hide_index=True, use_container_width=True)
                        st.info(f"💡 **Inquadramento Didattico:** La molecola analizzata fa parte della famiglia degli **{tipo_composto.replace('_', ' ').capitalize()}**. L'algoritmo ha verificato che la sommatoria del prodotto tra gli indici molecolari e gli stati di ossidazione sia pari a 0.")
                else:
                    st.error("⚠️ Impossibile bilanciare matematicamente le cariche elettroniche della molecola inserita con gli stati memorizzati.")
            else:
                st.error("⚠️ Classe funzionale della molecola non supportata dai nostri alberi logici strutturali.")
        else:
            st.error("⚠️ Errore di sintassi chimica. Verifica i simboli (Attenzione alle maiuscole: es. Cu2S e non cu2s).")

# =============================================================================
# RIPRISTINO COMPLETO DEL TUO COMODO BLOCCO DI CURIOSITÀ CHIMICA
# =============================================================================
if formula_utente:
    formula_pulita = formula_utente.strip().replace(" ", "")
    elementi_correnti = parse_formula(formula_pulita, [])
    if elementi_correnti:
        tipo = classifica_composto(elementi_correnti, formula_pulita, [])
        
        CURIOSITA = {
            'ossido_basico': ("💡 Lo sapevi?", "Gli **ossidi basici** si formano per reazione diretta tra un metallo e l'ossigeno. Molti di essi, a contatto con l'acqua, reagiscono vigorosamente per formare le rispettive basi o idrossidi (es. CaO + H2O ➔ Ca(OH)2, nota come calce spenta)."),
            'anidride': ("💡 Lo sapevi?", "Le **anidridi** (o ossidi acidi) prendono il nome dal fatto che, combinandosi con l'acqua, generano i rispettivi ossiacidi. Ad esempio, l'anidride carbonica (CO2) reagisce con l'acqua piovana formando acido carbonico, responsabile della naturale, seppur debole, acidità delle piogge."),
            'idracido': ("💡 Lo sapevi?", "Gli **idracidi** sono composti binari in cui l'idrogeno è legato a un non-metallo altamente elettronegativo. A differenza degli ossiacidi, non contengono ossigeno. Il più famoso è l'acido cloridrico (HCl), che è il componente principale dei nostri succhi gastrici."),
            'ossiacido': ("💡 Lo sapevi?", "Gli **ossiacidi** contengono ossigeno e sono generalmente più forti degli idracidi. L'acido solforico (H2SO4) è il prodotto chimico industriale più prodotto al mondo: oltre 250 milioni di tonnellate all'anno, usato in fertilizzanti, batterie e raffinazione."),
            'sale_binario': ("💡 Lo sapevi?", "I **sali binari** sono composti ionici formati da un reticolo geometrico ordinato di cationi e anioni. Il cloruro di sodio (NaCl, il comune sale da cucina) ne è l'esempio più celebre: la sua struttura cubica a facce centrate è uno dei modelli cristallini più studiati nella chimica dello stato solido."),
            'acqua': ("💡 Lo sapevi?", "L'**acqua (H2O)** ha proprietà così uniche e anomale da essere quasi classificata come un caso a parte. L'angolo di legame di 104.5° e il forte dipolo molecolare spiegano l'elevata tensione superficiale, il calore specifico altissimo e la densità anomala del ghiaccio, caratteristiche che rendono possibile la vita sulla Terra.")
        }
        
        if tipo in CURIOSITA:
            titolo, testo = CURIOSITA[tipo]
            st.markdown("---")
            with st.expander(titolo, expanded=True):
                st.write(testo)
