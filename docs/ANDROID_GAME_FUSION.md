# Android Game Fusion — Universal Modder + Agent OS

Status: experimental, **static APK recon and architectural planning only**. Nothing here merges third-party APKs or proves runtime compatibility.

## Quick start (Linux / Ubuntu, Python >=3.10)

```sh
./bin/um android inspect ~/owned-games/host.apk --json
./bin/um android inspect ~/owned-games/guest.apk --json
./bin/um android fusion-plan ~/owned-games/host.apk ~/owned-games/guest.apk --json
uv run --with pytest pytest -q tests/test_android.py
```

Do not store, commit or upload proprietary APKs, extracted assets, decrypted code or user saves. Inspect locally from authorized copies only. The inspector reads ZIP **entry names**; it does not extract or execute any APK contents and does not parse binary AndroidManifest.xml or detect app identity/permissions.

## Code and skills inventory

- `um/android.py` — read-only APK entry census, engine hints, ABI intersection, conservative fusion plan.
- `um/cli.py` — `um android` registration.
- `tests/test_android.py` — synthetic fixtures.
- `skills/game-recon/SKILL.md` — recon principles (PC-oriented; supplement with Android APK and NDK facts).
- `skills/mashup-mods/SKILL.md` — route selection and bridge ownership.
- `skills/mod-any-game/SKILL.md` — vertical-slice cycle.
- `knowledge/techniques/choosing-a-mashup-route.md` — seven fusion patterns, mostly demonstrated on desktop.
- `knowledge/techniques/bridge-contracts-ownership-units-and-lifecycle.md` — transferable ownership and protocol contracts.
- `knowledge/techniques/oracles-how-agents-know-a-mod-works.md` — gameplay evidence.

## Mobile fusion decision matrix

| Route | What runs on Android | Fidelity / feasibility | First slice |
| --- | --- | --- | --- |
| A. Host + original mechanic reimplementation | **One mobile app** using source-available host / SDK; guest mechanic is rewritten | Preferred: practical for own original gameplay; not a claim of exact proprietary logic | New enemy, projectile, input + saved state |
| B. Host + licensed portable guest core | **One app, two cooperating modules** compiled for same Android ABI, bridged over stable C ABI / JNI | Feasible when both source codes and licenses allow embedding; do not instantiate two arbitrary full engine runtimes | Guest deterministic simulation + host renderer |
| C. Two cooperating Android apps | **Two packages** which voluntarily implement an explicit IPC protocol | Possible for synchronized state; Android lifecycle, app sandbox, battery, background execution and visibility restrict guarantees | Send state/events between two own demo apps |
| D. Neutral deterministic shared simulation | One core authority plus multiple renderers/clients | Useful for cross-game collaboration, multiplayer or several viewpoints | Shared tick, unit conversion, reproducible event queue |
| E. Render/video passthrough of third-party apps | Surface capture and compositing across different applications | High risk, often blocked by secure surfaces/performance/process isolation; require explicit capture consent | Proof-of-concept of **owned test apps only** |

### Rules

1. Prefer a single **Android host APK** with a reimplemented, licensed guest mechanic before dual-runtime designs.
2. For true two-engine operation, use open-source/authorized code, same ABI or separate supported processes, and a **versioned bridge contract**.
3. For two independent installed APKs, do not assume arbitrary process injection, state reading, direct surface access, shared UID, or ADB/Shizuku availability. Require both applications to cooperate voluntarily.
4. Serialize **state and events**, not game objects/pointers. Define authority, timestamps, axes, units, frame/tick rates, queue limits, schema version and restart epoch.
5. Keep copyrighted third-party assets local; build original art or converter that reads the user's authorized source files locally. Do not redistribute game binaries or bypass DRM/anti-cheat/app signing.
6. Require measured Android-specific performance (FPS, CPU, memory, battery/thermal) and device test results. No green CI without a tested APK counts as gameplay success.

## Bridge contract template

```json
{
  "schema": "android-fusion/0.1",
  "host": {"package": "org.example.host", "engine": "source-available", "abi": "arm64-v8a"},
  "guest": {"kind": "portable-source-module", "engine": "source-available"},
  "authority": {"player": "host", "input": "host", "combat": "host", "guest_simulation": "guest"},
  "coordinate": {"unit": "metre", "axes": "x-right,y-up,z-forward"},
  "timing": {"host_fps": 60, "simulation_hz": 30, "max_staleness_ms": 100},
  "transport": {"type": "in-process-C-ABI", "schema_version": 1, "max_queue": 128},
  "lifecycle": {"pause": "freeze-guest", "disconnect": "disable-guest-feature", "restart": "new-epoch"},
  "saves": {"owner": "host", "guest_namespace": "guest_v1"}
}
```

This is an example interface contract, **not** a measured runtime or universal fit. Do not copy identifiers for real games without verifying the engine/API.

## Validation gates (strict)

- L0: legal/source provenance and **read-only APK fingerprints**
- L1: host compiles and artifact SHA-256 recorded
- L2: Android emulator/real device installs the **actual APK**
- L3: game actually launches and stays alive
- L4: scripted gameplay oracle proves the new mechanic
- L5: save data/regression/crash paths verified
- L6: target Android hardware FPS, memory and thermal measured
- L7: reproducible signed release, attributed code/assets and rollback

Every claimed PASS must include run URL, commit, artifact and device or emulator evidence. A ZIP-inspection PASS is only L0.
