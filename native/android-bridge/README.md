# Android native bridge: transport prototype, not a playable crossover

This ports the state/event channel idea from Universal Modder's PC passthrough
examples to Android-compatible C++17/POSIX. It does not port ScriptHookV, Fabric,
the compositor, or either game's engine binding.

## Reproduce

```
c++ -std=c++17 -Wall -Wextra -Werror test_bridge.cpp -o um_bridge_test
./um_bridge_test
```

Run from this directory on Linux or Termux. Alternatively use CMake/CTest.
For an NDK build pass the NDK toolchain, ANDROID_ABI=arm64-v8a and ANDROID_PLATFORM
appropriate to the host app. No APK build or NDK cross-build has been verified.

Probe local game APKs (all splits accepted):

```
python -m um.cli android native-probe pvz /private/pvz/base.apk
python -m um.cli android native-probe clash /private/clash/*.apk
```

Requires readelf or --readelf /path/to/llvm-readelf. It reads libraries into
a temporary file, inspects ELF metadata, then deletes that file. It does not
load or execute proprietary code. Package identity is not inferred from filenames.

## Implemented and verified

Linux and Android 16/aarch64 Termux compilation and execution. A parent and child
process exchange a synthetic spawn/damage pair. Same-process tests cover pause,
resume, malformed packets, stale epochs and bounded socket backpressure.
The synthetic peer is not PvZ or Titan. See device-evidence.txt for actual output.

Native probes ran against both installations. PvZ exported candidate gameplay
functions. Clash libg.so exposed no defined GLOBAL/WEAK dynamic symbols; its
companion exposed JNI_OnLoad. Hidden/internal functions may still exist.
These findings neither prove impossibility nor provide a callable engine API.

## Missing for the user's requested original-engine crossover

1. PvZ binding: verified ABI signatures, Board/Plant lifetimes, engine-thread
   scheduling, render/input hooks, version-specific initialization and unload.
2. Titan binding: identify executable simulation entry points and establish an
   offline lifecycle. JNI_OnLoad alone does not expose combat or rendering.
3. Concrete world/coordinate mapping and combat ownership for both engines.
4. Android lifecycle, authenticated descriptor handoff between cooperating apps,
   GPU surfaces/compositor, audio arbitration and save integration.
5. End-to-end APK build and gameplay tests against the original engines.

Do not call candidate symbols with guessed signatures or guessed object pointers.
No retail offsets, game binaries, account data, or game assets are included.
NDK API reference: https://developer.android.com/ndk/guides/stable_apis
