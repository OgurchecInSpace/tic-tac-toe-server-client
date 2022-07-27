# Сборщик программы
from cx_Freeze import Executable, setup

executables = [Executable('client.py', base='Win32GUI')]

# Библиотеки и т.д., которые не надо ставит
excludes = ['html', 'http', 'email', 'multiprocessing', 'unittest',
            'logging', 'urllib', 'argparse', 'webbrowser', 'warnings',
            'decimal', 'audioop', 'csv', 'tkinter', 'xml'
            'fractions', 'cmath', 'statistics', 'zlib', 'gzip', 'zipfile',
            'tarfile', 'pydoc_data', 'calendar', 'copy']

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
    }
}


setup(name='Client tic-tac-toe online',
      version='0.0.1',
      description='Client tic-tac-toe online, haha',
      executables=executables,
      options=options)
