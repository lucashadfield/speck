from setuptools import setup, find_packages

setup(
    name='speck',
    version='0.3.3',
    author='Lucas Hadfield',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'pillow',
        'opencv-python',
        'ipywidgets',
        'requests',
        'pytest',
        'pytest-mpl',
    ],
    include_package_data=True,
)
