"""Read-only Android APK recon and conservative mobile-game fusion planning.

No installation, patching, extraction, code injection, signature bypass, or game asset redistribution.
Works on Linux/Windows/macOS using the Python standard library only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

MAX_ENTRIES = 150000
ABIS = ("arm64-v8a", "armeabi-v7a", "x86_64", "x86")
ENGINE_SIGNS = {
    "unity": ("libunity.so", "assets/bin/data/", "libil2cpp.so"),
    "unreal": ("libue4.so", "libunreal.so", "assets/main.obb.png"),
    "cocos2dx": ("libcocos2dcpp.so", "libcocos2djs.so"),
    "godot": ("libgodot_android.so", "libgodot.so", "assets/.godot/"),
}

def inspect_apk(filename: str) -> dict:
    path = Path(filename).expanduser()
    if not path.is_file():
        raise ValueError(f"APK_NOT_FOUND: {filename}")
    try:
        with ZipFile(path) as archive:
            files = archive.infolist()
            if len(files) > MAX_ENTRIES:
                raise ValueError("APK_TOO_MANY_ENTRIES")
            names = [entry.filename.replace("\\", "/").lower() for entry in files]
    except BadZipFile as exc:
        raise ValueError("INVALID_APK_ZIP") from exc
    if not any(name == "androidmanifest.xml" for name in names):
        raise ValueError("NOT_AN_APK_NO_MANIFEST")
    libnames = [name for name in names if name.startswith("lib/") and name.endswith(".so")]
    abis = sorted({name.split("/")[1] for name in libnames if len(name.split("/")) > 2 and name.split("/")[1] in ABIS})
    engines = [engine for engine, signs in ENGINE_SIGNS.items()
               if any(sign in name for name in names for sign in signs)]
    return {
        "apk_name": path.name,
        "format": "apk",
        "engine_candidates": engines or ["unknown"],
        "abis": abis,
        "has_dex": any(n.endswith(".dex") for n in names),
        "has_native_libs": bool(libnames),
        "files_scanned": len(names),
        "manifest_present": True,
        "inspection": "static ZIP entry names only; no reverse engineering or dynamic proof",
    }

def fusion_plan(paths: list[str]) -> dict:
    if len(paths) < 2:
        raise ValueError("AT_LEAST_TWO_APKS_REQUIRED")
    reports = [inspect_apk(path) for path in paths]
    abi_sets = [set(rep["abis"]) for rep in reports if rep["abis"]]
    common = sorted(set.intersection(*abi_sets)) if abi_sets else []
    return {
        "platform": "Android",
        "inputs": reports,
        "shared_native_abis": common,
        "recommended_first_route": "one-host-port-original-mechanics-and-assets",
        "alternative_routes": [
            "cooperating-open-source-native-cores-in-one-application-via-JNI",
            "two-cooperating-apps-with-explicit-consent-and-versioned-IPC",
        ],
        "contract_required": [
            "game-and-asset-ownership", "player-and-input-authority",
            "coordinate-system-units", "state-and-event-schema",
            "transport-and-backpressure", "start-pause-restart-crash",
            "rendering-and-surface-ownership", "save-isolation", "package-signing",
        ],
        "limitations": [
            "APK analysis does not establish permission to reuse assets or code",
            "two proprietary Android apps cannot be assumed embeddable or hookable",
            "Android sandbox, foreground lifecycle, process visibility, GPU surfaces and memory restrict dual-app rendering",
            "ABI overlap is not sufficient for cross-engine compatibility",
            "no anti-cheat, DRM, ownership or application-signature bypass",
            "real Android device/emulator testing required before claiming a working crossover",
        ],
        "acceptance_gates": [
            "static-and-license-audit", "host-prototype-build",
            "install-and-launch", "real-gameplay-oracle", "regression",
            "hardware-and-performance", "reproducible-release",
        ],
    }

def _inspect(args: argparse.Namespace) -> None:
    print(json.dumps(inspect_apk(args.apk), ensure_ascii=False, indent=2))

def _plan(args: argparse.Namespace) -> None:
    print(json.dumps(fusion_plan(args.apks), ensure_ascii=False, indent=2))

def register(sub) -> None:
    group = sub.add_parser("android", help="Static APK inspection and conservative Android game-fusion planning")
    actions = group.add_subparsers(dest="action")
    inspect = actions.add_parser("inspect", help="Read APK archive metadata without extraction or modification")
    inspect.add_argument("apk")
    inspect.add_argument("--json", action="store_true", help="Output JSON (default)")
    inspect.set_defaults(func=_inspect)
    plan = actions.add_parser("fusion-plan", help="Compare two or more local APKs and propose safe architecture")
    plan.add_argument("apks", nargs="+")
    plan.add_argument("--json", action="store_true", help="Output JSON (default)")
    plan.set_defaults(func=_plan)
