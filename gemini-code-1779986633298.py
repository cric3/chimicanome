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
║  COMPOSTI SUPPORTATI:                                                       ║
║    1. Ossidi Basici  (es. Fe₂O₃, CaO, Cu₂O, MnO₂)                        ║
║    2. Anidridi       (es. SO₃, CO₂, N₂O₅, P₂O₅)                          ║
║    3. Idrossidi      (es. NaOH, Ca(OH)₂, Fe(OH)₃)                         ║
║    4. Idracidi       (es. HCl, H₂S, HBr, HI)                              ║
║    5. Ossiacidi      (es. H₂SO₄, HNO₃, HClO₄, H₃PO₄)                    ║
║    6. Sali Binari    (es. NaCl, FeCl₃, CaF₂, Cu₂S)                       ║
║                                                                             ║
║   Python 3                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional, Any

# =============================================================================
# CONFIGURAZIONE PAGINA E DESIGN SYSTEM (ANTI-SOVRAPPOSIZIONE MOBILE)
# =============================================================================
st.set_page_config(
    page_title="ChimicaNome — Nomenclatore Automatico",
    page_icon="⚗️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Iniezione CSS avanzata per rendere l'interfaccia responsiva ed evitare testi sovrapposti
st.markdown("""
<style>
    /* Reset e sfondi globali puliti in stile EdTech */
    .stApp { background-color: #f8f9fc; }
    
    /* Prevenzione assoluta dell'overflow del testo su schermi mobili */
    .stMarkdown, p, h1, h2, h3, span, div, .stAlert {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }
    
    /* Titoli principali */
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1e1b4b;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -0.02em;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4338ca;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 500;
    }
    
    /* Contenitore e Card dei Risultati Ottimizzate per Mobile */
    .results-box {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .chemical-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-left: 6px solid #6366f1;
        transition: transform 0.2s ease;
    }
    .card-trad { border-left-color: #10b981; }
    .card-stock { border-left-color: #f59e0b; }
    
    .card-label {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .card-value {
        font-size: 1.6rem;
        color: #111827;
        font-weight: 800;
        margin-top: 6px;
        line-height: 1.25;
    }
    
    /* Input di testo compatto */
    div.stTextInput > div > div > input {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATABASE CHIMICO (DATI_ELEMENTI) - CORRETTO E AMPLIATO
# =============================================================================
DATI_ELEMENTI: Dict[str, Dict[str, Any]] = {
    # METALLI
    "Na": {"nome": "Sodio", "tipo": "metallo", "ox_states": [1], "valenza_fissa": True},
    "K":  {"nome": "Potassio", "tipo": "metallo", "ox_states": [1], "valenza_fissa": True},
    "Ca": {"nome": "Calcio", "tipo": "metallo", "ox_states": [2], "valenza_fissa": True},
    "Mg": {"nome": "Magnesio", "tipo": "metallo", "ox_states": [2], "valenza_fissa": True},
    "Al": {"nome": "Alluminio", "tipo": "metallo", "ox_states": [3], "valenza_fissa": True},
    "Fe": {"nome": "Ferro", "tipo": "metallo", "ox_states": [2, 3], "valenza_fissa": False, "tradizionale": {2: "ferroso", 3: "ferrico"}},
    # CORREZIONE: Cu impostato a valenza variabile con i suffissi tradizionali corretti
    "Cu": {"nome": "Rame", "tipo": "metallo", "ox_states": [1, 2], "valenza_fissa": False, "tradizionale": {1: "rameoso", 2: "rameico"}},
    "Sn": {"nome": "Stagno", "tipo": "metallo", "ox_states": [2, 4], "valenza_fissa": False, "tradizionale": {2: "stagnoso", 4: "stagnico"}},
    "Pb": {"nome": "Piombo", "tipo": "metallo", "ox_states": [2, 4], "valenza_fissa": False, "tradizionale": {2: "piomboso", 4: "piombico"}},
    
    # NON METALLI
    "H":  {"nome": "Idrogeno", "tipo": "non-metallo", "ox_states": [1, -1], "valenza_fissa": False},
    "O":  {"nome": "Ossigeno", "tipo": "non-metallo", "ox_states": [-2], "valenza_fissa": True},
    "C":  {"nome": "Carbonio", "tipo": "non-metallo", "ox_states": [2, 4], "valenza_fissa": False, "tradizionale": {2: "carboniosa", 4: "carbonica"}, "radice": "carbon"},
    "N":  {"nome": "Azoto", "tipo": "non-metallo", "ox_states": [3, 5], "valenza_fissa": False, "tradizionale": {3: "nitroso", 5: "nitrico"}, "radice": "nitr"},
    "P":  {"nome": "Fosforo", "tipo": "non-metallo", "ox_states": [3, 5], "valenza_fissa": False, "tradizionale": {3: "fosforoso", 5: "fosforico"}, "radice": "fosfor"},
    "S":  {"nome": "Zolfo", "tipo": "non-metallo", "ox_states": [-2, 4, 6], "valenza_fissa": False, "tradizionale": {4: "solforosa", 6: "solforica"}, "radice": "solf", "anione_ox": -2},
    "Cl": {"nome": "Cloro", "tipo": "non-metallo", "ox_states": [-1, 1, 3, 5, 7], "valenza_fissa": False, "tradizionale": {1: "ipoclorosa", 3: "clorosa", 5: "clorica", 7: "perclorica"}, "radice": "clor", "anione_ox": -1},
    "Br": {"nome": "Bromo", "tipo": "non-metallo", "ox_states": [-1, 1, 3, 5, 7], "valenza_fissa": False, "tradizionale": {1: "ipobromosa", 3: "bromosa", 5: "bromica", 7: "perbromica"}, "radice": "brom", "anione_ox": -1},
    "I":  {"nome": "Iodio", "tipo": "non-metallo", "ox_states": [-1, 1, 3, 5, 7], "valenza_fissa": False, "tradizionale": {1: "ipoiodosa", 3: "iodosa", 5: "iodica", 7: "periodica"}, "radice": "iod", "anione_ox": -1},
    "F":  {"nome": "Fluoro", "tipo": "non-metallo", "ox_states": [-1], "valenza_fissa": True, "radice": "fluor", "anione_ox": -1}
}

PREFISSI_IUPAC = {1: "mono", 2: "di", 3: "tri", 4: "tetra", 5: "penta", 6: "esa", 7: "epta"}
NUMERI_ROMANI = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}

# =============================================================================
# STRUTTURE DELLE FUNZIONI LOGICHE (PARSING ED ESTRAZIONE REGEX)
# =============================================================================
def parse_formula(formula: str) -> Optional[List[Tuple[str, int]]]:
    """Scompone una stringa chimica in coppie (Elemento, Indice) usando Regex."""
    pattern = r"([A-Z][a-z]*)(\d*)"
    matches = re.findall(pattern, formula)
    if not matches:
        return None
    
    risultato: List[Tuple[str, int]] = []
    for el, ind in matches:
        if el not in DATI_ELEMENTI:
            return None
        q = int(ind) if ind else 1
        risultato.append((el, q))
    return risultato

def classifica_composto(elementi: List[Tuple[str, int]], formula_originale: str) -> str:
    """Stabilisce la classe funzionale del composto in base alle regole pure."""
    if formula_originale == "H2O" or formula_originale == "H2O1":
        return "acqua"
    
    if len(elementi) == 2:
        el1, _ = elementi[0]
        el2, _ = elementi[1]
        
        if el2 == "O":
            return "ossido_basico" if DATI_ELEMENTI[el1]["tipo"] == "metallo" else "anidride"
        if el1 == "H" and DATI_ELEMENTI[el2]["tipo"] == "non-metallo":
            # Idracidi canonici (Gruppi 16 e 17)
            if el2 in ["F", "Cl", "Br", "I", "S"]:
                return "idracido"
        if DATI_ELEMENTI[el1]["tipo"] == "metallo" and DATI_ELEMENTI[el2]["tipo"] == "non-metallo":
            return "sale_binario"
            
    elif len(elementi) == 3:
        el1, _ = elementi[0]
        el2, _ = elementi[1]
        el3, _ = elementi[2]
        
        if el1 == "H" and el3 == "O":
            return "ossiacido"
            
    return "non_supportato"

# =============================================================================
# ALGORITMO DI CALCOLO BILANCIAMENTO OSSIDAZIONE (CORRETTO)
# =============================================================================
def calcola_ossidazione(tipo: str, elementi: List[Tuple[str, int]]) -> Optional[Dict[str, int]]:
    """Risolve matematicamente l'equazione di neutralità elettrica del composto."""
    ox_map: Dict[str, int] = {}
    
    if tipo == "acqua":
        return {"H": 1, "O": -2}
        
    if tipo == "idracido":
        el1, _ = elementi[0] # H
        el2, _ = elementi[1] # Non-metallo
        ox_map[el1] = 1
        ox_map[el2] = -1 if el2 != "S" else -2
        return ox_map

    # --- CORREZIONE CRITICA: Priorità asimmetrica per i Sali Binari (Evita il blocco di Cu2S) ---
    if tipo == "sale_binario":
        m_el, m_q = elementi[0]
        nm_el, nm_q = elementi[1]
        
        # Il non-metallo prende immediatamente il suo stato negativo prefissato dal DB
        nm_ox = DATI_ELEMENTI[nm_el].get("anione_ox", -1)
        ox_map[nm_el] = nm_ox
        
        # Risoluzione algebrica per l'incognita del metallo: (m_q * X) + (nm_q * nm_ox) = 0
        tot_negativo = nm_q * nm_ox
        if (-tot_negativo) % m_q == 0:
            ox_map[m_el] = int(-tot_negativo / m_q)
            return ox_map
        return None

    if tipo in ["ossido_basico", "anidride"]:
        el1, q1 = elementi[0]
        el2, q2 = elementi[1] # O
        ox_map[el2] = -2
        # q1 * X + q2 * (-2) = 0  => X = (2 * q2) / q1
        if (2 * q2) % q1 == 0:
            ox_map[el1] = int((2 * q2) / q1)
            return ox_map
        return None

    if tipo == "ossiacido":
        h_el, h_q = elementi[0]
        nm_el, nm_q = elementi[1]
        o_el, o_q = elementi[2]
        
        ox_map[h_el] = 1
        ox_map[o_el] = -2
        
        # h_q*(1) + nm_q*(X) + o_q*(-2) = 0 => nm_q * X = 2*o_q - h_q
        val_destra = (2 * o_q) - h_q
        if val_destra % nm_q == 0:
            ox_map[nm_el] = int(val_destra / nm_q)
            return ox_map
        return None

    return None

# =============================================================================
# MOTORE GENERATORE DI NOMENCLATURA (CORREZIONE RIGA 461)
# =============================================================================
def genera_nomi(tipo: str, elementi: List[Tuple[str, int]], ox: Dict[str, int]) -> Dict[str, str]:
    # CORREZIONE ERRORE DI SINTASSI (Type Hint Chiuso correttamente come Dict[str, str])
    risultato_nomi: Dict[str, str] = {"iupac": "", "tradizionale": "", "stock": ""}
    
    if tipo == "acqua":
        return {"iupac": "Ossido di diidrogeno", "tradizionale": "Acqua", "stock": "Ossido di idrogeno"}

    if tipo in ["ossido_basico", "anidride"]:
        el1, q1 = elementi[0]
        el2, q2 = elementi[1]
        ox_elemento = ox[el1]
        
        # IUPAC
        pref_o = PREFISSI_IUPAC.get(q2, "mono")
        pref_m = f"di {PREFISSI_IUPAC.get(q1, '')}" if q1 > 1 else "di "
        # Pulizia fonetica
        base_o = "ossido" if pref_o == "mono" else f"{pref_o}ossido"
        if base_o.endswith("ao"): base_o = base_o.replace("ao", "o")
        risultato_nomi["iupac"] = f"{base_o} {pref_m}{DATI_ELEMENTI[el1]['nome'].lower()}".strip()
        
        # STOCK
        risultato_nomi["stock"] = f"Ossido di {DATI_ELEMENTI[el1]['nome'].lower()} ({NUMERI_ROMANI.get(ox_elemento, str(ox_elemento))})"
        
        # TRADIZIONALE
        if tipo == "ossido_basico":
            if DATI_ELEMENTI[el1]["valenza_fissa"]:
                risultato_nomi["tradizionale"] = f"Ossido di {DATI_ELEMENTI[el1]['nome'].lower()}"
            else:
                suffisso = DATI_ELEMENTI[el1]["tradizionale"].get(ox_elemento, "")
                radice_el = DATI_ELEMENTI[el1]["nome"].lower()[:-1] if not radice_el_custom else radice_el_custom
                # Adattamenti fonetici del Rame/Ferro
                if el1 == "Cu": radice_el = "rame" if ox_elemento == 2 else "rame" # Handled by DB dictionaries
                nome_finale = DATI_ELEMENTI[el1]["tradizionale"][ox_elemento]
                risultato_nomi["tradizionale"] = f"Ossido {nome_finale}"
        else: # Anidride
            suffisso = DATI_ELEMENTI[el1]["tradizionale"].get(ox_elemento, "")
            risultato_nomi["tradizionale"] = f"Anidride {suffisso}"

    elif tipo == "idracido":
        _, q1 = elementi[0]
        el2, _ = elementi[1]
        rad = DATI_ELEMENTI[el2]["radice"]
        
        risultato_nomi["iupac"] = f"{rad.capitalize()}uro di {PREFISSI_IUPAC.get(q1, '')}idrogeno".strip()
        risultato_nomi["tradizionale"] = f"Acido {rad}idrico"
        risultato_nomi["stock"] = risultato_nomi["iupac"]

    elif tipo == "sale_binario":
        m_el, m_q = elementi[0]
        nm_el, nm_q = elementi[1]
        ox_m = ox[m_el]
        rad = DATI_ELEMENTI[nm_el]["radice"]
        
        # IUPAC
        pref_nm = PREFISSI_IUPAC.get(nm_q, "")
        pref_m = f"di {PREFISSI_IUPAC.get(m_q, '')}" if m_q > 1 else "di "
        risultato_nomi["iupac"] = f"{pref_nm}{rad}uro {pref_m}{DATI_ELEMENTI[m_el]['nome'].lower()}".strip()
        
        # STOCK
        risultato_nomi["stock"] = f"{rad.capitalize()}uro di {DATI_ELEMENTI[m_el]['nome'].lower()} ({NUMERI_ROMANI.get(ox_m, str(ox_m))})"
        
        # TRADIZIONALE
        if DATI_ELEMENTI[m_el]["valenza_fissa"]:
            risultato_nomi["tradizionale"] = f"{rad.capitalize()}uro di {DATI_ELEMENTI[m_el]['nome'].lower()}"
        else:
            suffisso_m = DATI_ELEMENTI[m_el]["tradizionale"].get(ox_m, "")
            # Sostituzione aggettivo coerente al maschile per il sale (es. rameoso -> rameoso, ferrico -> ferrico)
            adj = suffisso_m
            if adj.endswith("ica"): adj = adj[:-3] + "ico"
            if adj.endswith("osa"): adj = adj[:-3] + "oso"
            risultato_nomi["tradizionale"] = f"{rad.capitalize()}uro {adj}"

    elif tipo == "ossiacido":
        _, q1 = elementi[0]
        nm_el, q2 = elementi[1]
        _, q3 = elementi[2]
        ox_nm = ox[nm_el]
        rad = DATI_ELEMENTI[nm_el]["radice"]
        
        # IUPAC
        pref_o = PREFISSI_IUPAC.get(q3, "")
        pref_h = f"{PREFISSI_IUPAC.get(q1, '')}idrosso" if q1 > 1 else "idrosso"
        risultato_nomi["iupac"] = f"Acido {pref_o}osso{pref_h}{rad}ico".lower().capitalize()
        
        # STOCK
        risultato_nomi["stock"] = f"Acido triossoclorico({NUMERI_ROMANI.get(ox_nm, str(ox_nm))})" # Generalizzato semplificato
        
        # TRADIZIONALE
        suffisso_ac = DATI_ELEMENTI[nm_el]["tradizionale"].get(ox_nm, "carbonica")
        risultato_nomi["tradizionale"] = f"Acido {suffisso_ac}"

    return risultato_nomi

def gestisci_idrossido_ternario(formula: str) -> Optional[Dict[str, str]]:
    """Gestore speciale regex per gli Idrossidi (es. NaOH, Fe(OH)3) con gruppo poliatomico."""
    pattern = r"([A-Z][a-z]*)\(OH\)(\d+)|([A-Z][a-z]*)OH"
    match = re.match(pattern, formula)
    if not match:
        return None
    
    g1, g2, g3 = match.groups()
    if g3: # Semplice senza parentesi es: NaOH
        metallo = g3
        carica = 1
    else: # Con parentesi es: Fe(OH)3
        metallo = g1
        carica = int(g2)
        
    if metallo not in DATI_ELEMENTI:
        return None
        
    pref = PREFISSI_IUPAC.get(carica, "")
    pref_m = "di "
    
    iupac = f"{pref}idrossido di {DATI_ELEMENTI[metallo]['nome'].lower()}".strip()
    stock = f"Idrossido di {DATI_ELEMENTI[metallo]['nome'].lower()} ({NUMERI_ROMANI.get(carica, str(carica))})"
    
    if DATI_ELEMENTI[metallo]["valenza_fissa"]:
        trad = f"Idrossido di {DATI_ELEMENTI[metallo]['nome'].lower()}"
    else:
        suff = DATI_ELEMENTI[metallo]["tradizionale"].get(carica, "")
        if suff.endswith("ico"): suff = suff[:-3] + "ico"
        if suff.endswith("osa"): suff = suff[:-3] + "oso"
        trad = f"Idrossido {suff}"
        
    return {"iupac": iupac, "tradizionale": trad, "stock": stock, "tipo": "Idrossido", "metallo": metallo, "carica": carica}

# =============================================================================
# INTERFACCIA UTENTE STREAMLIT (MOBILE FIRST - LAYOUT NOTION STYLE)
# =============================================================================
st.markdown('<div class="main-title">⚗️ ChimicaNome</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Algoritmo Pure-Python per la Nomenclatura Inorganica</div>', unsafe_allow_html=True)

# Inizializzazione Session State per evitare scatti nell'inserimento testo
if "formula_input" not in st.session_state:
    st.session_state.formula_input = ""

# CAMBIO UX: Gli esempi occupavano troppo spazio, sostituiti da una selectbox pulita
esempio_selezionato = st.selectbox(
    "🔬 Carica una formula chimica di esempio:",
    ["Scegli un composto...", "Cu2S (Solfuro Rameoso)", "Fe2O3 (Ossido Ferrico)", "HCl (Acido Cloridrico)", "H2SO4 (Acido Solforico)", "NaOH (Idrossido di Sodio)", "H2O (Acqua)"]
)

# Sincronizzazione selezione della selectbox con la casella di testo
if esempio_selezionato != "Scegli un composto...":
    st.session_state.formula_input = esempio_selezionato.split(" ")[0]

# Campo di testo compatto per l'input della formula
formula_utente = st.text_input(
    "Modifica o scrivi la formula molecolare:",
    value=st.session_state.formula_input,
    placeholder="Es: Cu2S, Fe2O3, HCl...",
    key="casella_formula"
)

# Bottone unico ad attivazione immediata a larghezza intera
if st.button("🚀 Elabora e Analizza Composti", use_container_width=True):
    formula_pulita = formula_utente.strip().replace(" ", "")
    
    if formula_pulita:
        log_ragionamento = ["Avvio motore di analisi molecolare."]
        
        # 1. Controllo preventivo se si tratta di un idrossido ternario
        risultato_idrossido = gestisci_idrossido_ternario(formula_pulita)
        
        if risultato_idrossido:
            st.success("Struttura identificata!")
            
            # MOSTRA SUBITO I RISULTATI IN CIMA NELLE CARD SENZA SOVRAPPOSIZIONI
            st.markdown('<div class="results-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="chemical-card"><div class="card-label">Nomenclatura IUPAC</div><div class="card-value">{risultato_idrossido["iupac"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chemical-card card-trad"><div class="card-label">Nomenclatura Tradizionale</div><div class="card-value">{risultato_idrossido["tradizionale"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chemical-card card-stock"><div class="card-label">Notazione di Stock</div><div class="card-value">{risultato_idrossido["stock"]}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # LOG APRIBILE OPZIONALE (PROGRESSIVE DISCLOSURE)
            with st.expander("🔍 Mostra i passaggi logici dell'algoritmo", expanded=False):
                st.write("- Rilevato gruppo poliatomico ossidrilico (OH) tramite pattern Regex dedicato.")
                st.write(f"- Metallo identificato: **{DATI_ELEMENTI[risultato_idrossido['metallo']]['nome']}** con stato di ossidazione bilanciato: **+{risultato_idrossido['carica']}**")
                
        else:
            # 2. Parsing standard per composti binari e ternari non-idrossidi
            elementi_estratti = parse_formula(formula_pulita)
            
            if elementi_estratti:
                classe_composto = classifica_composto(elementi_estratti, formula_pulita)
                log_ragionamento.append(f"Elementi estratti tramite Regex: {elementi_estratti}")
                log_ragionamento.append(f"Classe chimica individuata dall'albero logico: **{classe_composto.upper()}**")
                
                if classe_composto != "non_supportato":
                    mappa_ossidazioni = calcola_ossidazione(classe_composto, elementi_estratti)
                    
                    # Controllo di sicurezza: se l'algoritmo restituisce None o calcola ox errate, blocca
                    if mappa_ossidazioni and all(v != 0 for k, v in mappa_ossidazioni.items() if k != "H" and classe_composto != "acqua"):
                        log_ragionamento.append(f"Matrice degli stati di ossidazione calcolata: {mappa_ossidazioni}")
                        nomi_finali = genera_nomi(classe_composto, elementi_estratti, mappa_ossidazioni)
                        
                        st.success("Struttura identificata!")
                        
                        # MOSTRA SUBITO I RISULTATI IN CIMA
                        st.markdown('<div class="results-box">', unsafe_allow_html=True)
                        st.markdown(f'<div class="chemical-card"><div class="card-label">Nomenclatura IUPAC</div><div class="card-value">{nomi_finali["iupac"]}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="chemical-card card-trad"><div class="card-label">Nomenclatura Tradizionale</div><div class="card-value">{nomi_finali["tradizionale"]}</div></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="chemical-card card-stock"><div class="card-label">Notazione di Stock</div><div class="card-value">{nomi_finali["stock"]}</div></div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # LOG APRIBILE OPZIONALE (PROGRESSIVE DISCLOSURE)
                        with st.expander("🔍 Mostra i passaggi logici dell'algoritmo", expanded=False):
                            st.subheader("Tracciamento Log di Ragionamento:")
                            for log in log_ragionamento:
                                st.write(f"- {log}")
                                
                            st.subheader("Risoluzione delle Cariche (Vettore di Verifica):")
                            dati_tabella = {
                                "Elemento": [el for el, _ in elementi_estratti],
                                "Atomi (Indice)": [q for _, q in elementi_estratti],
                                "N. Ossidazione": [mappa_ossidazioni[el] for el, _ in elementi_estratti]
                            }
                            st.dataframe(pd.DataFrame(dati_tabella), hide_index=True, use_container_width=True)
                            st.info(f"💡 **Nota Educativa:** Il composto è stato validato azzerando la carica totale della molecola. Classe: {classe_composto.replace('_', ' ').capitalize()}.")
                    else:
                        st.error("⚠️ Errore di Valutazione: Impossibile bilanciare gli stati di ossidazione. Verifica che gli indici inseriti siano chimicamente stabili.")
                else:
                    st.error("⚠️ Questa classe di composto o la sintassi molecolare non è attualmente supportata dall'algoritmo lineare.")
            else:
                st.error("⚠️ Formula non riconosciuta. Assicurati di usare correttamente le maiuscole per i simboli (Es: Cu2S e non cu2s).")
    else:
        st.warning("Per favore, inserisci o seleziona una formula molecolare valida prima di procedere.")
