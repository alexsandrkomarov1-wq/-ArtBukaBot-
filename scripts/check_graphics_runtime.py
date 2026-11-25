#!/usr/bin/env python3
"""Static contract checks for the KOMAROVA_CORE adaptive graphics stack."""
from pathlib import Path

source = Path("assets/js/site-3d.js").read_text(encoding="utf-8")
required = {
    "secure-context WebGPU gate": "window.isSecureContext && navigator.gpu",
    "optional WebGPU renderer": "THREEGPU.WebGPURenderer",
    "asynchronous WebGPU initialization": "await renderer.init()",
    "WebGL2 renderer fallback": "new THREE.WebGLRenderer",
    "low-power 3D tier": 'graphicsMode = lowPower ? "lite-3d" : "webgl2"',
    "fresh canvas after failed GPU initialization": "const replacementCanvas = createCanvas()",
    "2D navigation fallback": "3D-графика недоступна · порталы и разделы остаются активны",
    "truthful WebGPU status": 'webgpu: "3D запущено · WebGPU"',
    "truthful WebGL2 status": 'webgl2: "3D запущено · WebGL2"',
    "truthful lite status": '"lite-3d": "Облегчённая 3D-сцена · WebGL2"',
}
missing = [label for label, token in required.items() if token not in source]
if missing:
    raise SystemExit("Graphics contract failed: " + ", ".join(missing))
print(f"Adaptive graphics contract passed ({len(required)} checks).")
