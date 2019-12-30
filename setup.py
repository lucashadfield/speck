from setuptools import setup, find_packages

setup(
    name='speck',
    version='0.2.2',
    author='Lucas Hadfield',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'pillow', 'opencv-python', 'ipywidgets'],
    include_package_data=True,
)
