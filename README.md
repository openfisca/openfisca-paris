# OpenFisca-Paris

## Introduction

[OpenFisca](https://fr.openfisca.org/) est un logiciel libre de micro-simulation. Ce dépôt contient la modélisation des aides spécifiques à la ville de Paris (France). Pour plus d'information sur les fonctionnalités et la manière d'utiliser OpenFisca, vous pouvez consulter la [documentation générale](http://openfisca.org/doc/).

## Installation

Ce paquet requiert [Python 3](https://www.python.org/downloads/) et [pip](https://pip.pypa.io/en/stable/installing/).

```sh
python --version  # Devrait afficher "Python 3.x.x".
```

## Contribuer à OpenFisca-Paris

Suivez cette installation si vous souhaitez :
- enrichir ou modifier la législation d'OpenFisca-Paris ;
- contribuer au code source d'OpenFisca-Paris.

### Installer 

Premièrement, assurez-vous que [Git](https://www.git-scm.com/) est bien installé chez vous.

Puis, dans le répertoire de votre machine où vous souhaitez voir OpenFisca-Paris clonez le contenu du dépôt GitHub :

```sh
git clone git@github.com:betagouv/openfisca-paris.git
```

Enfin, allez dans le répertoire `openfisca-paris` et installez OpenFisca-Paris et ses dépendances avec :

```sh
cd openfisca-paris
make install
```

Vous pouvez vous assurer que votre installation s'est bien passée en exécutant les tests comme décrit ci-dessous.

### Tester

Les tests d'OpenFisca-Paris sont au format `.yaml`. 
Pour les exécuter, dans votre répertoire `openfisca-paris`, utilisez la commande suivante :

```sh
openfisca test tests/unittests/**/*.yaml --extensions openfisca_paris
```

Les tests se sont déroulés sans erreur si les résultats s'achèvent par `OK` tel que présenté dans cet exemple :

```
........................................................
----------------------------------------------------------------------
Ran 129 tests in 123.608s

OK
```

> Pour en savoir plus sur les tests `.yaml`, une documentation est à votre disposition sur [openfisca.org/doc](http://openfisca.org/doc/coding-the-legislation/writing_yaml_tests.html).

:tada: OpenFisca-Paris est prêt à être utilisé !
