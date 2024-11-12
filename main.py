from flask import Flask, request, render_template, jsonify
import yt_dlp
import ffmpeg
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = './downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def show_download_form():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def handle_download_request():
    url = get_video_url()
    name = get_file_name()
    format = get_selected_format()
    
    if not url:
        return send_error("Nenhum Link foi inserido.", 400)
    
    temp_filename = os.path.join(DOWNLOAD_FOLDER, "temp_audio_or_video.mp4")

    try:
        download_video(url, temp_filename, format)
        return convert_and_save(temp_filename, name, format)
    except yt_dlp.utils.DownloadError as e:
        return send_error(f"Erro ao baixar o vídeo: {str(e)}", 500)
    except ffmpeg.Error as e:
        return send_error(f"Erro ao converter o arquivo: {str(e)}", 500)
    except Exception as e:
        return send_error(f"Erro inesperado: {str(e)}", 500)

def get_video_url():
    return request.form['url'].strip()

def get_file_name():
    return request.form['name'].strip()

def get_selected_format():
    return request.form['format']

def download_video(url, temp_filename, format):
    ydl_opts = {
        'format': 'bestaudio/best' if format in ["wav", "mp3"] else 'best',
        'outtmpl': temp_filename,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def convert_and_save(temp_filename, name, format):
    if format == "wav":
        return save_as_wav(temp_filename, name)
    elif format == "mp3":
        return save_as_mp3(temp_filename, name)
    elif format == "mp4":
        return save_as_mp4(temp_filename, name)
    else:
        return send_error("Formato inválido selecionado.", 400)

def save_as_wav(temp_filename, name):
    final_filename = os.path.join(DOWNLOAD_FOLDER, f"{name}.wav")
    ffmpeg.input(temp_filename).output(final_filename, format='wav', loglevel="error").run()
    os.remove(temp_filename)
    return send_success(f"Áudio baixado com sucesso em formato WAV: {final_filename}")

def save_as_mp3(temp_filename, name):
    final_filename = os.path.join(DOWNLOAD_FOLDER, f"{name}.mp3")
    ffmpeg.input(temp_filename).output(final_filename, format='mp3', loglevel="error").run()
    os.remove(temp_filename)
    return send_success(f"Áudio baixado com sucesso em formato MP3: {final_filename}")

def save_as_mp4(temp_filename, name):
    final_filename = os.path.join(DOWNLOAD_FOLDER, f"{name}.mp4")
    os.rename(temp_filename, final_filename)
    return send_success(f"Vídeo baixado com sucesso em formato MP4: {final_filename}")

def send_success(message):
    return jsonify({"success": message}), 200

def send_error(message, status_code):
    return jsonify({"error": message}), status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
