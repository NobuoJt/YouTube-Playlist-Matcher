#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

def update_main_csv():
    print("🔄 メインCSVファイルを最終マッチング結果で更新中...")
    
    # 元のリストとマッチング結果を読み込み
    try:
        original_df = pd.read_csv('list.csv', encoding='utf-8')
    except:
        original_df = pd.read_csv('list.csv', encoding='shift-jis')
    
    final_matches_df = pd.read_csv('final_hybrid_matches.csv', encoding='utf-8')
    
    print(f"📋 元リスト: {len(original_df)}曲")
    print(f"🎯 マッチング結果: {len(final_matches_df)}曲")
    
    # 新しい列を準備
    original_df['YouTube番号_新'] = ''
    original_df['YouTubeタイトル_新'] = ''
    original_df['YouTube作曲者_新'] = ''
    original_df['YouTubeURL_新'] = ''
    original_df['Video_ID_新'] = ''
    original_df['ハイブリッドスコア'] = ''
    original_df['単語類似度'] = ''
    original_df['アーティスト類似度'] = ''
    original_df['共通単語数'] = ''
    original_df['マッチング方式'] = ''
    
    # マッチング結果を統合
    matched_count = 0
    for _, match in final_matches_df.iterrows():
        idx = match['original_index'] - 1  # 0ベースのインデックスに変換
        
        if idx < len(original_df):
            original_df.loc[idx, 'YouTube番号_新'] = match['youtube_index']
            original_df.loc[idx, 'YouTubeタイトル_新'] = match['youtube_title']
            original_df.loc[idx, 'YouTube作曲者_新'] = match['youtube_artist']
            original_df.loc[idx, 'YouTubeURL_新'] = match['youtube_url']
            original_df.loc[idx, 'Video_ID_新'] = match['video_id']
            original_df.loc[idx, 'ハイブリッドスコア'] = match['hybrid_score']
            original_df.loc[idx, '単語類似度'] = match['word_similarity']
            original_df.loc[idx, 'アーティスト類似度'] = match['artist_similarity']
            original_df.loc[idx, '共通単語数'] = match['common_words']
            original_df.loc[idx, 'マッチング方式'] = match['method']
            matched_count += 1
    
    # 最終結果を保存
    output_filename = 'list_final_hybrid.csv'
    original_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"✅ {matched_count}曲のマッチング結果を統合完了")
    print(f"💾 最終結果ファイル: {output_filename}")
    
    # 統計情報
    print(f"\n📊 最終統計:")
    print(f"  • 総楽曲数: {len(original_df)}曲")
    print(f"  • マッチング成功: {matched_count}曲 ({matched_count/len(original_df)*100:.1f}%)")
    print(f"  • マッチング失敗: {len(original_df) - matched_count}曲 ({(len(original_df) - matched_count)/len(original_df)*100:.1f}%)")
    
    # 品質別統計
    quality_stats = original_df['マッチング方式'].value_counts()
    print(f"\n🎯 マッチング品質別統計:")
    for quality, count in quality_stats.items():
        if quality:  # 空でない場合のみ
            print(f"  • {quality}: {count}曲")
    
    print(f"\n🎉 list.csv が最終ハイブリッドマッチング結果で更新されました！")
    print(f"📁 新しいファイル: {output_filename}")

if __name__ == "__main__":
    update_main_csv()
