import os
import random
import json
import google.generativeai as genai
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- CONFIGURACIÓN DE APIS ---
# Estas variables se configuran en GitHub Secrets
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel('gemini-pro')

def elegir_tema_y_prompt():
    """Selecciona una categoría aleatoria para variar el contenido."""
    categorias = [
        {"tipo": "Animales", "prompt": "Dato curioso sobre un animal poco común para niños."},
        {"tipo": "Espacio", "prompt": "Dato asombroso sobre planetas o estrellas."},
        {"tipo": "Cuerpo Humano", "prompt": "Algo increíble que hace nuestro cuerpo cada día."},
        {"tipo": "Naturaleza", "prompt": "Dato curioso sobre plantas o el clima."},
        {"tipo": "Dinosaurios", "prompt": "Dato fascinante sobre un dinosaurio específico."}
    ]
    seleccion = random.choice(categorias)
    print(f"🎲 Categoría elegida: {seleccion['tipo']}")
    return seleccion['prompt']

def generar_contenido_ia():
    """Genera el guion del video usando Gemini."""
    print("🤖 Consultando a Gemini (Gratis)...")
    prompt_base = elegir_tema_y_prompt()
    instruccion = f"{prompt_base} Máximo 20 palabras, lenguaje muy sencillo, alegre y apto para niños pequeños."
    
    try:
        response = model.generate_content(instruccion)
        if response.candidates:
            return response.text
        else:
            return "¡Las abejas pueden reconocer rostros humanos!" # Respaldo por seguridad
    except Exception as e:
        print(f"⚠️ Error con Gemini: {e}")
        return "¡Los pulpos tienen tres corazones!" # Segundo respaldo

def crear_video(texto):
    """Crea el archivo MP4 usando MoviePy."""
    print(f"🎬 Creando video con el texto: {texto}")
    
    # Colores brillantes para captar la atención de los niños
    colores = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 200, 50), (200, 50, 255)]
    color_fondo = random.choice(colores)
    
    # Fondo de 1280x720 (HD)
    fondo = ColorClip(size=(1280, 720), color=color_fondo).set_duration(8)
    
    # Configuración del texto
    txt_clip = TextClip(
        texto, 
        fontsize=60, 
        color='white', 
        font='Arial-Bold', 
        method='caption', 
        size=(1100, None), 
        align='center'
    ).set_position('center').set_duration(8)
    
    video = CompositeVideoClip([fondo, txt_clip])
    video_output = "video_final.mp4"
    
    # Renderizado
    video.write_videofile(video_output, fps=24, codec="libx264")
    return video_output

def subir_a_youtube(ruta_archivo, titulo):
    """Sube el video generado al canal de YouTube."""
    print("🚀 Iniciando subida a YouTube...")
    
    # Cargamos el JSON del token de forma segura
    token_str = os.getenv("YOUTUBE_TOKEN")
    if not token_str:
        raise Exception("Falta la variable de entorno YOUTUBE_TOKEN")
    
    token_data = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(token_data)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": titulo,
            "description": "¡Aprende algo nuevo cada día con PequeBum Kids! 🌈✨\n#niños #educación #curiosidades",
            "tags": ["niños", "pequebum", "educación", "datos curiosos"],
            "categoryId": "27" # Categoría: Educación
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True # Declaración legal obligatoria
        }
    }

    media = MediaFileUpload(ruta_archivo, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    print(f"✅ Video publicado exitosamente: https://youtu.be/{response['id']}")

if __name__ == "__main__":
    try:
        guion = generar_contenido_ia()
        ruta_mp4 = crear_video(guion)
        subir_a_youtube(ruta_mp4, f"¿Sabías que...? 🧐 | PequeBum Kids")
        
        # Opcional: Limpiar archivo local después de subir
        if os.path.exists(ruta_mp4):
            os.remove(ruta_mp4)
            print("🧹 Archivo temporal eliminado.")
            
    except Exception as e:
        print(f"❌ Error crítico en el proceso: {e}")