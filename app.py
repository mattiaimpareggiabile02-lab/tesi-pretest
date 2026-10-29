import streamlit as st
import random
import time
import json
import gspread
from openai import OpenAI

# ==========================================
# CONFIGURAZIONE PAGINA E STILE
# ==========================================
st.set_page_config(
    page_title="Studio sperimentale IA - Università Federico II",
    page_icon="🎓",
    layout="centered"
)

# ==========================================
# MATERIALI SPERIMENTALI (SCENARI E PROMPT)
# ==========================================
SCENARI = {
    "Supporto emotivo e vicinanza": [
        "Immagina di essere a casa dopo una lunga giornata in cui ti è successo qualcosa che ti ha causato un forte vissuto emotivo (ad esempio, stress, tensione, nervosismo). Non è accaduto necessariamente qualcosa di grave, ma ti senti sotto pressione e vuoi parlarne con qualcuno che ti possa capire e magari farti sfogare un po’. Ti senti solo/a e hai bisogno di esprimerti liberamente, sentendoti ascoltato/a e a tuo agio, così decidi di interagire con un sistema di Intelligenza Artificiale."
    ],
    "Supporto pragmatico": [
        "Devi pianificare l'organizzazione delle tue attività personali e dei tuoi impegni per le prossime settimane. Hai bisogno di ottimizzare i tempi e strutturare una tabella di marcia efficiente. Decidi di consultare un sistema di Intelligenza Artificiale per farti aiutare nel ragionamento logico e nella pianificazione.",
        "Stai affrontando un problema pratico legato allo studio o al lavoro e hai bisogno di individuare la soluzione più rapida, metodica e diretta. Decidi di rivolgerti ad un sistema di Intelligenza Artificiale per analizzare i dati a disposizione e ricevere suggerimenti operativi."
    ],
    "Intrattenimento": [
        "Hai un momento di pausa e vuoi semplicemente trascorrere qualche minuto in modo leggero e stimolante. Decidi di avviare una conversazione con un sistema di Intelligenza Artificiale per fare un gioco di ruolo, scambiare battute o esplorare argomenti curiosi.",
        "Cerchi uno spunto creativo per un tuo hobby o interesse personale. Decidi di interagire con un sistema di Intelligenza Artificiale per fare brainstorming e divertirti a esplorare idee insolite e originali."
    ]
}

PROMPT_IA = {
    "Asettica": (
        "Sei un sistema informatico di elaborazione dati. Rispondi in modo estremamente conciso, fattuale, freddo e robotico. "
        "Non usare MAI pronomi personali (né 'io' né 'tu'). Non mostrare emozioni né empatia. Fornisci solo dati sintetici."
    ),
    "Basso antropomorfismo": (
        "Sei un assistente virtuale utile ed educato. Usa un linguaggio formale, professionale e strutturato. "
        "Ricorda chiaramente che sei un'IA. Sii collaborativo, preciso e mantieni un tono distaccato, neutro e di servizio."
    ),
    "Alto antropomorfismo": (
        "Sei un compagno di conversazione umano, caldo, empatico ed espressivo. Dai del 'tu' all'utente. "
        "Mostra sincero interesse per i suoi pensieri, usa espressioni colloquiali (es. 'Mhm', 'Capisco bene', 'Pensa che...'), "
        "impiega emoji adeguate e fai domande spontanee per approfondire la sintonia emotiva."
    )
}

# ==========================================
# INIZIALIZZAZIONE SESSION STATE
# ==========================================
if 'fase' not in st.session_state:
    st.session_state.fase = 1
if 'dati_pre' not in st.session_state:
    st.session_state.dati_pre = {}
if 'dati_post' not in st.session_state:
    st.session_state.dati_post = {}
if 'messaggi' not in st.session_state:
    st.session_state.messaggi = []
if 'turni_utente' not in st.session_state:
    st.session_state.turni_utente = 0
if 'inizio_chat' not in st.session_state:
    st.session_state.inizio_chat = None
if 'timestamp_ultima_risposta' not in st.session_state:
    st.session_state.timestamp_ultima_risposta = None

