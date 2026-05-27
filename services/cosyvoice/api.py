"""CosyVoice TTS API server stub.

In production, this is replaced by the full CosyVoice inference server.
See: https://github.com/FunAudioLLM/CosyVoice
"""

import argparse
import io
import wave

import numpy as np
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global model reference (loaded at startup)
cosyvoice_model = None


@app.route("/", methods=["POST"])
def synthesize():
    """
    Synthesize speech from text.

    Request JSON:
    {
        "text": "要合成的文本",
        "speaker": "clone" | "default",
        "speed": 1.0,
        "emotion": "neutral",
        "prompt_speech": "/path/to/reference.wav"  // for voice cloning
    }

    Returns: WAV audio file
    """
    data = request.get_json()
    text = data.get("text", "")
    speaker = data.get("speaker", "default")
    speed = data.get("speed", 1.0)
    emotion = data.get("emotion", "neutral")

    if not text:
        return jsonify({"error": "text is required"}), 400

    # Placeholder: generate a silent WAV file
    # In production, this calls cosyvoice_model.inference()
    sample_rate = 24000
    duration = len(text) * 0.3  # rough estimate
    num_samples = int(sample_rate * duration)
    silence = np.zeros(num_samples, dtype=np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(silence.tobytes())
    buf.seek(0)

    return send_file(buf, mimetype="audio/wav")


@app.route("/health")
def health():
    return {"status": "ok", "model_loaded": cosyvoice_model is not None}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9880)
    parser.add_argument("--model_dir", type=str, default="/app/models")
    args = parser.parse_args()

    print(f"CosyVoice API starting on port {args.port}")
    # In production: load CosyVoice model here
    # cosyvoice_model = CosyVoiceModel(args.model_dir)
    app.run(host="0.0.0.0", port=args.port, debug=False)
