from setuptools import setup

setup(name='TSP',
      version='1.0',
      description='TSP',
      author='Tydus Ken',
      author_email='Tydus@Tydus.org',
      url='http://github.com/tyeken8/tsp',
      install_requires=[
          'mongoengine>=0.5',
          'tornado>=2.0',
          'argparse>=1.0',
          ],
     )
