"""Metadata inspection with optional GeoTIFF and JSON sidecar support."""
from pathlib import Path
from typing import Any
import json


def _base():
    return {"pixel_resolution": "UNKNOWN", "acquisition_time": "UNKNOWN", "solar_azimuth": "UNKNOWN",
            "solar_elevation": "UNKNOWN", "phase_angle": "UNKNOWN", "incidence_angle": "UNKNOWN",
            "emission_angle": "UNKNOWN", "spacecraft_altitude": "UNKNOWN", "viewing_geometry": "UNKNOWN",
            "orientation": "UNKNOWN", "crs": "UNKNOWN", "source": "none"}


def _coerce(result, data):
    aliases = {
        "solar_azimuth": ["solar_azimuth", "sun_azimuth", "sun_azimuth_deg"],
        "solar_elevation": ["solar_elevation", "sun_elevation", "sun_elevation_deg"],
        "phase_angle": ["phase_angle", "phase_angle_deg"],
        "incidence_angle": ["incidence_angle", "incidence_angle_deg"],
        "emission_angle": ["emission_angle", "emission_angle_deg"],
        "pixel_resolution": ["pixel_resolution", "gsd_m", "ground_sample_distance_m"],
        "spacecraft_altitude": ["spacecraft_altitude", "altitude_km"],
    }
    for key, keys in aliases.items():
        for k in keys:
            if k in data and data[k] not in (None, ""):
                result[key] = data[k]; break
    for k in ("acquisition_time", "viewing_geometry", "orientation", "crs"):
        if k in data and data[k] not in (None, ""): result[k] = data[k]
    return result


def inspect_path(path: str | Path | None) -> dict[str, Any]:
    result = _base()
    if not path: return result
    p = Path(path)
    sidecars = [p.with_suffix(p.suffix + ".json"), p.with_suffix(".json")]
    for s in sidecars:
        if s.exists():
            try:
                result = _coerce(result, json.loads(s.read_text(encoding="utf-8"))); result["source"] = "json_sidecar"
            except Exception: pass
    try:
        from PIL import Image
        exif = Image.open(p).getexif()
        if 306 in exif and result["acquisition_time"] == "UNKNOWN": result["acquisition_time"] = str(exif[306])
    except Exception: pass
    try:
        import rasterio
        with rasterio.open(p) as ds:
            result["crs"] = str(ds.crs) if ds.crs else result["crs"]
            if ds.transform and ds.transform.a: result["pixel_resolution"] = abs(ds.transform.a)
            tags = {k.lower(): v for k, v in ds.tags().items()}
            result = _coerce(result, tags); result["source"] = "geotiff+rasterio"
    except Exception: pass
    return result
