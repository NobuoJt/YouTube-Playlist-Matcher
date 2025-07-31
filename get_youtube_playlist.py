#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTubeプレイリストから動画情報を取得するスクリプト
"""

import yt_dlp
import json
import csv
import sys

def get_playlist_info(playlist_url):
    """YouTubeプレイリストの情報を取得"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # メタデータのみ取得（ダウンロードしない）
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            return info
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def save_playlist_to_csv(playlist_info, output_file):
    """プレイリスト情報をCSVファイルに保存"""
    if not playlist_info or 'entries' not in playlist_info:
        print("プレイリスト情報が取得できませんでした")
        return False
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['番号', '曲名', '作曲者/アーティスト', 'YouTubeURL', 'Video_ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for i, entry in enumerate(playlist_info['entries'], 1):
                if entry:  # Noneでない場合のみ処理
                    title = entry.get('title', 'Unknown Title')
                    uploader = entry.get('uploader', 'Unknown Artist')
                    video_id = entry.get('id', '')
                    video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ''
                    
                    writer.writerow({
                        '番号': i,
                        '曲名': title,
                        '作曲者/アーティスト': uploader,
                        'YouTubeURL': video_url,
                        'Video_ID': video_id
                    })
            
        print(f"プレイリスト情報を {output_file} に保存しました")
        print(f"総楽曲数: {len([e for e in playlist_info['entries'] if e])}")
        return True
        
    except Exception as e:
        print(f"CSVファイルの保存中にエラーが発生しました: {e}")
        return False

def main():
    # URLファイルからプレイリストURLを読み取り
    try:
        with open('url', 'r', encoding='utf-8') as f:
            playlist_url = f.read().strip()
    except FileNotFoundError:
        print("urlファイルが見つかりません")
        return
    except Exception as e:
        print(f"urlファイルの読み取り中にエラーが発生しました: {e}")
        return
    
    print(f"プレイリストURL: {playlist_url}")
    print("プレイリスト情報を取得中...")
    
    # プレイリスト情報を取得
    playlist_info = get_playlist_info(playlist_url)
    
    if playlist_info:
        print(f"プレイリスト名: {playlist_info.get('title', 'Unknown')}")
        
        # CSVファイルに保存
        save_playlist_to_csv(playlist_info, 'youtube_playlist.csv')
        
        # JSONファイルにも保存（デバッグ用）
        with open('playlist_info.json', 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, ensure_ascii=False, indent=2)
        print("詳細情報を playlist_info.json に保存しました")
    else:
        print("プレイリスト情報の取得に失敗しました")

if __name__ == "__main__":
    main()
