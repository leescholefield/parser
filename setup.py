from distutils.core import setup

setup(name='Parser',
      version='1.0',
      description='Library for parsing a document.',
      author='Lee Scholefield',
      url='https://github.com/leescholefield/apl',
      packages=['apl'],
      install_requires=[
            'lxml',
      ]
      )
