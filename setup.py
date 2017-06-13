import unittest
from setuptools import setup


def test_suite():
    test_loader = unittest.TestLoader()
    suite = test_loader.discover('tests', pattern='test_*.py')
    return suite

setup(
    name='Tapylow',
    version='0.1dev',
    packages=['pylow'],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt').read(),
    test_suite='test.test_main'
)
