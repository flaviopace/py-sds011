from setuptools import setup

setup(
    name='py-sds011',
    description='Python framework to read air quality sensor data from SDS011 and upload them to DB/AQIcn/Thinspeak',
    author='Flavio Pace',
    version='0.9',
    url='https://github.com/flaviopace/py-sds011',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Operating System :: Linux',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
    ],
    license='Apache-2.0',
    packages=[
        'sds011',
    ],
    install_requires=[
        'pyserial',
        'python-aqi',
        'mysql-connector-python',
        'httplib2'
    ],
)
