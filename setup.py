from setuptools import setup

setup(
    name='cpgw',
    packages=['cpgw'],
    version='1.3.0',
    description='Cooper Gateway',
    url='https://github.com/blavka/cpgw',
    author='Karel Blavka',
    author_email='karel.blavka@hardwario.com',
    license='MIT',
    keywords = ['cooper', 'cli', 'tool'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Environment :: Console',
        'Intended Audience :: Science/Research'
    ],
    install_requires=[
        'Click>=6.0', 'click-log>=0.2.1', 'pyserial==3.4', 'paho-mqtt>=1.0', 'simplejson>=3.6.0', 'pyzmq', 'schema'
    ],
    entry_points='''
        [console_scripts]
        cpgw=cpgw.cli:main
    '''
)

