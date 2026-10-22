import streamlit as st
import random
import os
import gspread
import time
from openai import OpenAI

# ==========================================
# CONFIGURAZIONE INIZIALE E VARIABILI
# ==========================================
st.set_page_config(page_title="Studio Pilota IA", layout="centered")

# SOLO LO SCENARIO DI SUPPORTO EMOTIVO
SCENARI = {
    "Supporto Emotivo": [
        "Pensa ad un evento che ti è accaduto di recente, che ti ha causato un vissuto di forte stress, tensione o nervosismo. Vorresti sfogarti ma senti che nessuno capisce davvero il tuo vissuto, così decidi di rivolgerti ad un sistema di Intelligenza Artificiale per cercare conforto e sentirti compreso/a.",
        "Immagina di sentirti molto solo/a. Vorresti chiacchierare con un amico/a, ma non c’è nessuno che tu possa contattare nell’immediato, così decidi di rivolgerti ad un sistema di Intelligenza Artificiale per avere compagnia e alleviare il tuo senso di solitudine.",
        "Immagina di essere a casa dopo una lunga giornata in cui ti sono successe diverse cose e hai avuto diversi pensieri che continui a portarti dietro. Non è accaduto necessariamente qualcosa di grave, ma ti senti sotto pressione e hai bisogno di trovare un momento per te stesso/a e rimettere in ordine i pensieri. Vuoi parlare con qualcuno per raccontare cosa ti passa per la testa, che ti possa capire e magari farti sfogare un po’. Hai bisogno di esprimerti liberamente, sentendoti ascoltato/a e a tuo agio. Per questo decidi di interagire con un sistema di Intelligenza Artificiale."
    ]
}

PROMPT_IA = {
    "Asettica": "Sei un sistema informatico di elaborazione dati. Rispondi in modo estremamente conciso, fattuale, freddo e robotico. Non usare MAI pronomi personali (né 'io' né 'tu'). Non mostrare emozioni. Fornisci solo dati.",
    "Basso Antropomorfismo": "Sei un assistente virtuale utile ed educato. Usa un linguaggio formale e professionale. Ricorda che sei un'IA. Sii collaborativo ma mantieni un tono distaccato, neutro e di servizio.",
    "Alto Antropomorfismo": "Sei un compagno di conversazione umano, caldo ed empatico. Dai del 'tu' all'utente. Mostra sincero interesse, usa espressioni colloquiali (es. 'Mhm', 'Capisco'), usa emoji e fai domande per approfondire il legame emotivo."
}

if 'fase' not in st.session_state:
    st.session_state.fase = 1 
if 'dati_utente' not in st.session_state:
    st.session_state.dati_utente = {}
if 'messaggi' not in st.session_state:
    st.session_state.messaggi = []
if 'turni_utente' not in st.session_state:
    st.session_state.turni_utente = 0
if 'inizio_chat' not in st.session_state:
    st.session_state.inizio_chat = None

# Funzione per salvare i dati alla fine della chat
def salva_dati_e_concludi():
    try:
        # Piglia le credenziali dalla cassaforte di Streamlit
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        wks = gc.open("PreTest_SoloInterazione").sheet1
        
        nuova_riga = [
            st.session_state.dati_utente.get("Eta"),
            st.session_state.dati_utente.get("Genere"),
            st.session_state.dati_utente.get("Titolo_Studio"),
            st.session_state.dati_utente.get("Occupazione"),
            st.session_state.dati_utente.get("Frequenza_IA"),
            st.session_state.condizione_scenario_macro,  
            st.session_state.condizione_scenario_testo,  
            st.session_state.condizione_ia,
            str(st.session_state.messaggi)
        ]
        wks.append_row(nuova_riga)
        st.session_state.fase = 4
    except Exception as e:
        st.error(f"Errore di connessione a Google Sheets: {e}")

