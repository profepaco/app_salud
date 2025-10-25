import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import re
st.set_page_config(page_title="Mi Asistente de la Salud", page_icon="🩺")

st.title("👨🏼‍⚕️ Mi Asistente de la Salud")
st.write("Bienvenido a tu asistente personal de salud. Aquí puedes hacer preguntas relacionadas con tu bienestar y recibir respuestas informativas.")

st.markdown("""
    ### ¿Cómo funciona?
    Simplemente escribe tu pregunta relacionada con la salud en el cuadro de texto a continuación y presiona 'Enviar'. 
    Nuestro asistente utilizará la inteligencia artificial para proporcionarte una respuesta precisa y útil.
    """)

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Por favor, configura tu clave API de Google Generative AI en los secretos de Streamlit.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns([1, 2])
with col1:
    st.image("./img/imagen.png", width=150)

with col2:
    user_input = st.text_input("¿Cómo te sientes hoy o qué te gustaría mejorar?", key="user_input")
    
    if st.button("Enviar"):
        if user_input.strip() == "":
            st.warning("Por favor, ingresa una pregunta o comentario.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            try:
                prompt = f"""Eres un asistente amable y empático de bienestar. Ofrece consejos simples y prácticos sobre sueño, estrés, hidratación, ejercicio y nutrición. Nunca diagnóstiques ni recetes medicamentos. Mantén la respuesta en un tono empático y conciso."""
                full_prompt = prompt + "\n\nConversación:\n"

                conversation = "\n\nConversación:\n"
                for m in st.session_state.messages:
                    role = "Usuario" if m["role"] == "user" else "Asistente"
                    text = m.get("content") or m.get("text", "")
                    conversation += f"{role}: {text}\n"

                full_prompt = prompt + "\n" + conversation + "Asistente:"

                resp = model.generate_content(full_prompt)
               
                if hasattr(resp, "text") and resp.text:
                    response = resp.text.strip()
                else:
                    response = resp.candidates[0].content.parts[0].text.strip()

          
                st.session_state.messages.append({"role": "assistant", "text": response})
                st.success("Respuesta recibida.")

            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "text": f"Error al llamar a Gemini: {e}"})
                st.error(f"Error al llamar a Gemini: {e}")
    if st.button("Limpiar Conversación"):
        st.session_state.messages = []
        st.success("Conversación limpiada.")

st.divider()
st.subheader("💬 Conversación")

chat_css = """
<style>
.chat-message {
    border-radius: 12px;
    padding: 10px 14px;
    margin: 8px 0;
    max-width: 80%;
    line-height: 1.5;
    word-wrap: break-word;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    transition: background-color 0.3s, color 0.3s;
    font-size: 1.1rem;
}
.user {
    background-color: #DCF8C6;
    color: #000000;
    align-self: flex-start;
    margin-right: auto;
    text-align: left;
}
.assistant {
    background-color: #F1F0F0;
    color: #000000;
    align-self: flex-end;
    margin-left: auto;
    text-align: left;
}
.chat-container {
    display: flex;
    flex-direction: column;
}

@media (prefers-color-scheme: dark) {
    .user {
        background-color: #075E54; 
        color: #E0E0E0;
    }
    .assistant {
        background-color: #2A2A2A; 
        color: #EAEAEA;
    }
    body {
        background-color: #121212;
        color: #FFFFFF;
    }
}
</style>
"""

st.markdown(chat_css, unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-message user"><b>👨🏽‍💻Tú:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant"><b>👨🏼‍⚕️Asistente:</b><br>{msg["text"]}', unsafe_allow_html=True)
        
        clean_text = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ0-9,;.?!¡¿\s]", "", msg["text"])
        tts = gTTS(text=clean_text, lang='es')
    
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()
        st.audio(audio_bytes, format="audio/mp3")

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.caption("Ejemplo de Chatbot de Salud utilizando Google Gemini 2.5 Flash y Streamlit.")
st.caption("Desarrollado por Francisco Javier Reyes Santamand.")