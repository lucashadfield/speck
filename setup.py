from setuptools import setup, find_packages

setup(
    name='speck',
    version='0.2.4',
    author='Lucas Hadfield',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'pillow',
        'opencv-python',
        'ipywidgets',
        'requests',
    ],
    include_package_data=True,
)
