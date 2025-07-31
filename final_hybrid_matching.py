#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
from difflib import SequenceMatcher
import unicodedata
import time

def normalize_text(text):
    """テキストの正規化"""
    if pd.isna(text):
        return ""
    text = unicodedata.normalize('NFKC', str(text)).lower()
    text = re.sub(r'[（）()]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_words(text):
    """効率的な単語抽出"""
    if not text:
        return []
    
    text = normalize_text(text)
    
    # 日本語・英語境界で分割
    pattern = r'[\u4e00-\u9fff]+|[\u3040-\u309f]+|[\u30a0-\u30ff]+|[a-zA-Z0-9]+'
    words = re.findall(pattern, text)
    
    # 英語は2文字以上、日本語は1文字以上
    result = []
    for word in words:
        if re.match(r'^[a-zA-Z0-9]+$', word):
            if len(word) >= 2:
                result.append(word)
        else:
            result.append(word)
    
    return result

def word_similarity(words1, words2):
    """単語類似度計算（高速版）"""
    if not words1 or not words2:
        return 0.0, 0
    
    set1, set2 = set(words1), set(words2)
    common = len(set1 & set2)
    total = max(len(set1), len(set2))
    
    return common / total, common

def artist_similarity(artist1, artist2):
    """アーティスト類似度（高速版）"""
    if not artist1 or not artist2:
        return 0.0
    
    a1 = normalize_text(artist1).replace(' - topic', '').replace(' official', '')
    a2 = normalize_text(artist2).replace(' - topic', '').replace(' official', '')
    
    if len(a1) < 2 or len(a2) < 2:
        return 0.0
    
    return SequenceMatcher(None, a1, a2).ratio()

def progress_bar(current, total, stage="", width=50):
    """進捗バーの表示"""
    percent = current / total
    filled_width = int(width * percent)
    bar = '█' * filled_width + '░' * (width - filled_width)
    print(f'\r{stage} [{bar}] {current}/{total} ({percent*100:.1f}%)', end='', flush=True)

def main():
    print("🎵 最終版ハイブリッドマッチングシステム v1.0")
    print("=" * 60)
    
    start_time = time.time()
    
    # データ読み込み
    print("📂 データファイルを読み込み中...")
    try:
        original_df = pd.read_csv('list.csv', encoding='utf-8')
    except:
        original_df = pd.read_csv('list.csv', encoding='shift-jis')
    
    youtube_df = pd.read_csv('youtube_playlist.csv', encoding='utf-8')
    
    print(f"✅ 元リスト: {len(original_df)}曲")
    print(f"✅ YouTubeプレイリスト: {len(youtube_df)}曲")
    
    # 前処理：単語分割
    print("\n🔧 前処理中（単語分割）...")
    original_words = []
    for i, title in enumerate(original_df['.曲名']):
        progress_bar(i + 1, len(original_df), "単語分割")
        original_words.append(extract_words(title))
    
    print("\n🔧 YouTubeタイトル単語分割中...")
    youtube_words = []
    for i, title in enumerate(youtube_df['曲名']):
        progress_bar(i + 1, len(youtube_df), "YT単語分割")
        youtube_words.append(extract_words(title))
    
    print("\n")
    
    matches = []
    used_youtube = set()
    
    # 3段階マッチング
    thresholds = [
        (0.8, "🎯 高精度マッチング"),
        (0.6, "🎪 中精度マッチング"), 
        (0.4, "🔍 低精度マッチング")
    ]
    
    total_processed = 0
    
    for threshold, stage_name in thresholds:
        print(f"\n{stage_name} (スコア ≥ {threshold})")
        print("-" * 50)
        
        stage_count = 0
        unmatched_count = len(original_df) - len(matches)
        
        for i, row in original_df.iterrows():
            # 既にマッチ済みはスキップ
            if any(m['original_index'] == i + 1 for m in matches):
                continue
            
            # 進捗表示
            total_processed += 1
            if total_processed % 20 == 0 or total_processed <= 10:
                progress_bar(total_processed, unmatched_count, f"{stage_name}")
            
            best_score = 0.0
            best_match = None
            
            orig_words = original_words[i]
            orig_artist = row['.作曲者']
            
            for j, yt_row in youtube_df.iterrows():
                if j in used_youtube:
                    continue
                
                yt_words = youtube_words[j]
                yt_artist = yt_row['作曲者/アーティスト']
                
                # 単語類似度
                word_sim, common = word_similarity(orig_words, yt_words)
                
                # アーティスト類似度
                artist_sim = artist_similarity(orig_artist, yt_artist)
                
                # ハイブリッドスコア
                if artist_sim >= 0.8:
                    score = word_sim * 0.75 + artist_sim * 0.25
                    method = "hybrid_high_quality"
                elif artist_sim >= 0.5:
                    score = word_sim * 0.8 + artist_sim * 0.2
                    method = "hybrid_medium_quality"
                else:
                    score = word_sim * 0.9
                    method = "hybrid_word_based"
                
                if score >= threshold and score > best_score:
                    best_score = score
                    best_match = (j, yt_row, word_sim, artist_sim, common, method)
            
            if best_match:
                j, yt_row, word_sim, artist_sim, common, method = best_match
                used_youtube.add(j)
                stage_count += 1
                
                matches.append({
                    'original_index': i + 1,
                    'original_title': row['.曲名'],
                    'original_artist': row['.作曲者'],
                    'youtube_index': j + 1,
                    'youtube_title': yt_row['曲名'],
                    'youtube_artist': yt_row['作曲者/アーティスト'],
                    'youtube_url': yt_row['YouTubeURL'],
                    'video_id': yt_row['Video_ID'],
                    'hybrid_score': round(best_score, 3),
                    'word_similarity': round(word_sim, 3),
                    'artist_similarity': round(artist_sim, 3),
                    'common_words': common,
                    'method': method
                })
        
        print(f"\n✅ {stage_count}曲マッチング完了")
        total_processed = 0  # 次のステージ用にリセット
    
    # 結果保存
    print(f"\n💾 結果を保存中...")
    result_df = pd.DataFrame(matches)
    result_df.to_csv('final_hybrid_matches.csv', index=False, encoding='utf-8')
    
    # 処理時間計算
    elapsed_time = time.time() - start_time
    
    print(f"\n🎉 マッチング完了！")
    print("=" * 60)
    print(f"📊 総マッチ数: {len(matches)}曲")
    print(f"📈 マッチ率: {len(matches)/len(original_df)*100:.1f}%")
    print(f"⏱️ 処理時間: {elapsed_time:.1f}秒")
    
    # 品質統計
    print(f"\n📋 品質別統計:")
    method_counts = result_df['method'].value_counts()
    for method, count in method_counts.items():
        percentage = count / len(matches) * 100
        print(f"  • {method}: {count}曲 ({percentage:.1f}%)")
    
    # 重複チェック
    duplicates = result_df['video_id'].value_counts()
    dupe_count = (duplicates > 1).sum()
    print(f"\n🔗 Video ID重複: {dupe_count}件 {'✅' if dupe_count == 0 else '⚠️'}")
    
    # 高品質マッチ例
    high_quality = result_df[result_df['hybrid_score'] >= 0.95].head(5)
    if not high_quality.empty:
        print(f"\n⭐ 完璧マッチ例（スコア ≥ 0.95）:")
        for _, match in high_quality.iterrows():
            print(f"  • {match['original_title']} → {match['youtube_title']}")
            print(f"    スコア: {match['hybrid_score']} | 方式: {match['method']}")
    
    print(f"\n📁 結果ファイル: final_hybrid_matches.csv")
    print("🎵 マッチング処理が正常に完了しました！")

if __name__ == "__main__":
    main()
