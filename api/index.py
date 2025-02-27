from flask import Flask, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# testing api
@app.route('/', methods=['GET'])
def test_api():
    return jsonify({
        "message": "API is running /"
    })

@app.route('/api/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify({
            "success": True,
            "transcript": transcript
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
