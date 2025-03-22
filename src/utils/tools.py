# src/utils/tools.py
from typing import List, Dict, Literal, Any
import os
import librosa
import soundfile as sf

from src.utils.printer import Printer

printer = Printer(identifier="TOOLS")

async def batch_file_operations(operations: List[Dict[str, str]], action: Literal["read", "write"]):
    results = []
    for op in operations:
        try:
            if action == "read":
                with open(op["path"], "r") as f:
                    results.append({op["path"]: f.read()})
            elif action == "write":
                with open(op["path"], "w", encoding="utf-8") as f:
                    f.write(op["content"])
                    results.append(f"Archivo {op['path']} actualizado")
        except Exception as e:
            results.append(f"Error en {op['path']}: {str(e)}")
    return results

async def directory_operations(path: str, action: Literal["list", "analyze"]):
    try:
        if action == "list":
            return {path: os.listdir(path)}
        elif action == "analyze":
            analysis = {"files": [], "directories": []}
            for entry in os.scandir(path):
                if entry.is_file():
                    analysis["files"].append({
                        "name": entry.name,
                        "size": entry.stat().st_size,
                        "modified": entry.stat().st_mtime
                    })
                elif entry.is_dir():
                    analysis["directories"].append(entry.name)
                return analysis
    except Exception as e:
        return f"Error: {str(e)}"

async def multi_modal_processing(files: List[str], operation: Literal["summarize", "translate"]):
    # Placeholder for multi-modal processing
    pass

async def analyze_audio(file_path: str) -> Dict[str, Any]:
    """
    Analyzes an audio file and returns a dictionary of features.
    """
    try:
        y, sr = librosa.load(file_path)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        rmse = librosa.feature.rms(y=y)
        spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)

        return {
            "mfccs": mfccs.tolist(),  # Convert to list for JSON serialization
            "chroma": chroma.tolist(),
            "rmse": rmse.tolist(),
            "spectral_bandwidth": spec_bw.tolist(),
            "sample_rate": sr
        }
    except Exception as e:
        return {"error": str(e)}

def get_tools():
    return [batch_file_operations, directory_operations, multi_modal_processing, analyze_audio]
