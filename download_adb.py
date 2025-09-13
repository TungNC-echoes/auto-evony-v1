import os
import urllib.request
import zipfile
import shutil

def download_adb():
    adb_url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    zip_path = "platform-tools.zip"
    
    print("Dang tai ADB Platform Tools...")
    urllib.request.urlretrieve(adb_url, zip_path)
    
    print("Dang giai nen ADB...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    if os.path.exists("platform-tools"):
        for file in ["adb.exe", "AdbWinApi.dll", "AdbWinUsbApi.dll"]:
            src = os.path.join("platform-tools", file)
            dst = os.path.join("adb_tools", file)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"Da copy {file} vao adb_tools/")
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
    if os.path.exists("platform-tools"):
        shutil.rmtree("platform-tools")
    
    print("Hoan thanh tai ADB!")

if __name__ == "__main__":
    download_adb()
