# Сборщик программы
from cx_Freeze import Executable, setup

executables = [Executable('client.py')]

# Библиотеки и т.д., которые не надо ставит
excludes = ['html', 'http', 'email', 'multiprocessing', 'unittest',
            'logging', 'urllib', 'argparse', 'webbrowser', 'warnings',
            'decimal', 'audioop', 'csv', 'tkinter', 'xml'
            'fractions', 'cmath', 'statistics', 'zlib', 'gzip', 'zipfile',
            'tarfile', 'pydoc_data', 'calendar', 'copy']

# Библиотеки, которые надо в архив
zip_include_packages = ['collections', 'encodings', 'importlib', 'socket', 'threading']

# Настройки
options = {
    'build_exe': {
        'include_msvcr': True,
        'excludes': excludes,
        'zip_include_packages': zip_include_packages
    }
}


setup(name='Client',
      version='0.0.1',
      description='Client',
      executables=executables,
      options=options)
