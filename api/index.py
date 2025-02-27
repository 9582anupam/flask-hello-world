from flask import Flask, request, jsonify
import os
import tempfile
import webvtt
import yt_dlp
import traceback
# from transformers import pipeline

app = Flask(__name__)

# Load the DistilBERT model for question-answering
# qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'


def format_timestamp(timestamp):
    """Convert WebVTT timestamp to hh:mm:ss or mm:ss format."""
    try:
        parts = timestamp.split('.')  # Remove milliseconds if present
        time_parts = parts[0].split(':')

        # Convert to integer for proper formatting
        time_parts = list(map(int, time_parts))

        if len(time_parts) == 3:  # hh:mm:ss format
            return f"{time_parts[0]:02}:{time_parts[1]:02}:{time_parts[2]:02}"
        elif len(time_parts) == 2:  # mm:ss format
            return f"{time_parts[0]:02}:{time_parts[1]:02}"
        return timestamp  # Fallback in case of unexpected format
    except Exception as e:
        print(f"Error in format_timestamp: {e}")
        return timestamp

def get_auto_generated_captions(video_url):
    """Fetch auto-generated captions from a YouTube video."""
    try:
        ydl_opts = {
            "writeautomaticsub": True,
            "skip_download": True,
            "outtmpl": "captions.%(ext)s",  # Temporary name for caption file
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            auto_subtitles = info.get("automatic_captions", {})

            print("Auto subtitles available:", auto_subtitles.keys())  # Debugging

            # Prioritize English if available, otherwise take the first available language
            lang = "en" if "en" in auto_subtitles else next(iter(auto_subtitles), None)

            if lang:
                caption_filename = f"captions.{lang}.vtt"
                print(f"Expected caption filename: {caption_filename}")

                # Use a temporary directory for file storage in deployment environment
                with tempfile.NamedTemporaryFile(delete=False, suffix='.vtt') as tmpfile:
                    tmpfile.close()
                    os.rename(caption_filename, tmpfile.name)  # Move the file to the temp location

                    if os.path.exists(tmpfile.name):
                        captions = []
                        for caption in webvtt.read(tmpfile.name):
                            captions.append({
                                "start": format_timestamp(caption.start),
                                "end": format_timestamp(caption.end),
                                "text": caption.text
                            })
                            print("Extracted caption:", caption.text)  # Debugging
                        return captions

        print("Caption file NOT found!")  # Debugging
        return []
    except Exception as e:
        print(f"Error fetching captions: {e}")
        traceback.print_exc()  # Print the full stack trace to help debug
        return []

@app.route("/api/getCaptions", methods=["GET"])
def get_captions():
    """API endpoint to get YouTube video captions."""
    try:
        url = request.args.get("url")
        if not url:
            return jsonify({"error": "No URL provided"}), 400

        captions = get_auto_generated_captions(url)
        if captions:
            return jsonify({"captions": captions}), 200
        else:
            return jsonify({"error": "Captions not found"}), 404
    except Exception as e:
        print(f"Error in get_captions API: {e}")
        traceback.print_exc()  # Print the full stack trace for debugging
        return jsonify({"error": "Internal server error"}), 500

# @app.route('/ask-question', methods=['POST'])
# def ask_question():
#     try:
#         data = request.get_json()
#         question = data.get('question')
#         context = data.get('context')

#         # Get the answer from the model
#         result = qa_pipeline(question=question, context=context)
#         answer = result['answer']

#         return jsonify({'answer': answer})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