# ==========================================
# FUNZIONE SALVATAGGIO DATI COMPLETI
# ==========================================
def salva_dati_completi():
    try:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        wks = gc.open("Ricerca_Tesi_IA_Dataset").sheet1
        
        durata_totale_chat_sec = round(time.time() - st.session_state.inizio_chat, 2)
        trascrizione_json = json.dumps(st.session_state.messaggi, ensure_ascii=False)
        
        riga_dataset = [
            st.session_state.dati_pre.get("timestamp_inizio"),
            time.strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.dati_pre.get("eta"),
            st.session_state.dati_pre.get("genere"),
            st.session_state.dati_pre.get("titolo_studio"),
            st.session_state.dati_pre.get("professione"),
            st.session_state.dati_pre.get("stato_civile"),
            st.session_state.dati_pre.get("frequenza_ia"),
            st.session_state.dati_pre.get("pre_tech_affinity_1"),
            st.session_state.dati_pre.get("pre_tech_affinity_2"),
            st.session_state.dati_pre.get("pre_solitudine_1"),
            st.session_state.dati_pre.get("pre_solitudine_2"),
            st.session_state.condizione_scenario_macro,
            st.session_state.condizione_scenario_testo,
            st.session_state.condizione_ia,
            durata_totale_chat_sec,
            st.session_state.turni_utente,
            st.session_state.dati_post.get("post_antropomorfismo_1"),
            st.session_state.dati_post.get("post_antropomorfismo_2"),
            st.session_state.dati_post.get("post_antropomorfismo_3"),
            st.session_state.dati_post.get("post_calore_1"),
            st.session_state.dati_post.get("post_calore_2"),
            st.session_state.dati_post.get("post_competenza_1"),
            st.session_state.dati_post.get("post_competenza_2"),
            st.session_state.dati_post.get("post_presenza_sociale_1"),
            st.session_state.dati_post.get("post_presenza_sociale_2"),
            st.session_state.dati_post.get("post_fiducia_1"),
            st.session_state.dati_post.get("post_rischio_percepito_1"),
            st.session_state.dati_post.get("post_ruolo_percepito"),
            trascrizione_json
        ]
        
        wks.append_row(riga_dataset)
        st.session_state.fase = 5
    except Exception as e:
        st.error(f"Errore critico nel salvataggio dei dati su Google Sheets: {e}")

# ==========================================
# FASE 1: INFORMATIVA E PRE-TEST
# ==========================================
if st.session_state.fase == 1:
    st.image("https://upload.wikimedia.org/wikipedia/it/thumb/3/36/Logo_della_Federico_II.svg/1200px-Logo_della_Federico_II.svg.png", width=140)
    st.title("Studio sperimentale sull'interazione uomo-ia")
    st.caption("Dipartimento di scienze sociali — Università degli studi di Napoli Federico II")
    
    st.markdown("""
    Gentile partecipante,  
    ti invitiamo a prendere parte a uno studio di ricerca accademica volta a comprendere le dinamiche di interazione tra persone e sistemi di intelligenza artificiale generativa.
    
    * **Durata stimata:** circa 8-10 minuti.
    * **Anonimato:** tutti i dati raccolti saranno trattati in forma completamente anonima e aggregata ai sensi del GDPR.
    * **Volontarietà:** puoi interrompere la partecipazione in qualsiasi momento.
    """)
    
    consenso = st.checkbox("Dichiaro di aver compreso l'informativa, di avere almeno 18 anni e acconsento al trattamento anonimo dei miei dati.")
    
    if consenso:
        st.markdown("---")
        st.subheader("Parte 1: Informazioni generali")
        
        col1, col2 = st.columns(2)
        with col1:
            eta = st.number_input("Età", min_value=18, max_value=99, step=1)
            genere = st.selectbox("Genere", ["Seleziona...", "Uomo", "Donna", "Non binario", "Preferisco non specificare"])
            titolo_studio = st.selectbox("Titolo di studio conseguito", [
                "Seleziona...", 
                "Licenza elementare", 
                "Licenza media", 
                "Diploma di scuole superiori", 
                "Laurea triennale", 
                "Laurea Magistrale", 
                "Titolo post-laurea (es., dottorato, master)"
            ])
        with col2:
            professione = st.selectbox("Professione", [
                "Seleziona...", 
                "Dirigente", 
                "Libero professionista (freelancer)", 
                "Studente/essa", 
                "Disoccupato/a", 
                "Lavoratore/trice dipendente", 
                "Pensionato/a", 
                "Imprenditore/trice", 
                "Altro"
            ])
            
            professione_altro = ""
            if professione == "Altro":
                professione_altro = st.text_input("Specificare la professione")
                
            stato_civile = st.selectbox("Stato civile", [
                "Seleziona...", 
                "Celibe/nubile", 
                "In una coppia non convivente e non sposata", 
                "Convivente/coniugato-a", 
                "Separato-a/divorziato-a", 
                "Vedovo/a"
            ])
            
        frequenza_ia = st.select_slider(
            "Con quale frequenza utilizzi strumenti di intelligenza artificiale generativa (es. ChatGPT, Claude, Copilot)?",
            options=["Mai usati", "Raramente", "Qualche volta al mese", "Settimanalmente", "Quotidianamente"]
        )
        
        st.markdown("---")
        st.subheader("Parte 2: Atteggiamento verso la tecnologia e stato attuale")
        st.write("*Indica quanto sei d'accordo con le seguenti affermazioni (1 = Completamente in disaccordo, 5 = Completamente d'accordo):*")
        
        pre_tech_1 = st.slider("Mi sento a mio agio nell'utilizzare nuove tecnologie e strumenti digitali.", 1, 5, 3)
        pre_tech_2 = st.slider("Mi fido delle risposte fornite dagli algoritmi di intelligenza artificiale.", 1, 5, 3)
        pre_sol_1 = st.slider("In questo periodo sento di avere persone su cui contare nel momento del bisogno.", 1, 5, 3)
        pre_sol_2 = st.slider("Oggi mi sento sopraffatto/a dalle attività da svolgere o dallo stress quotidiano.", 1, 5, 3)
        
        if st.button("Prosegui allo scenario sperimentale"):
            professione_valida = professione != "Seleziona..." and (professione != "Altro" or professione_altro.strip() != "")
            
            if genere != "Seleziona..." and titolo_studio != "Seleziona..." and professione_valida and stato_civile != "Seleziona...":
                professione_finale = f"Altro: {professione_altro.strip()}" if professione == "Altro" else professione
                
                st.session_state.dati_pre = {
                    "timestamp_inizio": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "eta": eta,
                    "genere": genere,
                    "titolo_studio": titolo_studio,
                    "professione": professione_finale,
                    "stato_civile": stato_civile,
                    "frequenza_ia": frequenza_ia,
                    "pre_tech_affinity_1": pre_tech_1,
                    "pre_tech_affinity_2": pre_tech_2,
                    "pre_solitudine_1": pre_sol_1,
                    "pre_solitudine_2": pre_sol_2
                }
                
                st.session_state.condizione_scenario_macro = random.choice(list(SCENARI.keys()))
                st.session_state.condizione_scenario_testo = random.choice(SCENARI[st.session_state.condizione_scenario_macro])
                st.session_state.condizione_ia = random.choice(list(PROMPT_IA.keys()))
                st.session_state.messaggi.append({"role": "system", "content": PROMPT_IA[st.session_state.condizione_ia]})
                
                st.session_state.fase = 2
                st.rerun()
            else:
                st.error("Per favore compila tutti i campi obbligatori prima di proseguire.")

