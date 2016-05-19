from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(

    install_requires=required,
    name='monitoringHisto',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1',

    description='FIWARE Historical monitoring collector',
    long_description='',

    # The project's main homepage.
    url='https://github.com/SmartInfrastructures/FIWARELab-monitoringAPI',

    # Author details
    author='Daniele Santoro',
    author_email='',

    # Choose your license
    license='Apache v2.0',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['monitoringHisto'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={'console_scripts': [
            'monitoringHisto=monitoringHisto.monitoringHisto:main',
        ],
    },
)



