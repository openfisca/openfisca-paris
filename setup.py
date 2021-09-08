# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="Openfisca-Paris",
    version="2.2.5",
    description="Plugin OpenFisca pour les aides sociales de la mairie de Paris",
    license="http://www.fsf.org/licensing/licenses/agpl-3.0.html",
    author="Mairie de Paris, Incubateur de Services Numériques (SGMAP)",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'OpenFisca-Core >= 35.2.0, < 36',
        'OpenFisca-France >= 61, < 74'
    ],
    extras_require = {
        'test': [
            'nose',
            'pytest >= 5.4.2'
            ]
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
    ]
)
