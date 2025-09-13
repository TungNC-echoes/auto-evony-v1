#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil

def install_requirements():
    print('Dang cai dat dependencies...')
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print('✅ Cai dat dependencies thanh cong!')
        return True
    except subprocess.CalledProcessError as e:
        print(f'❌ Loi khi cai dat dependencies: {e}')
        return False

def download_adb():
    print('Dang tai ADB Platform Tools...')
    try:
        subprocess.run([sys.executable, 'download_adb.py'], check=True)
        print('✅ Tai ADB thanh cong!')
        return True
    except subprocess.CalledProcessError as e:
        print(f'❌ Loi khi tai ADB: {e}')
        return False

def backup_original_adb_utils():
    if os.path.exists('utils/adb_utils.py') and not os.path.exists('utils/adb_utils_backup.py'):
        shutil.copy2('utils/adb_utils.py', 'utils/adb_utils_backup.py')
        print('✅ Da backup adb_utils.py goc')

def replace_adb_utils():
    if os.path.exists('utils/adb_utils_new.py'):
        shutil.copy2('utils/adb_utils_new.py', 'utils/adb_utils.py')
        print('✅ Da thay the adb_utils.py')

def build_executable():
    print('Dang build executable...')
    try:
        os.makedirs('dist', exist_ok=True)
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', 'EVONY_Auto',
            '--add-data', 'images;images',
            '--add-data', 'actions;actions',
            '--add-data', 'components;components',
            '--add-data', 'utils;utils',
            '--add-data', 'adb_tools;adb_tools',
            '--hidden-import', 'cv2',
            '--hidden-import', 'numpy',
            '--hidden-import', 'tkinter',
            '--hidden-import', 'PIL',
            'main3_gui.py'
        ]
        
        subprocess.run(cmd, check=True)
        print('✅ Build executable thanh cong!')
        return True
    except subprocess.CalledProcessError as e:
        print(f'❌ Loi khi build executable: {e}')
        return False

def cleanup():
    print('Dang don dep...')
    cleanup_dirs = ['build', '__pycache__']
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    print('✅ Don dep hoan tat!')

def main():
    print('🚀 Bat dau qua trinh build EVONY Auto...')
    print('=' * 50)
    
    if not install_requirements():
        return False
    
    if not download_adb():
        return False
    
    backup_original_adb_utils()
    replace_adb_utils()
    
    if not build_executable():
        return False
    
    cleanup()
    
    print('=' * 50)
    print('🎉 Hoan thanh! File executable da duoc tao trong thu muc dist/')
    print('📁 File: dist/EVONY_Auto.exe')
    print('💡 Ban co the copy file nay sang may khac va chay truc tiep!')
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print('❌ Qua trinh build that bai!')
        sys.exit(1)
