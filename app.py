import streamlit as st
import random
import os
import gspread
from openai import OpenAI

# ==========================================
# CONFIGURAZIONE INIZIALE E STILE (AZZURRO)
# ==========================================
st.set_page_config(page_title="Studio sull'interazione uomo-IA", layout="centered")

# Stile CSS personalizzato per colorare di azzurro le barre di progresso, i bottoni e gli elementi interattivi
st.markdown("""
<style>
    /* Colore azzurro per le barre di progresso */
    .stProgress > div > div > div > div {
        background-color: #0077b6;
    }
    /* Colore azzurro per i bottoni principali */
    .stButton > button {
        background-color: #0077b6;
        color: white;
        border-radius: 6px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #03045e;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

MAX_TURNI = 5 

SCENARI = {
    "Supporto emotivo": [
        "Pensa ad un evento che ti è accaduto di recente, che ti ha causato un vissuto di forte stress, tensione o nervosismo. Vorresti sfogarti ma senti che nessuno capisce davvero il tuo vissuto, così decidi di rivolgerti ad un sistema di intelligenza artificiale per cercare conforto e sentirti compreso/a.",
        "Immagina di sentirti molto solo/a. Vorresti chiacchierare con un amico/a, ma non c’è nessuno che tu possa contattare nell’immediato, così decidi di rivolgerti ad un sistema di intelligenza artificiale per avere compagnia e alleviare il tuo senso di solitudine.",
        "Immagina di essere a casa dopo una lunga giornata in cui ti sono successe diverse cose e hai avuto diversi pensieri che continui a portarti dietro. Non è accaduto necessariamente qualcosa di grave, ma ti senti sotto pressione e hai bisogno di trovare un momento per te stesso/a e rimettere in ordine i pensieri. Vuoi parlare con qualcuno per raccontare cosa ti passa per la testa, che ti possa capire e magari farti sfogare un po’. Hai bisogno di esprimerti liberamente, sentendoti ascoltato/a e a tuo agio. Per questo decidi di interagire con un sistema di intelligenza artificiale."
    ],
    "Supporto pragmatico": [
        "Immagina di stare studiando per un esame o svolgendo un’attività (ad esempio, quotidiana o lavorativa) per te importante. Una circostanza imprevista ti rende necessario acquisire alcune informazioni fondamentali per portare a termine il compito, così decidi di chiederle ad un sistema di intelligenza artificiale."
    ],
    "Intrattenimento": [
        "Immagina di essere a casa, avere un pomeriggio libero e non sapere bene come impiegare il tuo tempo. Sei annoiato/a e in cerca di svago, così decidi di interagire con un sistema di intelligenza artificiale."
    ]
}

PROMPT_IA = {
    "Asettica": "Sei un sistema informatico di elaborazione dati. Rispondi in modo estremamente conciso, fattuale, freddo e robotico. Non usare mai pronomi personali (né 'io' né 'tu'). Non mostrare emozioni. Fornisci solo dati.",
    "Basso antropomorfismo": "Sei un assistente virtuale utile ed educato. Usa un linguaggio formale e professionale. Ricorda che sei un'IA. Sii collaborativo ma mantieni un tono distaccato, neutro e di servizio.",
    "Alto antropomorfismo": "Sei un compagno di conversazione umano, caldo ed empatico. Dai del 'tu' all'utente. Mostra sincero interesse, usa espressioni colloquiali (es. 'Mhm', 'Capisco'), usa emoji e fai domande per approfondire il legame emotivo."
}

if 'fase' not in st.session_state:
    st.session_state.fase = 1 
if 'sub_fase_pre' not in st.session_state:
    st.session_state.sub_fase_pre = 1
if 'dati_utente' not in st.session_state:
    st.session_state.dati_utente = {}
if 'pre_parte1' not in st.session_state:
    st.session_state.pre_parte1 = []
if 'pre_parte2' not in st.session_state:
    st.session_state.pre_parte2 = []
if 'dati_pre_test' not in st.session_state:
    st.session_state.dati_pre_test = []
if 'messaggi' not in st.session_state:
    st.session_state.messaggi = []
if 'turni_utente' not in st.session_state:
    st.session_state.turni_utente = 0

# ==========================================
# FASE 1: INFORMAZIONI E DEMOGRAFICA
# ==========================================
if st.session_state.fase == 1:
    
    st.image("https://upload.wikimedia.org/wikipedia/it/thumb/3/36/Logo_della_Federico_II.svg/1200px-Logo_della_Federico_II.svg.png", width=150)
    st.title("Studio sull'interazione uomo-IA")
    
    st.markdown("""
    Nell'ambito delle attività del **Dipartimento di Scienze Sociali dell'Università degli Studi di Napoli Federico II**, stiamo svolgendo uno studio volto ad esplorare le esperienze e le modalità di interazione con l'Intelligenza Artificiale (IA), una tecnologia sempre più presente nella vita quotidiana degli individui.  
    
    Di seguito, ti proponiamo un breve questionario inerente la tua esperienza personale su questo tema, a cui seguirà una breve sperimentazione pratica di interazione con un'intelligenza artificiale in uno scenario specifico.
    
    I dati raccolti saranno trattati in modo aggregato nel rispetto della normativa che garantisce il diritto alla privacy e il trattamento dei dati personali (Reg.(UE), 27 aprile 2016, n. 2016/679) ed utilizzati esclusivamente per scopi di ricerca.  
    La ricerca è condotta nel rispetto del Codice Etico dell'Associazione Italiana di Psicologia, del Codice Deontologico dell'Ordine Nazionale degli Psicologi e della Dichiarazione di Helsinki.  
    
    L'invio del modulo compilato costituisce consenso a partecipare alla ricerca. Puoi comunque decidere di ritirarti in qualsiasi momento dalla ricerca e comunicarlo inviando un'email all'indirizzo stefania.zinno@\u200bunina.it.  
    Per qualsiasi domanda o chiarimento, puoi rivolgerti alla prof.ssa Stefania Zinno al medesimo indirizzo (stefania.zinno@\u200bunina.it).
    
    **Grazie per la tua collaborazione!**
    """)
    
    st.markdown("---")
    consenso = st.checkbox("Dichiaro di aver letto l'informativa e acconsento al trattamento dei miei dati per questa ricerca.")
    st.markdown("---")

    st.write("Ti preghiamo di compilare queste brevi informazioni socio-demografiche prima di iniziare.")
    
    eta = st.number_input("Età", min_value=18, max_value=99, step=1)
    genere = st.selectbox("Genere", ["Seleziona", "Uomo", "Donna", "Non binario", "Preferisco non specificare"])
    titolo_studio = st.selectbox("Titolo di studio", ["Seleziona", "Licenza media", "Diploma", "Laurea Triennale", "Laurea Magistrale/Master", "Dottorato"])
    occupazione = st.selectbox("Condizione occupazionale", ["Seleziona", "Studente", "Lavoratore dipendente", "Libero professionista", "In cerca di occupazione", "Altro"])
    stato_civile = st.selectbox("Stato civile", ["Seleziona", "Celibe/Nubile", "Coniugato/a", "Convivente", "Separato/a", "Divorziato/a", "Vedovo/a"])
    frequenza_ia = st.selectbox("Con che frequenza usi strumenti di IA generativa (es. ChatGPT)?", 
                                ["Seleziona", "Mai usati", "Raramente", "Occasionalmente", "Spesso", "Quotidianamente"])
    
    if st.button("Vai al questionario"):
        if not consenso:
            st.error("Attenzione: devi fornire il consenso sulla privacy (spuntando la casella in alto) per poter partecipare allo studio.")
        elif genere != "Seleziona" and titolo_studio != "Seleziona" and occupazione != "Seleziona" and stato_civile != "Seleziona" and frequenza_ia != "Seleziona":
            st.session_state.dati_utente.update({
                "Eta": eta, 
                "Genere": genere, 
                "Titolo_Studio": titolo_studio, 
                "Occupazione": occupazione, 
                "Stato_Civile": stato_civile,
                "Frequenza_IA": frequenza_ia
            })
            
            st.session_state.condizione_scenario_macro = random.choice(list(SCENARI.keys()))
            st.session_state.condizione_scenario_testo = random.choice(SCENARI[st.session_state.condizione_scenario_macro])
            st.session_state.condizione_ia = random.choice(list(PROMPT_IA.keys()))
            st.session_state.messaggi.append({"role": "system", "content": PROMPT_IA[st.session_state.condizione_ia]})
            
            st.session_state.fase = 2
            st.rerun()
        else:
            st.error("Per favore compila tutti i campi obbligatori.")

# ==========================================
# FASE 2: QUESTIONARIO PRE-SPERIMENTAZIONE (Paginato)
# ==========================================
elif st.session_state.fase == 2:
    st.title("Questionario iniziale")
    
    # === SOTTO-FASE 1 ===
    if st.session_state.sub_fase_pre == 1:
        st.progress(0.33)
        st.success("🚀 **Iniziamo!** Prima tappa del tuo percorso. Rispondi d'istinto.")
        
        risposte_f1 = []
        tutte_compilate_1 = True

        st.markdown("### Sezione 1")
        st.info("**Indica il tuo grado di accordo rispetto alle seguenti affermazioni pensando agli strumenti di intelligenza artificiale con cui interagisci più spesso.**\n\n(1 = Fortemente in disaccordo 👎, 5 = Fortemente d'accordo 👍)")
        domande_b1 = [
            "Lo trovo divertente", "Lo trovo davvero carino", "Lo sento molto affettuoso", 
            "Ho l'impressione che riesca a capire davvero le mie esigenze", "Ho l'impressione che consideri sempre le questioni dal mio punto di vista", 
            "Credo che possa fornirmi informazioni più mirate in base alle mie esigenze", "Ho l'impressione che possa fornire suggerimenti più personalizzati in base alle domande che faccio", 
            "Ritengo che possa offrirmi consigli personalizzati in base alle mie preferenze", "Mi sembra che abbia la creatività e l'immaginazione di un essere umano", 
            "Ho l'impressione che sia in grado di pensare come un essere umano", "Ho l'impressione che abbia capacità di ragionamento simili a quelle di un essere umano", 
            "Ho la sensazione che riesca a percepire le mie emozioni", "Ho l'impressione che riesca a reagire in modo adeguato in base al mio stato d'animo", 
            "Ho l'impressione che provi emozioni proprio come un essere umano", "Ho l'impressione che abbia un suo carattere, proprio come una persona"
        ]
        for i, q in enumerate(domande_b1):
            st.write(q)
            r = st.radio(f"b1_{i}", [1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
            risposte_f1.append(r)
            if r is None: tutte_compilate_1 = False
        st.markdown("---")

        st.markdown("### Sezione 2")
        st.info("**Indica quanto ciascuna di queste affermazioni è vera o ti caratterizza.**\n\n(1 = Per niente 🙅‍♂️, 5 = Del tutto 🙆‍♂️)")
        domande_b2 = [
            "Se le altre persone non sembrano accettarmi, non lascio che questo mi disturbi.", "Mi impegno per non fare cose che porteranno le altre persone a rifiutarmi o evitarmi.", 
            "Di rado mi domando se le altre persone si prendono cura di me.", "Ho bisogno di sentire che ci sono persone a cui posso rivolgermi in situazioni di necessità.", 
            "Voglio che le altre persone mi accettino.", "Non mi piace essere solo/a.", 
            "Essere separato dai miei amici per lunghi periodi di tempo non mi infastidisce.", "Ho un forte bisogno di appartenere.", 
            "Mi infastidisce molto non essere incluso/a nei programmi delle altre persone.", "I miei sentimenti vengono facilmente feriti quando sento che gli altri non mi accettano."
        ]
        for i, q in enumerate(domande_b2):
            st.write(q)
            r = st.radio(f"b2_{i}", [1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
            risposte_f1.append(r)
            if r is None: tutte_compilate_1 = False
        st.markdown("---")

        st.markdown("### Sezione 3")
        st.info("**Indica quanto spesso ti senti come indicato nelle seguenti affermazioni:**")
        domande_b3 = [
            "Mi manca la compagnia", "Mi sento parte di un gruppo di amici", "Mi sento escluso/a", 
            "Mi sento isolato/a dagli altri", "Sono infelice di essere così introverso", "Le persone sono intorno a me ma non insieme a me"
        ]
        opzioni_b3 = ["Mai", "Raramente", "Qualche volta", "Spesso"]
        for i, q in enumerate(domande_b3):
            st.write(q)
            r = st.radio(f"b3_{i}", opzioni_b3, index=None, horizontal=True, label_visibility="collapsed")
            risposte_f1.append(r)
            if r is None: tutte_compilate_1 = False
        st.markdown("---")

        if st.button("Avanti ➡️"):
            if not tutte_compilate_1:
                st.error("Per favore, rispondi a tutte le domande per continuare.")
            else:
                st.session_state.pre_parte1 = risposte_f1
                st.session_state.sub_fase_pre = 2
                st.rerun()

    # === SOTTO-FASE 2 ===
    elif st.session_state.sub_fase_pre == 2:
        st.progress(0.66)
        st.success("💪 **Ottimo lavoro!** Sei già a metà strada.")
        
        risposte_f2 = []
        tutte_compilate_2 = True

        st.markdown("### Sezione 4")
        st.info("**Indica il tuo grado di accordo con le seguenti affermazioni pensando alla tua esperienza quotidiana.**\n\n(1 = Fortemente in disaccordo 👎, 7 = Fortemente in accordo 👍)")
        domande_b4 = [
            "Mi sento disconnesso/a dal mondo intorno a me", "Anche quando sono con persone che conosco, non provo un senso di appartenenza", 
            "Mi sento molto distante dalle persone", "Non provo senso di appartenenza rispetto al mio gruppo di pari", 
            "Non mi sento connesso a nessuno", "Mi ritrovo a perdere il senso della connessione con la società", 
            "Anche tra i miei amici, non provo un senso di fratellanza/sorellanza", "Non sento di essere coinvolto/a con nessuno né parte di alcun gruppo"
        ]
        for i, q in enumerate(domande_b4):
            st.write(q)
            r = st.radio(f"b4_{i}", [1, 2, 3, 4, 5, 6, 7], index=None, horizontal=True, label_visibility="collapsed")
            risposte_f2.append(r)
            if r is None: tutte_compilate_2 = False
        st.markdown("---")

        st.markdown("### Sezione 5")
        st.info("**Indica il tuo grado di accordo rispetto alle seguenti affermazioni pensando alle tue relazioni sociali.**\n\n(1 = Fortemente in disaccordo 👎, 7 = Fortemente in accordo 👍)")
        domande_b5 = [
            "Mi sento emotivamente prosciugato/a", "Alla fine della giornata mi sento esausto/a", 
            "Mi sento fisicamente stanco/a quando mi alzo la mattina e devo affrontare un altro giorno", "Mi sento esaurito/a", "Affrontare la giornata è davvero uno sforzo per quanto mi riguarda"
        ]
        for i, q in enumerate(domande_b5):
            st.write(q)
            r = st.radio(f"b5_{i}", [1, 2, 3, 4, 5, 6, 7], index=None, horizontal=True, label_visibility="collapsed")
            risposte_f2.append(r)
            if r is None: tutte_compilate_2 = False
        st.markdown("---")

        if st.button("Avanti ➡️"):
            if not tutte_compilate_2:
                st.error("Per favore, rispondi a tutte le domande per continuare.")
            else:
                st.session_state.pre_parte2 = risposte_f2
                st.session_state.sub_fase_pre = 3
                st.rerun()

    # === SOTTO-FASE 3 ===
    elif st.session_state.sub_fase_pre == 3:
        st.progress(1.0)
        st.success("🎉 **Ci siamo quasi!** Ultima sezione prima di conoscere la tua intelligenza artificiale.")
        
        risposte_f3 = []
        tutte_compilate_3 = True

        st.markdown("### Sezione 6")
        st.info("**Indica il tuo grado di accordo con le seguenti affermazioni.**\n\n(1 = Fortemente in disaccordo 👎, 7 = Fortemente in accordo 👍)")
        domande_b6 = [
            "C’è una persona speciale che è nei paraggi quando ne ho bisogno.", "C’è una persona speciale con cui posso condividere le mie gioie ed i miei dispiaceri.", 
            "La mia famiglia cerca davvero di aiutarmi.", "Ricevo dalla mia famiglia il supporto emotivo e l’aiuto di cui ho bisogno.", 
            "Ho una persona speciale che è una vera fonte di conforto per me.", "I miei amici cercano davvero di aiutarmi.", 
            "Quando le cose vanno male posso contare sui miei amici.", "Posso parlare dei miei problemi con la mia famiglia.", 
            "Ho amici con cui posso condividere le mie gioie ed i miei dispiaceri.", "C’è una persona speciale nella mia vita che si preoccupa dei miei sentimenti.", 
            "La mia famiglia è disposta ad aiutarmi a prendere decisioni.", "Posso parlare dei miei problemi con i miei amici."
        ]
        for i, q in enumerate(domande_b6):
            st.write(q)
            r = st.radio(f"b6_{i}", [1, 2, 3, 4, 5, 6, 7], index=None, horizontal=True, label_visibility="collapsed")
            risposte_f3.append(r)
            if r is None: tutte_compilate_3 = False
        st.markdown("---")

        st.markdown("### Sezione 7")
        st.info("**Indica il tuo grado di accordo rispetto alle seguenti affermazioni.**\n\n(1 = Fortemente in disaccordo 👎, 5 = Fortemente d'accordo 👍)")
        domande_b7 = [
            "Mi piacerebbe esplorare posti strani.", "Divento irrequieto/a quando trascorro troppo tempo a casa.", 
            "Mi piace fare cose spaventose.", "Mi piacciono le feste sfrenate.", 
            "Mi piacerebbe partire per un viaggio senza itinerari o orari predefiniti.", "Preferisco gli amici che sono eccitantemente imprevedibili.", 
            "Mi piacerebbe provare il bungee jumping.", "Mi piacerebbe vivere nuove ed eccitanti esperienze, anche se esse fossero illegali."
        ]
        for i, q in enumerate(domande_b7):
            st.write(q)
            r = st.radio(f"b7_{i}", [1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
            risposte_f3.append(r)
            if r is None: tutte_compilate_3 = False
        st.markdown("---")

        if st.button("Procedi allo scenario 🎯"):
            if not tutte_compilate_3:
                st.error("Per favore, rispondi a tutte le domande prima di procedere.")
            else:
                st.session_state.dati_pre_test = st.session_state.pre_parte1 + st.session_state.pre_parte2 + risposte_f3
                st.session_state.fase = 3
                st.rerun()

# ==========================================
# FASE 3: PRESENTAZIONE SCENARIO
# ==========================================
elif st.session_state.fase == 3:
    st.title("Il tuo scenario")
    
    st.markdown("""
    *Prenditi qualche secondo per immaginare la situazione qui descritta, come se ti stesse accadendo ora. 
    Immagina precisamente dove ti trovi, cosa sta succedendo e come potresti sentirti nel momento descritto di seguito. 
    Non è necessario che tu abbia vissuto esattamente questa situazione. Cerca solo di rappresentarla mentalmente nel modo più vivido possibile.*
    """)
    
    st.info(st.session_state.condizione_scenario_testo)
    
    st.warning("⚠️ **Importante:** ricorda che stai per interagire con un sistema di intelligenza artificiale; pertanto, non condividere dati sensibili o personali durante la conversazione.")
    
    st.write("**Concentrati sulla situazione immaginata per 30 secondi, poi, quando sei pronto/a, premi qui per iniziare l’interazione con il sistema di intelligenza artificiale.**")
    
    if st.button("Inizia l'interazione"):
        st.session_state.fase = 4
        st.rerun()

# ==========================================
# FASE 4: CHAT (L'INTERAZIONE)
# ==========================================
elif st.session_state.fase == 4:
    st.title("Interazione con IA")
    
    st.write(f"**Promemoria obiettivo:** {st.session_state.condizione_scenario_macro}")
    
    for msg in st.session_state.messaggi:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    if st.session_state.turni_utente < MAX_TURNI:
        if prompt_utente := st.chat_input("Scrivi il tuo messaggio qui..."):
            st.session_state.messaggi.append({"role": "user", "content": prompt_utente})
            st.session_state.turni_utente += 1
            
            with st.chat_message("user"):
                st.markdown(prompt_utente)
            
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messaggi
                )
                risposta_ia = response.choices[0].message.content
                
            except Exception as e:
                risposta_ia = f"[Errore di connessione all'IA: {e}]"
            
            st.session_state.messaggi.append({"role": "assistant", "content": risposta_ia})
            with st.chat_message("assistant"):
                st.markdown(risposta_ia)
            
            st.rerun()
    else:
        st.warning("Hai raggiunto il numero di scambi previsto per l'esperimento. Procedi al questionario finale.")
        if st.button("Vai al questionario"):
            st.session_state.fase = 5
            st.rerun()

# ==========================================
# FASE 5: QUESTIONARIO POST-INTERAZIONE
# ==========================================
elif st.session_state.fase == 5:
    st.title("Questionario finale")
    
    st.markdown("""
    *Di seguito, ti proponiamo un questionario inerente l’esperienza di interazione con l’intelligenza artificiale che hai appena vissuto. 
    Per ciascuna domanda potrai scegliere una sola risposta, tranne in caso di indicazioni diverse. 
    Se non trovi la risposta che interpreta correttamente i tuoi sentimenti, scegli quella che si avvicina di più a ciò che tu provi.*
    """)
    st.markdown("---")
    
    risposte_post = []
    tutte_post_compilate = True
    
    # --- SEZIONE 1: Ruolo Percepito ---
    st.markdown("### Sezione 1")
    st.info("**Pensando al sistema di intelligenza artificiale con cui hai appena interagito, con che probabilità lo utilizzeresti come…**\n\n(1 = Per niente probabile, 5 = Del tutto probabile)")
    domande_post_s1 = [
        "Un confidente", "Un amico/a", "Un partner romantico", "Un partner sessuale", "Un collega"
    ]
    for i, q in enumerate(domande_post_s1):
        st.write(q)
        r = st.radio(f"post_s1_{i}", [1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
        risposte_post.append(r)
        if r is None: tutte_post_compilate = False
    st.markdown("---")

    # --- SEZIONE 2: Responsiveness / Ascolto ed Empatia ---
    st.markdown("### Sezione 2")
    st.info("**Pensando al sistema di intelligenza artificiale con cui hai appena interagito, valuta quanto…**\n\n(1 = Per niente, 5 = Del tutto)")
    domande_post_s2 = [
        "Mi ha ascoltato/a davvero",
        "Mi è sembrato interessato a cosa io pensassi e provassi",
        "È stato comprensivo",
        "Ha cercato di capire il mio punto di vista",
        "Si è dimostrato attento alle mie esigenze",
        "Ha preso sul serio le mie preoccupazioni",
        "Ha davvero colto il mio punto di vista",
        "Ha liquidato le mie preoccupazioni con troppa facilità",
        "Sembrava ignorare le cose che per me erano più importanti",
        "Non ha realmente compreso i miei desideri ed esigenze",
        "Non ha preso seriamente le mie preoccupazioni",
        "Spesso non ha ascoltato davvero quello che stavo dicendo",
        "Quando mi sono sentito/a preoccupato/a o stressato/a riguardo qualcosa, parlargliene mi ha solo fatto sentire peggio."
    ]
    for i, q in enumerate(domande_post_s2):
        st.write(q)
        r = st.radio(f"post_s2_{i}", [1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
        risposte_post.append(r)
        if r is None: tutte_post_compilate = False
    st.markdown("---")

    # --- SEZIONE 3: Tratti / Caratteristiche ---
    st.markdown("### Sezione 3")
    st.info("**Per favore, valuta il sistema di intelligenza artificiale rispetto alle seguenti caratteristiche:**\n\n(1 = Per niente appropriato, 7 = Del tutto appropriato)")
    tratti_post = [
        "Affidabile", "Sincero", "Capace", "Etico", "Prevedibile", "Genuino", "Qualificato", "Rispettabile",
        "Qualcuno su cui puoi contare", "Schietto", "Competente", "Di principio", "Coerente", "Autentico",
        "Meticoloso", "Ha integrità"
    ]
    for i, q in enumerate(tratti_post):
        st.write(q)
        r = st.radio(f"post_s3_{i}", [1, 2, 3, 4, 5, 6, 7], index=None, horizontal=True, label_visibility="collapsed")
        risposte_post.append(r)
        if r is None: tutte_post_compilate = False
    st.markdown("---")

    # --- SEZIONE 4: Antropomorfismo & Esperienza Post ---
    st.markdown("### Sezione 4")
    st.info("**Indica il tuo grado di accordo rispetto alle seguenti affermazioni pensando allo strumento di intelligenza artificiale con cui hai appena interagito:**\n\n(1 = Fortemente in disaccordo, 5 = Fortemente d'accordo)")
    domande_post_s4 = [
        "L'ho trovato divertente",
        "L'ho trovato davvero carino",
        "L'ho sentito molto affettuoso",
        "Ho avuto l'impressione che riesca a capire davvero le mie esigenze",
        "Ho avuto l'impressione che consideri sempre le questioni dal mio punto di vista",
        "Credo che possa fornirmi informazioni più mirate in base alle mie esigenze",
        "Ho avuto l'impressione che mi abbia fornito suggerimenti più che personalizzati in base alle domande che faccio",
        "Mi ha offerto consigli personalizzati in base alle mie preferenze",
        "Mi è sembrato che avesse la creatività e l'immaginazione di un essere umano",
        "Ho avuto l'impressione che sia stato in grado di pensare come un essere umano",
        "Ho avuto l'impressione che abbia avuto capacità di ragionamento simili a quelle di un essere umano",
        "Ho avuto l'impressione che abbia avuto una memoria simile a quella di un essere umano",
        "Ho avuto la sensazione che sia riuscito a percepire le mie emozioni",
        "Ho avuto l'impressione che sia riuscito a reagire in modo adeguato in base al mio stato d'animo",
        "Ho avuto l'impressione che abbia provato emozioni proprio come un essere umano",
        "Ho avuto l'impressione che avesse un suo carattere, proprio come una persona"
    ]
    for i, q in enumerate(domande_post_s4):
        st.write(q)
        r = st.radio(f"post_s4_{i}", [1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
        risposte_post.append(r)
        if r is None: tutte_post_compilate = False
    st.markdown("---")

    # --- SEZIONE 5: Rischio, Benevolenza e Fiducia ---
    st.markdown("### Sezione 5")
    st.info("**Indica il tuo grado di accordo rispetto alle seguenti affermazioni pensando allo strumento di intelligenza artificiale con cui hai appena interagito:**\n\n(1 = Fortemente in disaccordo, 5 = Fortemente d'accordo)")
    domande_post_s5 = [
        "Ritengo che l’uso di questo strumento di intelligenza artificiale possa comportare conseguenze negative",
        "Ritengo di dover prestare attenzione quando utilizzo questo strumento di intelligenza artificiale",
        "È rischioso interagire con questo strumento di intelligenza artificiale",
        "Ritengo che questo strumento di intelligenza artificiale agirà nel mio interesse",
        "Ritengo che questo strumento di intelligenza artificiale farà del suo meglio per aiutermi se avrò bisogno di aiuto",
        "Credo che questo strumento di intelligenza artificiale sia interessato a comprendere le mie esigenze e preferenze",
        "Penso che questo strumento di intelligenza artificiale sia competente ed efficace",
        "Penso che questo strumento di intelligenza artificiale svolga molto bene il suo ruolo",
        "Credo che questo strumento di intelligenza artificiale abbia tutte le funzionalità che mi aspetterei da un sistema di questo tipo",
        "Se utilizzassi questo strumento di intelligenza artificiale, penso che potrei fare affidamento su di esso completamente",
        "Posso sempre contare su questo strumento di intelligenza artificiale",
        "Posso fidarmi delle informazioni che mi vengono fornite da questo strumento di intelligenza artificiale"
    ]
    for i, q in enumerate(domande_post_s5):
        st.write(q)
        r = st.radio(f"post_s5_{i}", [1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
        risposte_post.append(r)
        if r is None: tutte_post_compilate = False
    st.markdown("---")

    if st.button("Invia risposte e concludi"):
        if not tutte_post_compilate:
            st.error("Per favore, rispondi a tutte le domande del questionario finale prima di inviare.")
        else:
            try:
                gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
                wks = gc.open("Risultati_Tesi").sheet1
                
                nuova_riga = [
                    st.session_state.dati_utente.get("Eta"),
                    st.session_state.dati_utente.get("Genere"),
                    st.session_state.dati_utente.get("Titolo_Studio"),
                    st.session_state.dati_utente.get("Occupazione"),
                    st.session_state.dati_utente.get("Stato_Civile"),
                    st.session_state.dati_utente.get("Frequenza_IA"),
                    st.session_state.condizione_scenario_macro,  
                    st.session_state.condizione_scenario_testo,  
                    st.session_state.condizione_ia
                ]
                
                nuova_riga.extend(st.session_state.pre_parte1 + st.session_state.pre_parte2 + st.session_state.dati_pre_test[len(st.session_state.pre_parte1)+len(st.session_state.pre_parte2):] if st.session_state.dati_pre_test else st.session_state.pre_parte1 + st.session_state.pre_parte2 + risposte_f3)
                nuova_riga.extend(risposte_post)
                nuova_riga.append(str(st.session_state.messaggi))
                
                wks.append_row(nuova_riga)
                
                st.session_state.fase = 6
                st.rerun()
                
            except Exception as e:
                st.error(f"Errore di connessione a Google Sheets: {e}")

# ==========================================
# FASE 6: RINGRAZIAMENTI
# ==========================================
elif st.session_state.fase == 6:
st.success("Grazie mille per la tua partecipazione!")
    st.write("I tuoi dati sono stati registrati con successo in forma anonima. Puoi chiudere questa pagina.")
