import json
from pathlib import Path

assets = Path("assets")
hiragana = json.loads(assets.joinpath("hiragana.json").read_text(encoding="utf-8"))
katakana = json.loads(assets.joinpath("katakana.json").read_text(encoding="utf-8"))
jouyou = json.loads(assets.joinpath("jouyou_kanji.json").read_text(encoding="utf-8"))

# 単文字辞書（文字のみリスト化）
hiragana_chars = [entry["kana"] for entry in hiragana]
katakana_chars = [entry["kana"] for entry in katakana]
jouyou_chars = list(jouyou.keys())  # 常用漢字：キーが各文字

print(len(hiragana_chars), len(katakana_chars), len(jouyou_chars))