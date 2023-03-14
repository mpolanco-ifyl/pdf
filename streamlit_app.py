import os
import openai
import streamlit as st
import pdfplumber
from io import BytesIO
import os

# Inicializa el modelo GPT-3
openai.api_key = os.environ.get("OPENAI_API_KEY")


# Función para extraer texto de un archivo PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
        return "\n".join(pages)

# Función para generar respuesta utilizando GPT-3.5-turbo
def generate_answer(prompt, model="gpt-3.5-turbo"):
    completions = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text.strip()
    return message

# Interfaz de Streamlit
st.title("Lector de PDF y Asistente de Preguntas con GPT-3.5-turbo")

uploaded_file = st.file_uploader("Sube un archivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Extrayendo texto del archivo PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    st.write("Texto extraído:")
    st.write(pdf_text)

    question = st.text_input("Escribe tu pregunta:")

    if question:
        with st.spinner("Generando respuesta..."):
            prompt = f"El siguiente texto fue extraído de un PDF:\n\n{pdf_text}\n\nPregunta: {question}\nRespuesta:"
            answer = generate_answer(prompt)
            st.write("Respuesta:")
            st.write(answer)