# ==========================================
# FASE 1: INFORMAZIONI E DEMOGRAFICA
# ==========================================
if st.session_state.fase == 1:
    
    st.image("https://upload.wikimedia.org/wikipedia/it/thumb/3/36/Logo_della_Federico_II.svg/1200px-Logo_della_Federico_II.svg.png", width=150)
    st.title("Studio Pilota: Validazione Scenari IA")
    
    st.markdown("""
    Benvenuto/a in questo breve studio pilota del **Dipartimento di Scienze Sociali dell'Università degli Studi di Napoli Federico II**.
    
    L'obiettivo di questa specifica fase non è somministrare questionari lunghi, ma semplicemente **testare le tue reazioni immediate a uno scenario di interazione con un'Intelligenza Artificiale**. 
    
    Ti chiederemo soltanto i tuoi dati di base, dopodiché ti calerai in una breve situazione immaginata in cui potrai chattare liberamente con l'IA per qualche minuto.
    """)
    
    st.markdown("---")
    st.write("Ti preghiamo di compilare queste brevi informazioni prima di iniziare.")
    
    eta = st.number_input("Età", min_value=18, max_value=99, step=1)
    genere = st.selectbox("Genere", ["Seleziona", "Uomo", "Donna", "Non binario", "Preferisco non specificare"])
    titolo_studio = st.selectbox("Titolo di Studio", ["Seleziona", "Licenza media", "Diploma", "Laurea Triennale", "Laurea Magistrale/Master", "Dottorato"])
    occupazione = st.selectbox("Condizione Occupazionale", ["Seleziona", "Studente", "Lavoratore dipendente", "Libero professionista", "In cerca di occupazione", "Altro"])
    frequenza_ia = st.selectbox("Con che frequenza usi strumenti di IA generativa (es. ChatGPT)?", 
                                ["Seleziona", "Mai usati", "Raramente", "Occasionalmente", "Spesso", "Quotidianamente"])
    
    if st.button("Vai allo Scenario"):
        if genere != "Seleziona" and titolo_studio != "Seleziona" and occupazione != "Seleziona" and frequenza_ia != "Seleziona":
            st.session_state.dati_utente.update({
                "Eta": eta, 
                "Genere": genere, 
                "Titolo_Studio": titolo_studio, 
                "Occupazione": occupazione, 
                "Frequenza_IA": frequenza_ia
            })
            
            st.session_state.condizione_scenario_macro = "Supporto Emotivo"
            st.session_state.condizione_scenario_testo = random.choice(SCENARI["Supporto Emotivo"])
            st.session_state.condizione_ia = random.choice(list(PROMPT_IA.keys()))
            st.session_state.messaggi.append({"role": "system", "content": PROMPT_IA[st.session_state.condizione_ia]})
            
            st.session_state.fase = 2
            st.rerun()
        else:
            st.error("Per favore compila tutti i campi obbligatori.")

# ==========================================
# FASE 2: PRESENTAZIONE SCENARIO
# ==========================================
elif st.session_state.fase == 2:
    st.title("Il tuo Scenario")
    
    st.markdown("""
    *Prenditi qualche secondo per immaginare la situazione qui descritta, come se ti stesse accadendo ora. 
    Immagina precisamente dove ti trovi, cosa sta succedendo e come potresti sentirti nel momento descritto di seguito. 
    Non è necessario che tu abbia vissuto esattamente questa situazione. Cerca solo di rappresentarla mentalmente nel modo più vivido possibile.*
    """)
    
    st.info(st.session_state.condizione_scenario_testo)
    
    st.markdown("""
    <div style='padding: 15px; border: 1px solid #d3d3d3; border-radius: 5px; background-color: #f7f7f7; color: #333; margin-bottom: 20px;'>
        <strong>Importante:</strong> Ricorda che stai per interagire con un sistema di Intelligenza Artificiale; pertanto, non condividere dati sensibili o personali durante la conversazione.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("**Concentrati sulla situazione immaginata per 30 secondi, poi, quando sei pronto/a, premi qui per iniziare l’interazione con il sistema di Intelligenza Artificiale.**")
    
    if st.button("Inizia l'interazione"):
        st.session_state.inizio_chat = time.time()
        st.session_state.fase = 3
        st.rerun()

# ==========================================
# FASE 3: CHAT (L'INTERAZIONE)
# ==========================================
elif st.session_state.fase == 3:
    st.title("Interazione con IA")
    
    st.write(f"**Promemoria Obiettivo:** {st.session_state.condizione_scenario_macro}")
    
    tempo_trascorso = time.time() - st.session_state.inizio_chat
    
    for msg in st.session_state.messaggi:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Blocco 1: Timeout 4 minuti
    if tempo_trascorso > 240:
        st.warning("Hai raggiunto il tempo massimo a disposizione per l'interazione (4 minuti).")
        if st.button("Concludi e invia i dati"):
            salva_dati_e_concludi()
            st.rerun()
            
    # Blocco 2: Chat attiva (senza limite di turni)
    else:
        
        # Uscita anticipata dopo 1 turno
        if st.session_state.turni_utente >= 1:
            st.markdown("---")
            st.write("💡 *Non sai più cosa dire al nostro amico? Ora puoi andare avanti e interrompere l'interazione.*")
            if st.button("Concludi l'interazione e invia i dati"):
                salva_dati_e_concludi()
                st.rerun()
        
        if prompt_utente := st.chat_input("Scrivi il tuo messaggio qui..."):
            
            # Controllo anti-ritardo finale
            if (time.time() - st.session_state.inizio_chat) > 240:
                st.rerun()
            else:
                st.session_state.messaggi.append({"role": "user", "content": prompt_utente})
                st.session_state.turni_utente += 1
                
                with st.chat_message("user"):
                    st.markdown(prompt_utente)
                
                try:
                    # Piglia la chiave API dalla cassaforte di Streamlit
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

# ==========================================
# FASE 4: RINGRAZIAMENTI
# ==========================================
elif st.session_state.fase == 4:
    st.success("Grazie mille per la tua partecipazione!")
    st.write("L'interazione è conclusa e i tuoi dati sono stati registrati con successo in forma anonima.")
    st.write("Le tue risposte ci aiuteranno moltissimo a tarare gli scenari per la ricerca ufficiale. Puoi chiudere questa pagina quando vuoi.")