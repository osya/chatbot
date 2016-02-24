from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=[], includes=['lxml._elementpath', 'gzip'], excludes=['collections.abc'])

base = 'Console'

executables = [
    Executable('main.py', base=base, targetName='ai.exe')
]

setup(name='chat_bot',
      version='1.0',
      description='',
      options=dict(build_exe=buildOptions),
      executables=executables, requires=['lxml', 'requests', 'cx_Freeze', ])
