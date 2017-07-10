from setuptools import setup

setup(
    name='DataPylot',
    version='0.0.1.dev1',
    description='A python tool that generates web-based visualizations based on a datasource and config',
    long_description=open('README.md').read(),
    author='Mr Trustworthy',
    license='unlicensed',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',

        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database :: Front-Ends',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',

        'Programming Language :: Python :: 3.6',
    ],
    keywords='data visualization development',

    packages=['datapylot'],
    install_requires=open('requirements.txt').read(),
    python_requires='~=3.6',

)
