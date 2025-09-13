import os
import sys
import subprocess

def build_drag_drop():
    print('Dang build executable voi main3_drag_drop.py...')
    try:
        os.makedirs('dist', exist_ok=True)
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', 'EVONY_Auto_DragDrop',
            '--add-data', 'images;images',
            '--add-data', 'actions;actions',
            '--add-data', 'components;components',
            '--add-data', 'utils;utils',
            '--add-data', 'adb_tools;adb_tools',
            '--collect-all', 'cv2',
            '--collect-all', 'numpy',
            'main3_drag_drop.py'
        ]
        
        subprocess.run(cmd, check=True)
        print('✅ Build drag drop version thanh cong!')
        return True
    except subprocess.CalledProcessError as e:
        print(f'❌ Loi khi build: {e}')
        return False

if __name__ == '__main__':
    build_drag_drop()
