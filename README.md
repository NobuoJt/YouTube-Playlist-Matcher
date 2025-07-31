# 🎵 YouTube Playlist Song Matcher

YouTubeプレイリストと楽曲リストの高精度マッチングシステム

## 📋 概要

このプロジェクトは、CSVファイルに記載された楽曲リストとYouTubeプレイリストの楽曲を、**単語ベース + アーティスト考慮**のハイブリッドアルゴリズムで自動マッチングするシステムです。

### 🌟 主な特徴

- **高精度マッチング**: 単語レベルでの類似度計算とアーティスト情報を組み合わせ
- **段階的処理**: 高精度 → 中精度 → 低精度の3段階でマッチング
- **重複完全解消**: Video IDの重複を0件に抑制
- **進捗表示**: リアルタイムの処理状況表示
- **日本語対応**: 漢字・ひらがな・カタカナ・英数字の境界を考慮した単語分割

## 📊 処理結果

- **総楽曲数**: 572曲
- **マッチング成功**: 316曲（55.2%）
- **重複数**: 0件
- **処理時間**: 約24秒

### 品質別内訳

- **高品質マッチング**: 149曲（47.2%）- アーティスト高一致
- **単語ベースマッチング**: 148曲（46.8%）- 単語主体
- **中品質マッチング**: 19曲（6.0%）- アーティスト中一致

## 🚀 使用方法

### 前提条件

- Python 3.11以上
- 仮想環境（推奨）

### セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd YouTube Playlist Matcher

# 仮想環境を作成
python -m venv .venv

# 仮想環境をアクティベート（Windows）
.venv\Scripts\activate

# 仮想環境をアクティベート（macOS/Linux）
source .venv/bin/activate

# 必要なパッケージをインストール
pip install pandas yt-dlp requests beautifulsoup4
```

### 必要なデータファイルの準備

クローン後、以下のファイルを用意してください：

1. **楽曲リスト**: `list.csv`
    ```csv
    .曲名,.作曲者
    楽曲名1,アーティスト1
    楽曲名2,アーティスト2
    ...
    ```

2. **YouTubeプレイリストURL**: `url`
    ```
    https://music.youtube.com/playlist?list=YOUR_PLAYLIST_ID
    ```

    ```

### 実行手順

1. **YouTubeプレイリストの情報取得**

   ```bash
   python get_youtube_playlist.py
   ```

2. **ハイブリッドマッチング実行**

   ```bash
   python final_hybrid_matching.py
   ```

3. **結果をメインCSVに統合**

   ```bash
   python update_main_csv.py
   ```

## 📁 ファイル構成

```text
YouTube Playlist Matcher/
├── 📊 データファイル (Git除外)
│   ├── list.csv                      # 元の楽曲リスト
│   ├── youtube_playlist.csv          # YouTubeプレイリスト情報
│   ├── 曲.xlsx                       # 元のExcelファイル
│   └── url                           # YouTubeプレイリストURL
│
├── 🎵 メインシステム
│   ├── final_hybrid_matching.py      # 最終版マッチングシステム
│   ├── get_youtube_playlist.py       # プレイリスト取得スクリプト
│   └── update_main_csv.py            # CSV更新ツール
│
├── 📈 結果ファイル (Git除外)
│   ├── final_hybrid_matches.csv      # 詳細マッチング結果
│   └── list_final_hybrid.csv         # 最終統合ファイル
│
├── 🔧 環境
│   ├── .venv/                        # Python仮想環境 (Git除外)
│   ├── .gitignore                    # Git除外設定
│   └── README.md                     # このファイル
│
```

**⚠️ 注意**: 個人の楽曲データファイル（`list.csv`, `*.xlsx`, `url`等）は`.gitignore`によりGitリポジトリに含まれません。
    └── .venv/                        # Python仮想環境
```

## 🔬 技術詳細

### アルゴリズム

1. **正規化処理**
   - Unicode正規化（NFKC）
   - 全角→半角変換
   - 記号・括弧の除去

2. **単語抽出**

   ```python
   # 日本語・英語境界で分割
   pattern = r'[\u4e00-\u9fff]+|[\u3040-\u309f]+|[\u30a0-\u30ff]+|[a-zA-Z0-9]+'
   ```

3. **ハイブリッドスコア計算**
   - アーティスト一致度 ≥ 0.8: `単語類似度 × 0.75 + アーティスト類似度 × 0.25`
   - アーティスト一致度 ≥ 0.5: `単語類似度 × 0.8 + アーティスト類似度 × 0.2`
   - その他: `単語類似度 × 0.9`

4. **段階的マッチング**
   - 第1段階: スコア ≥ 0.8（高精度）
   - 第2段階: スコア ≥ 0.6（中精度）
   - 第3段階: スコア ≥ 0.4（低精度）

### 使用ライブラリ

- **pandas**: データ処理・CSV操作
- **yt-dlp**: YouTube情報取得
- **unicodedata**: 文字正規化
- **difflib.SequenceMatcher**: 文字列類似度計算
- **re**: 正規表現処理

## 📝 出力形式

### final_hybrid_matches.csv

```csv
original_index,original_title,original_artist,youtube_index,youtube_title,youtube_artist,youtube_url,video_id,hybrid_score,word_similarity,artist_similarity,common_words,method
```

### list_final_hybrid.csv

元のリストに以下の列が追加されます：

- `YouTube番号_新`
- `YouTubeタイトル_新`
- `YouTube作曲者_新`
- `YouTubeURL_新`
- `Video_ID_新`
- `ハイブリッドスコア`
- `単語類似度`
- `アーティスト類似度`
- `共通単語数`
- `マッチング方式`

## 🎯 特徴的な改善点

### 問題解決

- **重複排除**: 以前の25件のVideo ID重複を0件に解消
- **精度向上**: 文字レベルから単語レベルのマッチングに改良
- **YouTubeの特性対応**: "- Topic"チャンネルやアップロード者名の適切な処理

### マッチング品質向上例

- `Angel Dust (2008 mix)` → 正確な同名楽曲マッチング
- `far in the blue sky... [Trance]` → アーティスト名付きタイトルの適切な処理
- `DJ Chipstyler - Control Interference +` → 長いタイトルの高精度マッチング

## 🤝 貢献

バグ報告や改善提案は Issue でお知らせください。

## 📄 ライセンス

MIT License

## 🏷️ バージョン履歴

### v1.0.0 (2025-08-01)

- 最終版ハイブリッドマッチングシステム完成
- 単語ベース + アーティスト考慮アルゴリズム実装
- 段階的マッチング機能追加
- 進捗表示機能追加
- 重複完全解消
- 316曲のマッチング成功（55.2%）

---

**開発者**: GitHub Copilot  
**作成日**: 2025年8月1日
