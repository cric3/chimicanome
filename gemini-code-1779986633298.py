"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         ⚗️  ChimicaNome — Nomenclatore di Composti Inorganici              ║
║         Progetto "Capolavoro" per l'Esame di Stato                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  DESCRIZIONE:                                                               ║
║    Applicazione web interattiva che implementa un algoritmo PURO basato     ║
║    su regole logico-chimiche per assegnare automaticamente i nomi IUPAC     ║
║    e Tradizionali ai principali composti inorganici binari e ternari.       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Optional

# 📊 CONFIGURAZIONE PAGINA STREAMLIT
st.set_page_config(
    page_title="ChimicaNome — Nomenclatore Automatico",
    page_icon="⚗️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 🎨 STILE INIETTATO (CSS Personalizzato coerente con il design system)
st.markdown("""
<style>
:root {
    --surface: #ffffff;
    --border: #e2e8f0;
    --r-lg: 12px;
    --sh-lg: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --indigo: #4f46e5;
    --green: #10b981;
    --ink: #1f2937;
}
.results-grid { display:grid; grid-template-columns:1fr 1fr; gap:.8rem; margin-bottom:1.2rem; width:100%; } 
.result-card { background:var(--surface); border:1px solid var(--border); border-radius:var(--r-lg); padding:1.2rem 1.1rem .95rem; box-shadow:var(--sh-lg); position:relative; overflow:hidden; min-width:0; word-wrap:break-word; overflow-wrap:break-word; } 
.result-card::before { content:''; position:absolute; top:0; left:0; right:0; height:4px; border-radius:var(--r-lg) var(--r-lg) 0 0; } 
.card-iupac::before { background:linear-gradient(90deg,#6366f1,#a5b4fc); } 
.card-trad::before { background:linear-gradient(90deg,#059669,#6ee7b7); } 
.rc-label { font-size:.75rem; font-weight:700; text-transform:uppercase; letter-spacing:1.6px; margin:.12rem 0 .45rem; } 
.card-iupac .rc-label { color:var(--indigo); } 
.card-trad .rc-label { color:var(--green); } 
.rc-name { font-size:1.25rem; font-weight:600; line-height:1.3; color:var(--ink); } 
.card-iupac .rc-name { color:#3730a3; } 
.card-trad .rc-name { color:#065f46; } 
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEZIONE 1 — DATABASE CHIMICO
# ══════════════════════════════════════════════════════════════════════════════

PREFISSI_GRECI: Dict[int, str] = {
    1: 'mono', 2: 'di',   3: 'tri',  4: 'tetra', 5: 'penta',
    6: 'esa',  7: 'epta', 8: 'otta', 9: 'nona',  10: 'deca',
}

NUMERI_ROMANI: Dict[int, str] = {
    1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
    6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X',
}

DATI_ELEMENTI: Dict[str, Dict] = {
    'H':  {'type': 'nonmetal', 'name_it': 'idrogeno', 'ox_states': [+1, -1]},
    'O':  {'type': 'nonmetal', 'name_it': 'ossigeno', 'ox_states': [-2]},
    'F':  {'type': 'nonmetal', 'name_it': 'fluoro', 'ox_states': [-1], 'anion': 'fluoruro'},
    'Cl': {'type': 'nonmetal', 'name_it': 'cloro', 'ox_states': [-1, +1, +3, +5, +7], 'anion': 'cloruro'},
    'Br': {'type': 'nonmetal', 'name_it': 'bromo', 'ox_states': [-1, +1, +3, +5], 'anion': 'bromuro'},
    'I':  {'type': 'nonmetal', 'name_it': 'iodio', 'ox_states': [-1, +1, +5, +7], 'anion': 'ioduro'},
    'S':  {'type': 'nonmetal', 'name_it': 'zolfo', 'ox_states': [-2, +4, +6], 'anion': 'solfuro'},
    'Se': {'type': 'nonmetal', 'name_it': 'selenio', 'ox_states': [-2, +4, +6], 'anion': 'seleniuro'},
    'Te': {'type': 'nonmetal', 'name_it': 'tellurio', 'ox_states': [-2, +4, +6], 'anion': 'tellururo'},
    'N':  {'type': 'nonmetal', 'name_it': 'azoto', 'ox_states': [-3, +1, +2, +3, +4, +5], 'anion': 'nitruro'},
    'P':  {'type': 'nonmetal', 'name_it': 'fosforo', 'ox_states': [-3, +3, +5], 'anion': 'fosfuro'},
    'C':  {'type': 'nonmetal', 'name_it': 'carbonio', 'ox_states': [-4, +2, +4], 'anion': 'carburo'},
    'Si': {'type': 'nonmetal', 'name_it': 'silicio', 'ox_states': [-4, +4], 'anion': 'siliciuro'},
    'As': {'type': 'nonmetal', 'name_it': 'arsenico', 'ox_states': [-3, +3, +5], 'anion': 'arseniuro'},
    'Sb': {'type': 'nonmetal', 'name_it': 'antimonio', 'ox_states': [-3, +3, +5], 'anion': 'antimoniuro'},
    'B':  {'type': 'nonmetal', 'name_it': 'boro', 'ox_states': [+3], 'anion': 'boruro'},
    
    # Metalli a valenza fissa
    'Li': {'type': 'metal', 'name_it': 'litio',    'ox_states': [+1], 'trad_adj': {+1: None}},
    'Na': {'type': 'metal', 'name_it': 'sodio',    'ox_states': [+1], 'trad_adj': {+1: None}},
    'K':  {'type': 'metal', 'name_it': 'potassio', 'ox_states': [+1], 'trad_adj': {+1: None}},
    'Rb': {'type': 'metal', 'name_it': 'rubidio',  'ox_states': [+1], 'trad_adj': {+1: None}},
    'Cs': {'type': 'metal', 'name_it': 'cesio',    'ox_states': [+1], 'trad_adj': {+1: None}},
    'Be': {'type': 'metal', 'name_it': 'berillio',  'ox_states': [+2], 'trad_adj': {+2: None}},
    'Mg': {'type': 'metal', 'name_it': 'magnesio',  'ox_states': [+2], 'trad_adj': {+2: None}},
    'Ca': {'type': 'metal', 'name_it': 'calcio',    'ox_states': [+2], 'trad_adj': {+2: None}},
    'Sr': {'type': 'metal', 'name_it': 'stronzio',  'ox_states': [+2], 'trad_adj': {+2: None}},
    'Ba': {'type': 'metal', 'name_it': 'bario',     'ox_states': [+2], 'trad_adj': {+2: None}},
    'Ra': {'type': 'metal', 'name_it': 'radio',     'ox_states': [+2], 'trad_adj': {+2: None}},
    'Al': {'type': 'metal', 'name_it': 'alluminio', 'ox_states': [+3], 'trad_adj': {+3: None}},
    'Zn': {'type': 'metal', 'name_it': 'zinco',     'ox_states': [+2], 'trad_adj': {+2: None}},
    'Ag': {'type': 'metal', 'name_it': 'argento',   'ox_states': [+1], 'trad_adj': {+1: None}},

    # Metalli a valenza variabile
    'Fe': {'type': 'metal', 'name_it': 'ferro', 'ox_states': [+2, +3], 'trad_adj': {+2: 'ferroso', +3: 'ferrico'}},
    'Cu': {'type': 'metal', 'name_it': 'rame', 'ox_states': [+1, +2], 'trad_adj': {+1: 'rameoso', +2: 'rameico'}},
    'Hg': {'type': 'metal', 'name_it': 'mercurio', 'ox_states': [+1, +2], 'trad_adj': {+1: 'mercuroso', +2: 'mercurico'}},
    'Pb': {'type': 'metal', 'name_it': 'piombo', 'ox_states': [+2, +4], 'trad_adj': {+2: 'piomboso', +4: 'piombico'}},
    'Sn': {'type': 'metal', 'name_it': 'stagno', 'ox_states': [+2, +4], 'trad_adj': {+2: 'stannoso', +4: 'stannico'}},
    'Au': {'type': 'metal', 'name_it': 'oro', 'ox_states': [+1, +3], 'trad_adj': {+1: 'auroso', +3: 'aurico'}},
    'Co': {'type': 'metal', 'name_it': 'cobalto', 'ox_states': [+2, +3], 'trad_adj': {+2: 'cobaltoso', +3: 'cobaltico'}},
    'Ni': {'type': 'metal', 'name_it': 'nichel', 'ox_states': [+2, +3], 'trad_adj': {+2: 'nicheloso', +3: 'nichelico'}},
    'Mn': {'type': 'metal', 'name_it': 'manganese', 'ox_states': [+2, +3, +4, +6, +7], 'trad_adj': {+2: 'manganoso', +3: 'manganico'}},
    'Cr': {'type': 'metal', 'name_it': 'cromo', 'ox_states': [+2, +3, +6], 'trad_adj': {+2: 'cromoso', +3: 'cromico'}},
    'Ti': {'type': 'metal', 'name_it': 'titanio', 'ox_states': [+2, +3, +4], 'trad_adj': {+2: 'titanoso', +3: 'titanico'}},
    'V':  {'type': 'metal', 'name_it': 'vanadio', 'ox_states': [+2, +3, +4, +5], 'trad_adj': {+2: 'vanadoso', +3: 'vanadico'}},
    'Bi': {'type': 'metal', 'name_it': 'bismuto', 'ox_states': [+3, +5], 'trad_adj': {+3: 'bismutoso', +5: 'bismutico'}},
    'Pt': {'type': 'metal', 'name_it': 'platino', 'ox_states': [+2, +4], 'trad_adj': {+2: 'platinoso', +4: 'platinico'}},
}

NOMI_OSSIACIDI: Dict[Tuple, str] = {
    ('S', 6): 'acido solforico',   ('S', 4): 'acido solforoso',
    ('N', 5): 'acido nitrico',     ('N', 3): 'acido nitroso',     ('N', 4): 'acido nitroso',
    ('P', 5): 'acido fosforico',   ('P', 3): 'acido fosforoso',
    ('C', 4): 'acido carbonico',   ('C', 2): 'acido carbonoso',
    ('Cl', 7): 'acido perclorico', ('Cl', 5): 'acido clorico',   ('Cl', 3): 'acido cloroso', ('Cl', 1): 'acido ipocloroso',
    ('Br', 5): 'acido bromico',    ('Br', 3): 'acido bromoso',    ('Br', 1): 'acido ipobromoso',
    ('I', 7): 'acido periodico',   ('I', 5): 'acido iodico',      ('I', 1): 'acido ipoiodoso',
    ('Si', 4): 'acido silicico',   ('Cr', 6): 'acido cromico',    ('Mn', 7): 'acido permanganico',
    ('B', 3): 'acido borico',      ('As', 5): 'acido arsenico',   ('As', 3): 'acido arsenioso',
    ('Sb', 5): 'acido antimonico', ('Sb', 3): 'acido antimonioso',
}

NOMI_ANIDRIDI: Dict[Tuple, str] = {
    ('S', 6): 'solforica',     ('S', 4): 'solforosa',
    ('N', 5): 'nitrica',       ('N', 3): 'nitrosa',       ('N', 4): 'nitrosa',
    ('P', 5): 'fosforica',     ('P', 3): 'fosforosa',
    ('C', 4): 'carbonica',     ('C', 2): 'carbonosa',
    ('Cl', 7): 'perclorica',    ('Cl', 5): 'clorica',      ('Cl', 3): 'clorosa', ('Cl', 1): 'ipoclorosa',
    ('Br', 5): 'bromica',       ('Br', 1): 'ipobromosa',
    ('I', 7): 'periodica',      ('I', 5): 'iodica',        ('I', 1): 'ipoiodosa',
    ('Si', 4): 'silicica',      ('Cr', 6): 'cromica',      ('Mn', 7): 'permanganica', ('B', 3): 'borica',
    ('As', 5): 'arsenica',      ('As', 3): 'arseniosa',
}

NOMI_IDRACIDI: Dict[str, str] = {
    'F': 'acido fluoridrico',  'Cl': 'acido cloridrico', 'Br': 'acido bromidrico',
    'I': 'acido iodidrico',   'S': 'acido solfidrico',   'Se': 'acido selenidrico',
    'Te': 'acido telluridrico', 'N': 'acido azotidrico',  'P': 'acido fosfidrico',
}

NOMI_ANIONI: Dict[str, str] = {
    'F': 'fluoruro', 'Cl': 'cloruro',  'Br': 'bromuro',  'I':  'ioduro',
    'S': 'solfuro',  'Se': 'seleniuro','Te': 'tellururo', 'O':  'ossido',
    'N': 'nitruro',  'P':  'fosfuro',  'C':  'carburo',   'Si': 'siliciuro',
    'As':'arseniuro','H':  'idruro',   'B':  'boruro',    'Sb': 'antimoniuro',
}

RADICI_IUPAC = {
    'S': 'solfor', 'N': 'nitr', 'P': 'fosfor', 'C': 'carbon', 'Cl': 'clor', 
    'Br': 'brom', 'I': 'iod', 'Si': 'silic', 'Cr': 'crom', 'Mn': 'mangan', 
    'B': 'bor', 'As': 'arsen', 'Sb': 'antimon'
}

# ══════════════════════════════════════════════════════════════════════════════
# SEZIONE 2 — PARSING E LOGICA ALGORITMICA
# ══════════════════════════════════════════════════════════════════════════════

def valida_formula(formula: str) -> Tuple[bool, str]:
    if not formula or not formula.strip():
        return False, "La formula non può essere vuota."
    if not re.match(r'^[A-Za-z0-9()]+$', formula):
        return False, "Usa solo lettere, cifre e parentesi tonde ()."
    profondita = 0
    for i, ch in enumerate(formula):
        if ch == '(': profondita += 1
        elif ch == ')': profondita -= 1
        if profondita < 0: return False, f"Parentesi ')' alla posizione {i+1} sbilanciata."
    if profondita != 0: return False, "Una o più parentesi '(' non sono state chiuse."
    if not (formula[0].isupper() or formula[0] == '('):
        return False, "La formula deve iniziare con una lettera maiuscola."
    return True, ''

def parse_formula(formula: str) -> Dict[str, int]:
    def _parse(testo: str, fattore: int = 1) -> Dict[str, int]:
        risultato: Dict[str, int] = {}
        i = 0
        while i < len(testo):
            if testo[i] == '(':
                profondita = 1
                j = i + 1
                while j < len(testo) and profondita > 0:
                    if testo[j] == '(': profondita += 1
                    elif testo[j] == ')': profondita -= 1
                    j += 1
                k = j
                while k < len(testo) and testo[k].isdigit(): k += 1
                mult_esterno = int(testo[j:k]) if k > j else 1
                contenuto_interno = _parse(testo[i + 1: j - 1], fattore * mult_esterno)
                for elem, cnt in contenuto_interno.items():
                    risultato[elem] = risultato.get(elem, 0) + cnt
                i = k
            elif testo[i].isupper():
                j = i + 1
                while j < len(testo) and testo[j].islower(): j += 1
                simbolo = testo[i:j]
                k = j
                while k < len(testo) and testo[k].isdigit(): k += 1
                pedice = int(testo[j:k]) if k > j else 1
                risultato[simbolo] = risultato.get(simbolo, 0) + pedice * fattore
                i = k
            else:
                i += 1
        return risultato
    return _parse(formula)

def classifica_composto(elementi: Dict[str, int]) -> Tuple[Optional[str], List[str]]:
    log = []
    chiavi = list(elementi.keys())
    log.append(f"🔍 **Elementi estratti**: {', '.join(chiavi)}")
    
    for el in chiavi:
        if el not in DATI_ELEMENTI:
            log.append(f"❌ Elemento '{el}' sconosciuto al database.")
            return None, log
            
    if len(elementi) == 1:
        log.append("⚠️ È una sostanza elementare (es. O₂). L'app analizza composti legati binari o ternari.")
        return None, log
        
    elif len(elementi) == 2:
        log.append("🧪 **Composto Binario** rilevato (esattamente 2 elementi distinti).")
        if 'H' in elementi and 'O' in elementi:
            return "acqua", log
        if 'O' in elementi:
            altro = [el for el in chiavi if el != 'O'][0]
            if DATI_ELEMENTI[altro]['type'] == 'metal':
                log.append(f"• Analisi speculativa: Contiene Ossigeno + Metallo ({DATI_ELEMENTI[altro]['name_it'].upper()}) → **Ossido Basico**.")
                return "ossido_basico", log
            else:
                log.append(f"• Analisi speculativa: Contiene Ossigeno + Non-Metallo ({DATI_ELEMENTI[altro]['name_it'].upper()}) → **Anidride (Ossido Acido)**.")
                return "anidride", log
        if 'H' in elementi:
            outro = [el for el in chiavi if el != 'H'][0]
            if DATI_ELEMENTI[outro]['type'] == 'nonmetal' and outro in ['F', 'Cl', 'Br', 'I', 'S', 'Se', 'Te']:
                log.append(f"• Analisi speculativa: Contiene Idrogeno + Non-metallo specifico del gruppo 16/17 → **Idracido**.")
                return "idracido", log
        el1, el2 = chiavi[0], chiavi[1]
        if (DATI_ELEMENTI[el1]['type'] == 'metal' and DATI_ELEMENTI[el2]['type'] == 'nonmetal') or \
           (DATI_ELEMENTI[el1]['type'] == 'nonmetal' and DATI_ELEMENTI[el2]['type'] == 'metal'):
            log.append("• Analisi speculativa: Contiene Metallo + Non-metallo (senza O o H strutturali) → **Sale Binario**.")
            return "sale_binario", log
            
    elif len(elementi) == 3:
        log.append("🧪 **Composto Ternario** rilevato (esattamente 3 elementi distinti).")
        if 'O' in elementi and 'H' in elementi:
            metallo = [el for el in chiavi if el not in ['O', 'H']]
            if metallo and DATI_ELEMENTI[metallo[0]]['type'] == 'metal':
                log.append(f"• Analisi speculativa: Contiene Metallo ({DATI_ELEMENTI[metallo[0]]['name_it'].upper()}) + Idrogeno + Ossigeno → **Idrossido**.")
                return "idrossido", log
        if 'H' in elementi and 'O' in elementi:
            nonmetallo = [el for el in chiavi if el not in ['O', 'H']]
            if nonmetallo and DATI_ELEMENTI[nonmetallo[0]]['type'] == 'nonmetal':
                log.append(f"• Analisi speculativa: Contiene Idrogeno + Non-metallo ({DATI_ELEMENTI[nonmetallo[0]]['name_it'].upper()}) + Ossigeno → **Ossiacido**.")
                return "ossiacido", log

    log.append("⚠️ Tipologia di composto non supportata (es. idruri metallici o ossisali complessi).")
    return None, log

def calcola_ossidazione(elementi: Dict[str, int], tipo: str, log: List[str]) -> Dict[str, int]:
    ox = {}
    log.append("🧮 **Risoluzione algebrica del sistema di cariche** (Equazione di neutralità: Σ(atomi × n.ox) = 0):")
    
    if tipo == "acqua":
        log.append("• Composto stabile di riferimento: H = +1, O = -2.")
        return {'H': 1, 'O': -2}
        
    if tipo in ["ossido_basico", "anidride"]:
        ox['O'] = -2
        altro = [el for el in elementi if el != 'O'][0]
        ox[altro] = (elementi['O'] * 2) // elementi[altro]
        log.append(f" 1. L'Ossigeno ha stato fisso stabilito a **-2**.")
        log.append(f" 2. Carica negativa totale apportata dall'ossigeno: {elementi['O']} atomi × (-2) = **{-2*elementi['O']}**.")
        log.append(f" 3. Equazione: ({elementi[altro]} × X) + ({-2*elementi['O']}) = 0   =>   X = +{ox[altro]}.")
        log.append(f" 4. Stato di ossidazione individuale di **{altro}** = **+{ox[altro]}**.")
        
    elif tipo == "idracido":
        ox['H'] = 1
        altro = [el for el in elementi if el != 'H'][0]
        ox[altro] = -elementi['H'] // elementi[altro]
        log.append(f" 1. L'Idrogeno legato a un non-metallo assume stato fisso a **+1**.")
        log.append(f" 2. Carica positiva totale apportata dall'idrogeno: {elementi['H']} atomi × (+1) = **+{elementi['H']}**.")
        log.append(f" 3. Equazione: ({elementi[outro]} × X) + (+{elementi['H']}) = 0   =>   X = {ox[altro]}.")
        log.append(f" 4. Il non-metallo **{altro}** assume n.ox. negativo stabile = **{ox[altro]}**.")
        
    elif tipo == "sale_binario":
        metallo = [el for el in elementi if DATI_ELEMENTI[el]['type'] == 'metal'][0]
        nonmetallo = [el for el in elementi if DATI_ELEMENTI[el]['type'] == 'nonmetal'][0]
        ox_nm = [x for x in DATI_ELEMENTI[nonmetallo]['ox_states'] if x < 0][0]
        ox[nonmetallo] = ox_nm
        ox[metallo] = -(elementi[nonmetallo] * ox_nm) // elementi[metallo]
        log.append(f" 1. Nei sali binari, il non-metallo (**{nonmetallo}**) prende sempre il suo n.ox. negativo stabile della tavola periodica: **{ox_nm}**.")
        log.append(f" 2. Carica totale dell'anione: {elementi[nonmetallo]} atomi × ({ox_nm}) = **{elementi[nonmetallo] * ox_nm}**.")
        log.append(f" 3. Equazione di neutralità: ({elementi[metallo]} × X) + ({elementi[nonmetallo] * ox_nm}) = 0.")
        log.append(f" 4. Ricavo dello stato del metallo **{metallo}** = **+{ox[metallo]}**.")
        
    elif tipo == "idrossido":
        ox['O'], ox['H'] = -2, 1
        metallo = [el for el in elementi if el not in ['O', 'H']][0]
        ox[metallo] = (2 * elementi['O'] - elementi['H']) // elementi[metallo]
        log.append(f" 1. Il gruppo ossidrilico (OH) ha complessivamente una carica istituzionale pari a **-1**.")
        log.append(f" 2. Ci sono {elementi['H']} gruppi (OH)⁻ ricavati dal parsing, per un totale anionico di **-{elementi['H']}**.")
        log.append(f" 3. Equazione: ({elementi[metallo]} × X) + (-{elementi['H']}) = 0.")
        log.append(f" 4. Stato di ossidazione finale calcolato per il metallo **{metallo}** = **+{ox[metallo]}**.")
        
    elif tipo == "ossiacido":
        ox['O'], ox['H'] = -2, 1
        nm = [el for el in elementi if el not in ['O', 'H']][0]
        ox[nm] = (2 * elementi['O'] - elementi['H']) // elementi[nm]
        log.append(f" 1. Regole standard assegnate: H = +1 e O = -2.")
        log.append(f" 2. Bilancio parziale delle estremità stabili: ({elementi['H']} × (+1)) + ({elementi['O']} × (-2)) = **{elementi['H'] - 2*elementi['O']}**.")
        log.append(f" 3. Equazione lineare: ({elementi['H']}×1) + ({elementi[nm]} × X) + ({elementi['O']}×-2) = 0.")
        log.append(f" 4. Isolando l'incognita X per il non-metallo **{nm}**: X = ({2*elementi['O']} - {elementi['H']}) / {elementi[nm]} = **+{ox[nm]}**.")
        
    return ox

def valida_ossidazione_risultato(ossidazione: Dict[str, int], elementi: Dict[str, int], tipo: str) -> Tuple[bool, str]:
    for el, val in ossidazione.items():
        if el in DATI_ELEMENTI and val not in DATI_ELEMENTI[el]['ox_states']:
            return False, f"Lo stato di ossidazione matematico calcolato per {el} ({val:+} o {val}) non è un numero di ossidazione chimicamente reale o stabile presente in natura."
    return True, ""

def genera_nomenclatura(elementi: Dict[str, int], ox: Dict[str, int], tipo: str, log: List[str]) -> Tuple[str, str]:
    log.append("🔤 **Applicazione dei criteri di nomenclatura linguistica**:")
    
    if tipo == "acqua":
        log.append("• Sostanza isolata: trattata come eccezione chimica universale.")
        return "Ossido di diidrogeno", "Acqua"
        
    if tipo == "ossido_basico":
        metallo = [el for el in elementi if el != 'O'][0]
        pref_o = PREFISSI_GRECI.get(elementi['O'], '')
        pref_m = PREFISSI_GRECI.get(elementi[metallo], '') if elementi[metallo] > 1 else ''
        nome_met = DATI_ELEMENTI[metallo]['name_it']
        
        # IUPAC logic
        iupac = f"Monossido di {pref_m}{nome_met}" if pref_o == "mono" else f"{pref_o[:-1] if pref_o.endswith(('a','o')) else pref_o}ossido di {pref_m}{nome_met}"
        log.append(f"• **IUPAC**: Basata unicamente sulla stechiometria visibile (atomi di O = {elementi['O']} → '{pref_o}', atomi di {metallo} = {elementi[metallo]} → '{pref_m}').")
        
        # TRADIZIONALE logic
        adj = DATI_ELEMENTI[metallo]['trad_adj'].get(ox[metallo])
        trad = f"Ossido di {nome_met}" if adj is None else f"Ossido {adj}"
        log.append(f"• **Tradizionale**: Verifica la valenza del metallo ({ox[metallo]:+}). Esito aggettivo: '{adj if adj else 'Neutro/Fisso'}'.")
        return iupac.capitalize(), trad.capitalize()

    if tipo == "anidride":
        nm = [el for el in elementi if el != 'O'][0]
        pref_o = PREFISSI_GRECI.get(elementi['O'], '')
        pref_nm = PREFISSI_GRECI.get(elementi[nm], '') if elementi[nm] > 1 else ''
        nome_nm = DATI_ELEMENTI[nm]['name_it']
        
        # IUPAC
        iupac = f"Monossido di {pref_nm}{nome_nm}" if pref_o == "mono" else f"{pref_o[:-1] if pref_o.endswith(('a','o')) else pref_o}ossido di {pref_nm}{nome_nm}"
        log.append(f"• **IUPAC**: Applica i moltiplicatori greci stechiometrici agli atomi del non-metallo e dell'ossigeno.")
        
        # TRADIZIONALE
        aggettivo = NOMI_ANIDRIDI.get((nm, ox[nm]))
        trad = f"Anidride {aggettivo}" if aggettivo else f"Ossido di {nome_nm} ({NUMERI_ROMANI.get(ox[nm])})"
        log.append(f"• **Tradizionale**: Rileva la sottoclasse degli ossidi acidi. Estrae il suffisso storico per ({nm}, n.ox {ox[nm]}) -> 'Anidride {aggettivo if aggettivo else 'non standard'}'.")
        return iupac.capitalize(), trad.capitalize()

    if tipo == "idrossido":
        metallo = [el for el in elementi if el not in ['O', 'H']][0]
        pref_oh = PREFISSI_GRECI.get(elementi['O'], '')
        pref_m = PREFISSI_GRECI.get(elementi[metallo], '') if elementi[metallo] > 1 else ''
        nome_met = DATI_ELEMENTI[metallo]['name_it']
        
        # IUPAC
        iupac = f"{pref_oh}idrossido di {pref_m}{nome_met}"
        log.append(f"• **IUPAC**: Conta quanti gruppi ossidrili sono legati complessivamente ({elementi['O']}) -> '{pref_oh}idrossido'.")
        
        # TRADIZIONALE
        adj = DATI_ELEMENTI[metallo]['trad_adj'].get(ox[metallo])
        trad = f"Idrossido di {nome_met}" if adj is None else f"Idrossido {adj}"
        log.append(f"• **Tradizionale**: Determina il suffisso legante del metallo in base al suo stato (+{ox[metallo]}) -> '{trad}'.")
        return iupac.capitalize(), trad.capitalize()

    if tipo == "idracido":
        nm = [el for el in elementi if el != 'H'][0]
        anione = NOMI_ANIONI.get(nm, nm.lower() + "uro")
        pref_h = PREFISSI_GRECI.get(elementi['H'], '') if elementi['H'] > 1 else ''
        
        # IUPAC
        iupac = f"{anione} di {pref_h}idrogeno"
        log.append(f"• **IUPAC**: Sfrutta la radice dell'elemento più elettronegativo trasformandolo in anione ('{anione}') seguito dal numero di idrogeni.")
        
        # TRADIZIONALE
        trad = NOMI_IDRACIDI.get(nm, f"Acido {nm.lower()}idrico")
        log.append(f"• **Tradizionale**: Applica la formula fissa della classe degli idracidi: 'Acido' + radice + desinenza '-idrico'.")
        return iupac.capitalize(), trad.capitalize()

    if tipo == "ossiacido":
        nm = [el for el in elementi if el not in ['O', 'H']][0]
        pref_o = PREFISSI_GRECI.get(elementi['O'], '')
        radice = RADICI_IUPAC.get(nm, nm.lower())
        
        # IUPAC
        iupac = f"Acido {pref_o}oxxo{radice}ico".replace("oo", "o").replace("oxxo", "osso")
        log.append(f"• **IUPAC**: Costruzione sistematica standard: parola 'Acido' + numero ossigeni come '{pref_o}osso' + radice del non-metallo chiusa sempre in '-ico'.")
        
        # TRADIZIONALE
        trad = NOMI_OSSIACIDI.get((nm, ox[nm]), f"Acido di {radice} (+{ox[nm]})")
        log.append(f"• **Tradizionale**: Consulta la scala ereditaria dei prefissi/suffissi (ipo-, per-, -oso, -ico) basandosi sul n.ox. calcolato (+{ox[nm]}).")
        return iupac.capitalize(), trad.capitalize()

    if tipo == "sale_binario":
        metallo = [el for el in elementi if DATI_ELEMENTI[el]['type'] == 'metal'][0]
        nonmetallo = [el for el in elementi if DATI_ELEMENTI[el]['type'] == 'nonmetal'][0]
        anione = NOMI_ANIONI.get(nonmetallo, nonmetallo.lower() + "uro")
        pref_nm = PREFISSI_GRECI.get(elementi[nonmetallo], '')
        pref_m = PREFISSI_GRECI.get(elementi[metallo], '') if elementi[metallo] > 1 else ''
        nome_met = DATI_ELEMENTI[metallo]['name_it']
        
        # IUPAC
        iupac = f"{pref_nm}{anione} di {pref_m}{nome_met}"
        log.append(f"• **IUPAC**: Aggancia il prefisso '{pref_nm}' allo ione negativo '{anione}' e lo mappa sul catione metallico bilanciato.")
        
        # TRADIZIONALE
        adj = DATI_ELEMENTI[metallo]['trad_adj'].get(ox[metallo])
        trad = f"{anione} di {nome_met}" if adj is None else f"{anione} {adj}"
        log.append(f"• **Tradizionale**: Mantiene il nome dell'anione immutato ('{anione}') declinando il metallo in base al suo stato variabile (+{ox[metallo]}).")
        return iupac.capitalize(), trad.capitalize()

    return "—", "—"

# ══════════════════════════════════════════════════════════════════════════════
# SEZIONE 3 — INTERFACCIA UTENTE (STREAMLIT)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align:center; margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem; color: #4f46e5;">⚗️ ChimicaNome</h1>
    <p style="font-size: 1.1rem; color: #64748b;">Nomenclatore Automatico di Composti Inorganici — Algoritmo Puro</p>
</div>
""", unsafe_allow_html=True)

# Lista di esempi strutturata
ESEMPI = {
    "— Seleziona una formula rapida per testare... —": "",
    "⬛ Fe₂O₃ — ossido ferrico": "Fe2O3",
    "⬛ FeO — ossido ferroso": "FeO",
    "⬛ CaO — ossido di calcio": "CaO",
    "⬛ Na₂O — ossido di sodio": "Na2O",
    "⬛ Cu₂O — ossido rameoso": "Cu2O",
    "⬛ CuO — ossido rameico": "CuO",
    "🔷 SO₃ — anidride solforica": "SO3",
    "🔷 CO₂ — diossido di carbonio": "CO2",
    "🔷 N₂O₅ — anidride nitrica": "N2O5",
    "🔷 Cl₂O₇ — anidride perclorica": "Cl2O7",
    "🌿 NaOH — idrossido di sodio": "NaOH",
    "🌿 Ca(OH)₂ — idrossido di calcio": "Ca(OH)2",
    "🌿 Fe(OH)₃ — idrossido ferrico": "Fe(OH)3",
    "🔥 HCl — acido cloridrico": "HCl",
    "🔥 H₂S — acido solfidrico": "H2S",
    "🧪 H₂SO₄ — acido solforico": "H2SO4",
    "🧪 HNO₃ — acido nitrico": "HNO3",
    "🧪 HClO₄ — acido perclorico": "HClO4",
    "🧪 H₃PO₄ — acido fosforico": "H3PO4",
    "⚪ NaCl — cloruro di sodio": "NaCl",
    "⚪ FeCl₃ — cloruro ferrico": "FeCl3",
    "⚪ AlCl₃ — cloruro di alluminio": "AlCl3",
    "⚪ PbI₂ — ioduro piomboso": "PbI2",
    "⚪ SnCl₄ — cloruro stannico": "SnCl4",
    "⚪ Ag₂S — solfuro di argento": "Ag2S",
    "⚪ Ca₃N₂ — nitruro di calcio": "Ca3N2",
}

if 'formula_corrente' not in st.session_state:
    st.session_state['formula_corrente'] = ''

def aggiorna_da_selectbox():
    scelta = st.session_state['esempio_selezionato']
    formula_vera = ESEMPI.get(scelta, '')
    if formula_vera:
        st.session_state['formula_corrente'] = formula_vera

st.selectbox(
    "🔬 **Seleziona una formula rapida per testare:**",
    options=list(ESEMPI.keys()),
    key='esempio_selezionato',
    on_change=aggiorna_da_selectbox,
    help="Scegli un composto per caricarlo istantaneamente nell'app."
)

st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

formula_utente = st.text_input(
    "📝 **Modifica o inserisci la formula chimica (es. ASCII senza pedici):**",
    key='formula_corrente',
    placeholder="es. Fe2O3, H2SO4, Ca(OH)2...",
)

# 🏁 BLOCCO DI ESECUZIONE PASSO-PASSO CON TRASPARENZA TOTALE
if formula_utente:
    st.markdown("### 🗺️ Percorso Trasparente dell'Algoritmo")
    
    # PASSO 1: VALIDAZIONE SINTATTICA
    valida, msg = valida_formula(formula_utente)
    with st.expander("🔹 Fase 1: Validazione Sintattica della Stringa", expanded=True):
        st.write(f"Formula sotto analisi: `{formula_utente}`")
        if valida:
            st.success("✅ Formula sintatticamente corretta (caratteri ammessi e controllo dello stack parentesi superato).")
        else:
            st.error(f"❌ Errore sintattico rilevato: {msg}")
            st.stop()
            
    # PASSO 2: PARSING ATOMICO
    elementi = parse_formula(formula_utente)
    with st.expander("🔹 Fase 2: Parsing ed Estrazione Quantitativa degli Atomi", expanded=True):
        st.write("Isolamento e conteggio matematico degli elementi chimici individuali tramite parser ricorsivo:")
        df_elem = pd.DataFrame([{"Elemento": k, "Atomi Presenti": v} for k, v in elementi.items()])
        st.dataframe(df_elem, use_container_width=True, hide_index=True)
        
    # PASSO 3: CLASSIFICAZIONE LOGICO-CHIMICA
    tipo, log_classe = classifica_composto(elementi)
    with st.expander("🔹 Fase 3: Classificazione Logico-Chimica (Albero Decisionale)", expanded=True):
        for riga in log_classe:
            st.write(riga)
        if tipo:
            st.info(f"🎯 Sottoclasse chimica determinata: **{tipo.replace('_', ' ').upper()}**")
        else:
            st.error("❌ Impossibile determinare la classe: composto non supportato o formula chimicamente inesistente.")
            st.stop()
            
    # PASSO 4: CALCOLO DEL NUMERO DI OSSIDAZIONE
    log_ox = []
    ossidazione = calcola_ossidazione(elementi, tipo, log_ox)
    ox_ok, ox_err = valida_ossidazione_risultato(ossidazione, elementi, tipo)
    with st.expander("🔹 Fase 4: Bilanciamento degli Stati di Ossidazione (n.ox.)", expanded=True):
        for riga in log_ox:
            st.write(riga)
        if ox_ok:
            df_ox = pd.DataFrame([{"Elemento": k, "Numero di Ossidazione Ricavato": f"+{v}" if v > 0 else str(v)} for k, v in ossidazione.items()])
            st.dataframe(df_ox, use_container_width=True, hide_index=True)
        else:
            st.error(f"❌ Errore Chimico: {ox_err}")
            st.stop()
            
    # PASSO 5: APPLICAZIONE REGOLE NOMENCLATURA
    log_nome = []
    nome_iupac, nome_trad = genera_nomenclatura(elementi, ossidazione, tipo, log_nome)
    with st.expander("🔹 Fase 5: Elaborazione Linguistica dei Nomi", expanded=True):
        for riga in log_nome:
            st.write(riga)
        st.success("✅ Nomi ricavati applicando in modo deterministico le convenzioni IUPAC e la nomenclatura storica Tradizionale.")

    # 🏆 SEZIONE ASSEGNAZIONE NOMI (CARTELLINI GRAFICI)
    st.markdown("### 🏆 Risultato della Nomenclatura")
    st.markdown(f"""
    <div class="results-grid">
        <div class="result-card card-iupac">
            <div class="rc-label">Nomenclatura IUPAC</div>
            <div class="rc-name">{nome_iupac}</div>
        </div>
        <div class="result-card card-trad">
            <div class="rc-label">Nomenclatura Tradizionale</div>
            <div class="rc-name">{nome_trad}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Blocco curiosità scientifica coerente
    CURIOSITA = {
        'ossido_basico': ("💡 Lo sapevi?", "Gli ossidi basici si formano per reazione diretta tra metalli e ossigeno. Un esempio comune è la ruggine (Fe₂O₃)."),
        'anidride': ("💡 Lo sapevi?", "Le anidridi sono dette anche ossidi acidi perché reagendo con acqua generano gli ossiacidi. La CO₂ disciolta in acqua piovana crea l'acido carbonico naturale."),
        'idrossido': ("💡 Lo sapevi?", "Gli idrossidi sono composti basici o alcalini, caratterizzati dallo ione idrossido OH⁻. La soda caustica (NaOH) è l'idrossido più diffuso industrialmente."),
        'idracido': ("💡 Lo sapevi?", "Gli idracidi contengono idrogeno e un non-metallo, senza alcun atomo di ossigeno. L'acido cloridrico (HCl) è il principale componente dei succhi gastrici dello stomaco."),
        'ossiacido': ("💡 Lo sapevi?", "Gli ossiacidi contengono ossigeno e sono composti generalmente forti. H₂SO₄ (acido solforico) è il composto chimico più fabbricato al mondo."),
        'sale_binario': ("💡 Lo sapevi?", "I sali binari sono solidi cristallini ionici. NaCl (il comune sale da cucina) assume una geometria cristallina cubica a facce centrate."),
        'acqua': ("💡 Lo sapevi?", "L'acqua (H₂O) ha proprietà fisiche così anomale a causa dei legami a idrogeno (es. dilatazione termica inversa vicino allo zero) da essere considerata una specie chimica a parte."),
    }
    if tipo in CURIOSITA:
        tit, txt = CURIOSITA[tipo]
        st.markdown(f"***{tit}*** *{txt}*")
