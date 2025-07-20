#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gistデータマネージャーのテストスクリプト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def test_gist_manager():
    """Gistマネージャーの動作テスト"""
    print("🧪 Gistデータマネージャーのテスト")
    print("=" * 50)
    
    # 環境変数の確認
    github_token = os.getenv("GITHUB_TOKEN")
    gist_id = os.getenv("GIST_ID")
    
    if not github_token:
        print("❌ GITHUB_TOKEN環境変数が設定されていません")
        return False
    
    if not gist_id:
        print("❌ GIST_ID環境変数が設定されていません")
        return False
    
    print(f"✅ GITHUB_TOKEN: {'*' * len(github_token[:10])}...")
    print(f"✅ GIST_ID: {gist_id}")
    
    try:
        from logics.gist_manager import GistDataManager
        
        # Gistマネージャーを初期化
        print("\n📡 Gistマネージャーを初期化中...")
        manager = GistDataManager()
        
        # 現在のデータをダウンロード
        print("⬇️ Gistからデータをダウンロード中...")
        current_data = manager.download_from_gist()
        print(f"✅ ダウンロード完了: {len(current_data)}ユーザーのデータ")
        
        # テスト用データを追加
        test_user_id = "test_user_123456"
        current_data[test_user_id] = {
            "points": 100,
            "last_claim_date": "2025-07-21",
            "letters": ["テ", "ス", "ト"],
            "login_count": 1,
            "mission_cleared": "2025-07-21",
            "ssr_points": 0
        }
        
        # Gistにアップロード
        print("⬆️ テストデータをGistにアップロード中...")
        success = manager.upload_to_gist(current_data)
        
        if success:
            print("✅ アップロード成功!")
            
            # アップロードしたデータを再ダウンロードして確認
            print("🔄 データを再ダウンロードして確認中...")
            verified_data = manager.download_from_gist()
            
            if test_user_id in verified_data:
                print("✅ テストデータが正常に保存・読み込みされました!")
                
                # テストデータを削除
                del verified_data[test_user_id]
                manager.upload_to_gist(verified_data)
                print("✅ テストデータを削除しました")
                
                return True
            else:
                print("❌ テストデータの確認に失敗しました")
                return False
        else:
            print("❌ アップロードに失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def test_data_manager_integration():
    """data_managerとの統合テスト"""
    print("\n🔧 data_manager統合テスト")
    print("=" * 50)
    
    try:
        from logics.data_manager import init_data_manager, load_data, save_data
        
        # データマネージャーを初期化
        print("🚀 データマネージャーを初期化中...")
        init_data_manager()
        
        # データの読み込み
        print("📖 データを読み込み中...")
        data = load_data()
        print(f"✅ 読み込み完了: {len(data)}ユーザーのデータ")
        
        # テスト用データを追加
        test_user_id = "integration_test_789"
        original_count = len(data)
        
        data[test_user_id] = {
            "points": 50,
            "last_claim_date": "2025-07-21",
            "letters": ["統", "合", "テ", "ス", "ト"],
            "login_count": 2,
            "mission_cleared": "2025-07-21",
            "ssr_points": 1
        }
        
        # データの保存
        print("💾 テストデータを保存中...")
        save_data(data)
        
        # データの再読み込み
        print("🔄 データを再読み込み中...")
        reloaded_data = load_data()
        
        if test_user_id in reloaded_data and len(reloaded_data) == original_count + 1:
            print("✅ 統合テスト成功!")
            
            # テストデータを削除
            del reloaded_data[test_user_id]
            save_data(reloaded_data)
            print("✅ テストデータを削除しました")
            
            return True
        else:
            print("❌ 統合テストに失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Gistデータ永続化システムのテスト")
    print("=" * 60)
    
    # 基本的なGistマネージャーのテスト
    gist_test_result = test_gist_manager()
    
    if gist_test_result:
        # 統合テスト
        integration_test_result = test_data_manager_integration()
        
        if integration_test_result:
            print("\n🎉 すべてのテストに成功しました!")
            print("✅ Gistデータ永続化システムは正常に動作しています")
        else:
            print("\n❌ 統合テストに失敗しました")
    else:
        print("\n❌ Gistマネージャーのテストに失敗しました")
        print("💡 環境変数の設定を確認してください")
