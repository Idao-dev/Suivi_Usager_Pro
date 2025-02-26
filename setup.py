from setuptools import setup, find_packages

setup(
    name="SuiviUsagerPro",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        'customtkinter',
        'pandas',
        'matplotlib'
    ],
    entry_points={
        'console_scripts': [
            'suiviusagerpro=src.main:main',
        ],
    },
) 