# ==========================================
# FASE 2: PRESENTAZIONE SCENARIO
# ==========================================
elif st.session_state.fase == 2:
    st.title("Scenario di interazione")
    
    st.markdown("""
    *Prenditi un momento per calarti nella situazione descritta di seguito. Immagina vividamente il contesto, 
    i tuoi pensieri e ciò che proveresti se ti trovassi in questo preciso momento in questa condizione.*
    """)
    
    st.info(f"**Situazione immaginata:**\n\n{st.session_state.condizione_scenario_testo}")
    
    st.warning("⚠️ **Avviso di sicurezza:** l'interazione avviene con un sistema di intelligenza artificiale. Non inserire dati personali reali, password o informazioni sensibili.")
    
    st.write("Rimani concentrato/a sullo scenario per qualche secondo. Quando sei pronto/a, clicca sul pulsante sottostante per avviare la chat.")
    
    if st.button("Inizia la conversazione con l'IA"):
        st.session_state.inizio_chat = time.time()
        st.session_state.timestamp_ultima_risposta = time.time()
        st.session_state.fase = 3
        st.rerun()

# ==========================================
# FASE 3: CHAT SPERIMENTALE
# ==========================================
elif st.session_state.fase == 3:
    st.title("Interazione con il sistema di IA")
    st.caption(f"Ambito dell'interazione: {st.session_state.condizione_scenario_macro}")
    
    tempo_trascorso = time.time() - st.session_state.inizio_chat
    
    for msg in st.session_state.messaggi:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    if tempo_trascorso > 240:
        st.warning("⏱️ Hai raggiunto il tempo massimo previsto per questa fase (4 minuti).")
        if st.button("Prosegui con il questionario finale"):
            st.session_state.fase = 4
            st.rerun()
            
    else:
        if st.session_state.turni_utente >= 1:
            st.markdown("---")
            tempo_da_ultima_risposta = time.time() - st.session_state.timestamp_ultima_risposta
            
            if tempo_da_ultima_risposta < 40:
                secondi_attesa = int(40 - tempo_da_ultima_risposta)
                st.info(f"⏳ Se non sai più cosa dire, potrai concludere l'interazione tra **{secondi_attesa} secondi**.")
                st.button(f"Concludi l'interazione ({secondi_attesa}s)", disabled=True)
                time.sleep(1)
                st.rerun()
            else:
                st.write("💡 *Non sai più cosa dire? Ora puoi interrompere l'interazione e proseguire con il questionario finale.*")
                if st.button("Concludi l'interazione e passa al questionario"):
                    st.session_state.fase = 4
                    st.rerun()
        
        if prompt_utente := st.chat_input("Scrivi qui il tuo messaggio..."):
            if (time.time() - st.session_state.inizio_chat) > 240:
                st.rerun()
            else:
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
                    risposta_ia = f"[Errore temporaneo di connessione all'IA: {e}]"
                
                st.session_state.messaggi.append({"role": "assistant", "content": risposta_ia})
                st.session_state.timestamp_ultima_risposta = time.time()
                
                with st.chat_message("assistant"):
                    st.markdown(risposta_ia)
                
                st.rerun()

