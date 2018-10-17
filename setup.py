# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="Openfisca-Paris",
    version="2.2.0",
    description="Plugin OpenFisca pour les aides sociales de la mairie de Paris",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    author="Mairie de Paris, Incubateur de Services Numériques (SGMAP)",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'OpenFisca-Core >= 24, < 25',
        'OpenFisca-France >= 25, < 27'
    ],
    extras_require = {
        'test': 'nose'
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
