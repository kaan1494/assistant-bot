"""
Ses işleme ve FFmpeg kontrolü için yardımcı fonksiyonlar
"""
import os
from pydub import AudioSegment
from pydub.utils import which

def setup_ffmpeg():
    """FFmpeg yollarını ayarla ve kontrol et"""
    # Artık PATH'te olduğu için basit şekilde kontrol et
    try:
        from pydub.utils import which
        ffmpeg_path = which("ffmpeg")
        ffprobe_path = which("ffprobe")
        
        print("FFMPEG path:", ffmpeg_path)
        print("FFPROBE path:", ffprobe_path)
        
        return ffmpeg_path is not None and ffprobe_path is not None
    except Exception as e:
        print(f"FFmpeg kontrol hatası: {e}")
        return False

def convert_voice_to_wav(ogg_path, wav_path):
    """Ses dosyasını WAV formatına çevir"""
    # Dosya varlığını kontrol et
    if not os.path.exists(ogg_path):
        raise Exception(f"Ses dosyası bulunamadı: {ogg_path}")
    
    print(f"Ses dosyası boyutu: {os.path.getsize(ogg_path)} bytes")
    
    try:
        # Önce OGG olarak dene
        print("OGG formatı deneniyor...")
        seg = AudioSegment.from_file(str(ogg_path), format="ogg")
        print("OGG formatı başarılı!")
    except Exception as e1:
        print(f"OGG formatı başarısız: {e1}")
        try:
            # Sonra WEBM olarak dene
            print("WEBM formatı deneniyor...")
            seg = AudioSegment.from_file(str(ogg_path), format="webm")
            print("WEBM formatı başarılı!")
        except Exception as e2:
            print(f"WEBM formatı başarısız: {e2}")
            try:
                # Son çare: format belirtmeden
                print("Format belirtmeden deneniyor...")
                seg = AudioSegment.from_file(str(ogg_path))
                print("Format belirtmeden başarılı!")
            except Exception as e3:
                print(f"Tüm formatlar başarısız: {e3}")
                raise Exception(f"Ses dosyası okunamadı. OGG: {e1}, WEBM: {e2}, Auto: {e3}")
    
    # 16kHz mono WAV'e çevir
    print("WAV formatına çevriliyor...")
    seg = seg.set_frame_rate(16000).set_channels(1)
    seg.export(str(wav_path), format="wav")
    print(f"WAV dosyası oluşturuldu: {wav_path}")
    return True
