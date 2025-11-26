import subprocess
import os

def merge_video_audio(video_path, audio_path, output_path):
    # Скачать FFmpeg: https://github.com/BtbN/FFmpeg-Builds/releases
    ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"

    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(f"FFmpeg не найден.")

    cmd = [
        ffmpeg_path,
        '-hide_banner',
        '-loglevel', 'quiet',  # Полностью отключает вывод
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        output_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Видео и аудио объединены в {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при обработке: {e}")


def main():
    # Получаем все mp4 файлы в текущей папке
    files = [f for f in os.listdir() if f.lower().endswith('.mp4')]

    if not files:
        print("В текущей папке нет MP4 файлов")
        return

    print("Найдены файлы:")
    for i, filename in enumerate(files, 1):
        print(f"{i}. {filename}")

    try:
        video_num = int(input("Введите номер видеофайла: ")) - 1
        if video_num < 0 or video_num >= len(files):
            raise ValueError
    except:
        print("❌ Некорректный номер")
        return

    try:
        audio_num = int(input("Введите номер аудиофайла: ")) - 1
        if audio_num < 0 or audio_num >= len(files):
            raise ValueError
    except:
        print("❌ Некорректный номер")
        return

    output_name = input("Введите имя для выходного файла (без .mp4): ") + ".mp4"
    merge_video_audio(files[video_num], files[audio_num], output_name)


if __name__ == "__main__":
    main()
