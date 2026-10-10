# Android original-engine adapter work — 2026-10-10

Goal: original PvZ + Clash Royale on Android, no replacement game.
Base: Universal Modder PR #1, 26fe72a3d0fad7ac6b256fe29fac75018881f911.
Route: original-engine state exchange; implement and measure transport first.
User must have both original Android installations. They were found via pm path.
KB searches for PvZ and Titan returned no matches.

Added native POSIX transport, contract tests, CMake target, and actual per-game ELF
recon profiles. Compiled/executed the native test on the connected Android 16 ARM64
phone using Termux clang++. No original game launched/patched; game state untouched.
The native probe ran against both packages and all relevant splits. Evidence in
native/android-bridge/device-evidence.txt. Export counts include GLOBAL and WEAK;
initial manual probe counted only GLOBAL (45000 for PvZ), final counts include both.

Transport is functional; PvZ/Titan runtime bindings remain unimplemented. Missing
Titan callable interface is a concrete blocker to a complete original-engine pair.
Do not report tests with synthetic peers as gameplay. Follow README's missing-work
list and CONTRACT before further engine integration. Phone lab remains at
/data/data/com.termux/files/home/um-android-adapter-lab.
