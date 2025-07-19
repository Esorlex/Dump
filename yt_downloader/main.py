import os
import sys
import yt_dlp

def download_video(url):
    download_path = os.path.join(os.getcwd(), "Downloads")
    os.makedirs(download_path, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'format': 'best[ext=mp4][vcodec^=avc1][acodec^=mp4a][protocol^=https]',
        'noplaylist': True,
        'quiet': False,
        'restrictfilenames': True,
        'nocheckcertificate': True,
        'merge_output_format': 'mp4',
        'postprocessors': [],  # ⛔ no ffmpeg needed
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            ydl.download([url])
            print("✅ Download complete.")
    except Exception as e:
        print(f"❌ Error during download: {e}")

if __name__ == "__main__":
    url = input("Enter the YouTube URL: ").strip()
    if not url:
        print("❌ No URL provided.")
        sys.exit(1)
    download_video(url)
