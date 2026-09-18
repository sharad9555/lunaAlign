from dataclasses import dataclass
import importlib.util

@dataclass(frozen=True)
class EngineChoice:
    requested: str
    active: str
    reason: str
    device: str

def choose_engine(mode: str, sensor_source: str = "UNKNOWN", sensor_target: str = "UNKNOWN") -> EngineChoice:
    mode = (mode or "BALANCED").upper()
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
    except Exception: device = "cpu"
    deep_ready = importlib.util.find_spec("kornia") is not None
    cross_modal = "IIRS" in {sensor_source.upper(), sensor_target.upper()}
    if mode == "FAST": return EngineChoice(mode, "ORB", "fast CPU classical mode", device)
    if mode == "RESEARCH" and deep_ready: return EngineChoice(mode, "DEEP_OPTIONAL+SIFT", "local optional deep dependency available", device)
    if mode == "RESEARCH": return EngineChoice(mode, "SIFT", "optional deep model unavailable; safe classical fallback", device)
    return EngineChoice(mode, "SIFT", "structural classical baseline" + (" selected for cross-modality" if cross_modal else ""), device)
