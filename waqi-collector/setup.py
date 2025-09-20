import setuptools

setuptools.setup(
    name='aqi-dataflow',
    version='1.0',
    install_requires=[
        'apache-beam[gcp]',
        'google-cloud-storage'
    ],
    packages=setuptools.find_packages()
)