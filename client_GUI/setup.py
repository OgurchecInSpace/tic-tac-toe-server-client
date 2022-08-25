# Сборщик программы
from cx_Freeze import Executable, setup

executables = [Executable('client.py', base='Win32GUI', targetName='Client-TicTacToe')]

# Библиотеки и т.д., которые не надо ставит
excludes = ['html', 'http', 'email', 'multiprocessing', 'unittest',
            'logging', 'urllib', 'argparse', 'webbrowser', 'warnings',
            'decimal', 'audioop', 'csv', 'xml', 'email', 'html', 'http',
            'fractions', 'cmath', 'statistics', 'zlib', 'gzip', 'zipfile',
            'tarfile', 'pydoc_data', 'calendar', 'copy', 'multipoccessing',
            'lib2to3', 'concurrent', 'urllib`']

# Библиотеки, которые надо в архив
zip_include_packages = ['collections', 'encodings', 'importlib', 'socket', 'threading', 'tkinter']

# Включаемые другие файлы
include_files = ['other_files']

# Настройки
options = {
    'build_exe': {
        'include_msvcr': True,
        # 'excludes': excludes,
        'zip_include_packages': zip_include_packages,
        'include_files': include_files,
        'build_exe': 'build_windows'
    }
}


setup(name='Client tic-tac-toe online',
      version='1.0.0',
      description='Client tic-tac-toe online, haha',
      executables=executables,
      options=options)
