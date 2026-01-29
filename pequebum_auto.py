import os
import random
import json
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, afx
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- CONFIGURACIÓN ---
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel('gemini-pro')

def elegir_asset_aleatorio(directorio):
    archivos = [f for f in os.listdir(directorio) if not f.startswith('.')]
    return os.path.join(directorio, random.choice(archivos))

def generar_guion_ia():
    print("🤖 Gemini generando contenido dinámico...")
    categorias = [
        "Dato sobre un animal marino",
        "Pregunta sobre un color (ej: ¿De qué color es la manzana?)",
        "Dato asombroso del espacio"
    ]
    tema = random.choice(categorias)
    instruccion = f"{tema}. Máximo 12 palabras, muy alegre para niños."
    
    try:
        response = model.generate_content(instruccion)
        return response.text if response.candidates else "¡Mira este divertido baile!"
    except:
        return "¡Aprender es muy divertido!"

def crear_video_pro(texto):
    print("🎬 Ensamblando video con assets reales...")
    
    # 1. Seleccionar Clip de fondo y Música
    ruta_clip = elegir_asset_aleatorio("assets/clips")
    ruta_musica = elegir_asset_aleatorio("assets/musica")
    
    clip_base = VideoFileClip(ruta_clip).resize(height=720) # Asegura formato HD
    duracion = clip_base.duration

    # 2. Crear Capa de Texto (Estilo PequeBum)
    txt_clip = TextClip(
        texto, 
        fontsize=70, 
        color='yellow', 
        font='Arial-Bold',
        stroke_color='black',
        stroke_width=2,
        method='caption', 
        size=(clip_base.w * 0.8, None)
    ).set_position('center').set_duration(duracion).set_start(0.5)

    # 3. Configurar Audio
    musica = AudioFileClip(ruta_musica).set_duration(duracion).volumex(0.2) # Volumen bajo
    
    # 4. Composición Final
    video_final = CompositeVideoClip([clip_base, txt_clip])
    video_final.audio = musica
    
    output = "video_pequebum_pro.mp4"
    video_final.write_videofile(output, fps=24, codec="libx264", audio_codec="aac")
    return output

def subir_a_youtube(ruta, titulo):
    print("🚀 Subiendo a YouTube...")
    token_data = json.loads(os.getenv("YOUTUBE_TOKEN"))
    creds = Credentials.from_authorized_user_info(token_data)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": titulo,
            "description": "Contenido educativo de alta calidad. #PequeBum #Kids",
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True
        }
    }

    media = MediaFileUpload(ruta, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    request.execute()
    print("✅ ¡Video Pro publicado!")

if __name__ == "__main__":
    try:
        texto = generar_guion_ia()
        video_ruta = crear_video_pro(texto)
        subir_a_youtube(video_ruta, "¡Diversión y Aprendizaje! 🌈 | PequeBum Kids")
    except Exception as e:
        print(f"❌ Error: {e}")
