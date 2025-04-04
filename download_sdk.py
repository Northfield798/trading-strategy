import requests
import zipfile
import io
import os

def download_sdk():
    # GitHub API URL for the repository
    url = "https://api.github.com/repos/hyperliquid-dex/hyperliquid-python-sdk/zipball/main"
    
    # 发送请求获取仓库内容
    response = requests.get(url)
    
    if response.status_code == 200:
        # 创建临时目录
        os.makedirs("temp_sdk", exist_ok=True)
        
        # 解压下载的内容
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall("temp_sdk")
            
        print("SDK 下载成功！")
        return True
    else:
        print(f"下载失败，状态码：{response.status_code}")
        return False

if __name__ == "__main__":
    download_sdk() 