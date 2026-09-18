from dataclasses import dataclass, asdict
from typing import Optional

@dataclass(frozen=True)
class SensorProfile:
    name: str
    spatial_resolution_m: Optional[float]
    spectral_characteristics: str
    normalization: str
    feature_strategy: str
    scale_strategy: str
    notes: str

PROFILES={
 "UNKNOWN":SensorProfile("UNKNOWN",None,"UNKNOWN","auto","structural + classical","image pyramid","No sensor assumptions are applied."),
 "OHRC":SensorProfile("OHRC",None,"optical panchromatic; verify product metadata","illumination + CLAHE ensemble","SIFT/ORB + terrain edges","image pyramid","Resolution and solar geometry are read from supplied metadata when available."),
 "TMC":SensorProfile("TMC",None,"optical terrain camera; verify product metadata","illumination + CLAHE ensemble","SIFT/ORB + terrain edges","image pyramid","Resolution and solar geometry are read from supplied metadata when available."),
 "IIRS":SensorProfile("IIRS",None,"hyperspectral; structural band selection","gradient/edge + sun prior","modality-invariant structures","image pyramid","Select a band explicitly for reproducible experiments."),
 "LRO_NAC":SensorProfile("LRO_NAC",None,"optical panchromatic","illumination + CLAHE ensemble","SIFT/ORB + terrain edges","image pyramid","Use mission product metadata or sidecar JSON for geometry."),
 "SELENE":SensorProfile("SELENE",None,"optical; verify product metadata","illumination + CLAHE ensemble","SIFT/ORB + terrain edges","image pyramid","Use product metadata or sidecar JSON for geometry."),
}
def profile_for(name): return PROFILES.get((name or "UNKNOWN").upper(),PROFILES["UNKNOWN"])
