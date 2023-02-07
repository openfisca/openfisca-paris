# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="Openfisca-Paris",
    version="3.6.3",
    author="OpenFisca Team",
    author_email="contact@openfisca.fr",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    description="Plugin OpenFisca pour les aides sociales de la mairie de Paris",
    keywords="benefit france paris microsimulation social tax",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'OpenFisca-Core >= 35.2.0, < 36',
        'OpenFisca-France >= 102, < 143',
    ],
    extras_require={
        'test': [
            'nose',
            'pytest >= 5.4.2'
        ]
    },
)
