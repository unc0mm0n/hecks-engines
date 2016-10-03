from distutils.core import setup


def readme(file):
    with open(file) as f:
        return f.read()

setup(
    name='hecks-engines',
    version='0.0.0',
    packages=['hecks_engines'],
    url='https://github.com/unc0mm0n/hecks-engines',
    license='WTFPL',
    author='YuvalW',
    author_email='yvw.bor@gmail.com',
    description='Collection of HTP compliant Hecks engines.',
    long_description=readme("README.rst"),
    include_package_data=True,
    install_requires=['htp-client']
)
