from setuptools import setup

setup(
    name='ramen',
    version='0.1.0',    
    description='A Python library for inexpensive process-structure-property calculations for alloys.',
    url='https://code.ornl.gov/ramen/ramen',
    author='Stephen DeWitt',
    author_email='dewittsj@ornl.gov',
    license='ORNL Internal Software - Currently unlicensed',
    packages=['ramen'],
    install_requires=[ 'mist',
                      "numpy"           
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
    ],
)