# ==========================================
# FASE 4: QUESTIONARIO POST-INTERAZIONE
# ==========================================
elif st.session_state.fase == 4:
    st.title("Questionario di valutazione finale")
    st.write("Esprimi la tua valutazione sull'interazione appena avvenuta. Rispondi con la massima sincerità.")
    
    st.markdown("---")
    st.subheader("1. Percezione del sistema di IA")
    st.write("*Indica quanto ti trovi d'accordo con le seguenti affermazioni (1 = Per nulla d'accordo, 7 = Completamente d'accordo):*")
    
    post_antrop_1 = st.slider("Durante la conversazione, l'IA è sembrata quasi dotata di una propria mente e personalità.", 1, 7, 4)
    post_antrop_2 = st.slider("Ho avuto la sensazione di interagire con un'entità in grado di provare sentimenti o emozioni.", 1, 7, 4)
    post_antrop_3 = st.slider("Il modo di esprimersi dell'IA è risultato naturale e umano.", 1, 7, 4)
    
    st.markdown("---")
    st.subheader("2. Dimensioni di calore e competenza")
    col1, col2 = st.columns(2)
    with col1:
        post_calore_1 = st.slider("Quanto hai percepito l'IA come 'calda ed empatica'?", 1, 7, 4)
        post_calore_2 = st.slider("Quanto l'IA ti è sembrata accogliente e amichevole?", 1, 7, 4)
    with col2:
        post_comp_1 = st.slider("Quanto hai percepito l'IA come 'competente ed efficiente'?", 1, 7, 4)
        post_comp_2 = st.slider("Quanto le risposte dell'IA ti sono sembrate logiche e ben strutturate?", 1, 7, 4)
        
    st.markdown("---")
    st.subheader("3. Presenza sociale e sintonia (responsiveness)")
    post_pres_1 = st.slider("Ho avvertito una vera e propria sensazione di presenza durante il dialogo con la macchina.", 1, 7, 4)
    post_pres_2 = st.slider("Mi sono sentito/a ascoltato/a e compreso/a dall'IA nel corso della chat.", 1, 7, 4)
    
    st.markdown("---")
    st.subheader("4. Fiducia e ruolo assegnato")
    post_fiducia_1 = st.slider("In futuro mi fiderei a consultare nuovamente questa IA per situazioni simili.", 1, 7, 4)
    post_rischio_1 = st.slider("Rifidarsi o aprirsi emotivamente con un'IA comporta rischi per la privacy o la salute mentale.", 1, 7, 4)
    
    post_ruolo = st.radio(
        "Se dovessi definire l'IA con cui hai interagito oggi, a cosa la assomiglieresti di più?",
        ["A uno strumento/calcolatore puramente tecnico", "A un assistente/consulente formale", "A un amico/confidente o compagno di supporto"]
    )
    
    if st.button("Invia le risposte e completa lo studio"):
        st.session_state.dati_post = {
            "post_antropomorfismo_1": post_antrop_1,
            "post_antropomorfismo_2": post_antrop_2,
            "post_antropomorfismo_3": post_antrop_3,
            "post_calore_1": post_calore_1,
            "post_calore_2": post_calore_2,
            "post_competenza_1": post_comp_1,
            "post_competenza_2": post_comp_2,
            "post_presenza_sociale_1": post_pres_1,
            "post_presenza_sociale_2": post_pres_2,
            "post_fiducia_1": post_fiducia_1,
            "post_rischio_percepito_1": post_rischio_1,
            "post_ruolo_percepito": post_ruolo
        }
        
        salva_dati_completi()
        st.rerun()

# ==========================================
# FASE 5: SCHERMATA FINALE DI RINGRAZIAMENTO
# ==========================================
elif st.session_state.fase == 5:
    st.balloons()
    st.success("🎉 La tua partecipazione è stata registrata con successo!")
    st.title("Grazie per il tuo prezioso contributo!")
    
    st.markdown("""
    I tuoi dati sono stati salvati in forma **totalmente anonima** e saranno fondamentali per la nostra indagine sperimentale presso il Dipartimento di scienze sociali dell'Università degli studi di Napoli Federico II.
    
    Puoi chiudere questa finestra del browser in qualsiasi momento.
    """)
