import os
import openai
import streamlit as st
import pdfplumber
from io import BytesIO

# Inicializa el modelo GPT-3
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Función para extraer texto de un archivo PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
        return "\n".join(pages)

# Función para dividir el texto en segmentos de menos de 4000 tokens
def split_text(text, max_tokens=4000):
    tokens = openai.api_key.split(text)
    if len(tokens) <= max_tokens:
        return [text]

    segments = []
    current_segment = []

    for token in tokens:
        if len(current_segment) + len(token) > max_tokens:
            segments.append("".join(current_segment))
            current_segment = []

        current_segment.append(token)

    if current_segment:
        segments.append("".join(current_segment))

    return segments

# Función para generar respuesta utilizando GPT-3
def generate_answer(prompt, model="text-davinci-003"):
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
st.title("Asistente de Preguntas sobre PDF con GPT-3.5-turbo")

uploaded_file = st.file_uploader("Sube un archivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Extrayendo texto del archivo PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    question = st.text_input("Escribe tu pregunta:")

    if question:
        text_segments = split_text(pdf_text)
        answers = []

        for i, segment in enumerate(text_segments):
            with st.spinner(f"Generando respuesta para el segmento {i + 1}..."):
                prompt = f"El siguiente texto fue extraído de un PDF:\n\n{segment}\n\nPregunta: {question}\nRespuesta:"
                answer = generate_answer(prompt)
                answers.append(answer)

        st.write("Respuesta:")
        st.write(" ".join(answers))
