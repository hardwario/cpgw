from setuptools import setup

setup(
    name='cpgw',
    packages=['cpgw'],
    version='@@VERSION@@',
    description='Cooper Gateway',
    url='https://github.com/hardwario/cpgw',
    author='HARDWARIO s.r.o.',
    author_email='ask@hardwario.com',
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
        'Click>=6.0', 'click-log>=0.2.1', 'pyserial==3.4', 'simplejson>=3.6.0', 'pyzmq>=17.1', 'schema>=0.6', 'PyYAML>=3.13'
    ],
    entry_points='''
        [console_scripts]
        cpgw=cpgw.app:main
    '''
)

