"""Synthetic APK fixtures: no proprietary binaries or game assets."""
from zipfile import ZipFile

import pytest
from um.android import inspect_apk, fusion_plan


def fake_apk(path, names):
    with ZipFile(path, "w") as archive:
        archive.writestr("AndroidManifest.xml", b"synthetic-manifest")
        for name in names:
            archive.writestr(name, b"synthetic-test-bytes")
    return str(path)


def test_android_inspect_unity_il2cpp(tmp_path):
    path = fake_apk(tmp_path / "host.apk", [
        "lib/arm64-v8a/libunity.so",
        "lib/arm64-v8a/libil2cpp.so",
        "classes.dex",
        "assets/bin/Data/globalgamemanagers",
    ])
    item = inspect_apk(path)
    assert "unity" in item["engine_candidates"]
    assert item["abis"] == ["arm64-v8a"]
    assert item["has_dex"] is True
    assert item["manifest_present"] is True


def test_android_multiple_abis_and_engines(tmp_path):
    path = fake_apk(tmp_path / "game.apk", [
        "lib/armeabi-v7a/libcocos2dcpp.so",
        "lib/arm64-v8a/libcocos2dcpp.so",
    ])
    item = inspect_apk(path)
    assert item["engine_candidates"] == ["cocos2dx"]
    assert item["abis"] == ["arm64-v8a", "armeabi-v7a"]


def test_android_fusion_plan_recommends_host_mechanics_first(tmp_path):
    host = fake_apk(tmp_path / "a.apk", ["lib/arm64-v8a/libunity.so"])
    guest = fake_apk(tmp_path / "b.apk", ["lib/arm64-v8a/libcocos2dcpp.so"])
    result = fusion_plan([host, guest])
    assert result["shared_native_abis"] == ["arm64-v8a"]
    assert result["recommended_first_route"] == "one-host-port-original-mechanics-and-assets"
    assert "game-and-asset-ownership" in result["contract_required"]


def test_android_rejects_missing_manifest(tmp_path):
    path = tmp_path / "fake.apk"
    with ZipFile(path, "w") as archive:
        archive.writestr("classes.dex", b"x")
    with pytest.raises(ValueError, match="NOT_AN_APK_NO_MANIFEST"):
        inspect_apk(str(path))


def test_android_rejects_single_apk(tmp_path):
    with pytest.raises(ValueError, match="AT_LEAST_TWO"):
        fusion_plan([str(tmp_path / "a.apk")])
