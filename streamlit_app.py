import os
import openai
import streamlit as st
import pdfplumber
from io import BytesIO
import concurrent.futures


# Inicializa el modelo GPT-3
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Función para extraer texto de un archivo PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
        return "\n".join(pages)

# Función para dividir el texto en segmentos
def split_text(text, max_tokens=4096):
    if len(text) <= max_tokens:
        return [text]

    segments = []
    words = text.split()
    current_segment = []

    for word in words:
        if len(' '.join(current_segment) + ' ' + word) > max_tokens:
            segments.append(' '.join(current_segment))
            current_segment = []

        current_segment.append(word)

    if current_segment:
        segments.append(' '.join(current_segment))

    return segments

# Función para generar respuesta utilizando GPT-3.5-turbo
def generate_answer(prompt, model="gpt-3.5-turbo"):
    completions = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Eres un asistente de IA que responde preguntas basadas en el contenido de un PDF."},
            {"role": "user", "content": f"El texto del PDF es:\n\n{prompt}\n"},
            {"role": "user", "content": f"Pregunta: {question}"}
        ],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text.strip()
    return message

# Función auxiliar para generar respuestas en paralelo
def generate_answer_for_segment(segment, question):
    prompt = f"El siguiente texto fue extraído de un PDF:\n\n{segment}\n\nPregunta: {question}\nRespuesta:"
    return generate_answer(prompt)

# Interfaz de Streamlit
st.title("Asistente de Preguntas sobre PDF con GPT-3.5-turbo")

uploaded_file = st.file_uploader("Sube un archivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Extrayendo texto del archivo PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    question = st.text_input("Escribe tu pregunta:")

    if question:
        text_segments = split_text(pdf_text, max_tokens=2048)
        answers = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_segment = {executor.submit(generate_answer_for_segment, segment, question): segment for segment in text_segments}
            for future in concurrent.futures.as_completed(future_to_segment):
                answers.append(future.result())

        st.write("Respuesta:")
        st.write(" ".join(answers))
