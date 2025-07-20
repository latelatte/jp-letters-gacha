import json
import requests
import os
from typing import Dict, Any, Optional
from pathlib import Path


class GistDataManager:
    """GitHub Gistを使ってdata.jsonを永続化するクラス"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.gist_id = os.getenv("GIST_ID")
        self.filename = "data.json"
        
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN環境変数が設定されていません")
        if not self.gist_id:
            raise ValueError("GIST_ID環境変数が設定されていません")
            
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # ローカルキャッシュファイル
        self.local_cache = Path("./assets/data_cache.json")
    
    def download_from_gist(self) -> Dict[str, Any]:
        """Gistからデータをダウンロードしてローカルキャッシュに保存"""
        try:
            url = f"https://api.github.com/gists/{self.gist_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            gist_data = response.json()
            
            if self.filename not in gist_data["files"]:
                # ファイルが存在しない場合は空のデータを返す
                data = {}
            else:
                file_content = gist_data["files"][self.filename]["content"]
                data = json.loads(file_content) if file_content.strip() else {}
            
            # ローカルキャッシュに保存
            self._save_to_cache(data)
            
            return data
            
        except requests.RequestException as e:
            print(f"⚠️ Gistからのダウンロードに失敗: {e}")
            return self._load_from_cache()
        except json.JSONDecodeError as e:
            print(f"⚠️ JSONデコードエラー: {e}")
            return self._load_from_cache()
        except Exception as e:
            print(f"⚠️ 予期しないエラー: {e}")
            return self._load_from_cache()
    
    def upload_to_gist(self, data: Dict[str, Any]) -> bool:
        """データをGistにアップロード"""
        try:
            content = json.dumps(data, ensure_ascii=False, indent=2)
            
            payload = {
                "files": {
                    self.filename: {
                        "content": content
                    }
                }
            }
            
            url = f"https://api.github.com/gists/{self.gist_id}"
            response = requests.patch(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            # アップロード成功時はローカルキャッシュも更新
            self._save_to_cache(data)
            
            print("✅ データをGistに保存しました")
            return True
            
        except requests.RequestException as e:
            print(f"❌ Gistへのアップロードに失敗: {e}")
            # ローカルキャッシュには保存しておく
            self._save_to_cache(data)
            return False
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            self._save_to_cache(data)
            return False
    
    def _load_from_cache(self) -> Dict[str, Any]:
        """ローカルキャッシュからデータを読み込み"""
        try:
            if self.local_cache.exists():
                with open(self.local_cache, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ ローカルキャッシュの読み込みに失敗: {e}")
        
        return {}
    
    def _save_to_cache(self, data: Dict[str, Any]):
        """データをローカルキャッシュに保存"""
        try:
            self.local_cache.parent.mkdir(exist_ok=True)
            with open(self.local_cache, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ ローカルキャッシュの保存に失敗: {e}")
    
    def sync_with_gist(self) -> Dict[str, Any]:
        """Gistと同期してデータを取得（起動時用）"""
        print("🔄 Gistからデータを同期中...")
        return self.download_from_gist()
