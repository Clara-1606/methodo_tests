# Méthodologies de tests et tests unitaires : Méthode Guillarme --> La gestion des séries 

## Table des matières

1. [Avant de commencer](#avant-de-commencer)
2. [Contexte](#contexte)
3. [Introduction](#introduction)
4. [Technologies utilisées](#technologies-utilisées) 
5. [Règles Métiers Algorithme](#règles-métiers-algorithme)
6. [Contraintes](#contraintes)
7. [Lancer le projet](#lancer-le-projet)  
8. [Documentations](#documentations)
9. [Résultats](#résultats)
10. [Contact](#contact)  


## Avant de commencer
Ce projet contient un banc de tests automatisé pour vérifier le bon fonctionnement d'un script Python qui traite des fichiers CSV. 
Il inclue également banc de test automatisé en bash, et toute une documentation sur les tests et le V&V



### Prérequis

Pour plus de simplicité, vous pouvez utiliser uniquement un terminal si vous pouvez lancer des programmes en bash (`.sh`)
Ou si vous êtes à l'aise en Python, un environnement de dev


### Structure des répertoires

- `Dev/` --> Contient tout le code, dont le script Python principal (`main.py`)
	- `Dev/banc_de_tests/` --> Contient les fichiers CSV de test et les fichiers CSV des résultats attendus, ainsi que le script pour lancer les tests (`run_tests.py`)
- `/Executable` --> Contient tout le nécessaire pour lancer le programme et/ou exécuter les tests sans environnement ou manipulations au préalable grâce à des Script Bash
		- `Executable/programme/` --> Pour lancer le programme sans installation `/programme`, 
			- `Executable\programme\resultats` --> Contiendra les résultats générés après l'exécution du programme par défaut.
		- `Executable/banc_de_tests/`--> Pour lancer le bancs de tests automatisés `/banc_de_tests`
			- `Executable\banc_de_tests\results` --> Contiendra les résultats générés après l'exécution des tests.
- `Doc/` --> Toute la documentation des tests (Voir [Documentations](#documentations))	
- `README.md` : Ce fichier 


### Installation 

1. Avant tout, cloner le projet ;) 
```sh
git clone https://github.com/Clara-1606/methodo_tests.git
```

2. Si vous voulez pas vous embêter et juste tester le programme et/ou lancer le banc de tests automatisés aller [Ici](#lancer-le-projet)

3. Si vous êtes encore là c'est que vous voulez jouer avec le python et/ou modifier un peu le code, bref vous êtes un dev :P (Si Monsieur Bourdillon est encore là, je vous invite à aller aussi directement [Ici](#lancer-le-projet) pour avoir le système «ready to run») 

4. Télécharger Python évidement :
	- Téléchargez et installez Python 3.10.14 à partir du site officiel selon votre système d'exploitation : 
		- Windows : https://www.python.org/downloads/windows/
		- MacOs : https://www.python.org/downloads/macos/
		- Linux/Unix : https://www.python.org/downloads/source/
	- Suivez les instructions d'installation pour votre système d'exploitation
		- ATTENTION, pour Windows, il faut que Python soit ajouté à voir `path` : https://datatofish.com/add-python-to-windows-path/

5. Ouvrez le projet `/Dev` dans votre IDE préféré (Bon pas Notepad, il faut au moins un terminal inclus ^^)
6. On va tester que python fonctionne : 
	- Si besoin : 
		```sh
		python -m pip install --upgrade pip
		```
	Puis si tout va bien, installer les dépendances :
	- Gérer les DataFrames : 
		```sh
		pip install pandas
		```
	- Pouvoir créer un exécutable portable :
		```sh
		pip install pyinstaller
		```
	- Pouvoir extraire les données HTML (sert pour le compte rendu de tests)
		```sh
		pip install beautifulsoup4
		```
7. Lancer les fichiers : 
	- Pour l'algorithme, se mettre à la racine de `/Dev` : 
		- Obligatoire : 
			- `fichier.csv` : Fichier d'entrée CSV qui respectent les [contraintes](#contraintes)
		- Optionnel : 
			- `sortie` : Dossier pour récupérer le résultat
				- S'il n'existe pas --> Il le créer
				- Si rien est mis --> Créer un défault "Resultats" à la racine `/Dev`
				```sh
				python main.py chemin\vers\fichier\fichier.csv <chemin\vers\repertoire\sortie>
				```
	- Pour l'algorithme, se mettre dans /Dev/banc_de_tests : 
		- Optionnel : 
			- `test-name` : Nom du test à lancer individuellement 
				- Si rien est mis --> Lance tous les tests existants
				```sh
				python run_tests.py <test-name>
				```
		
8. Pour les petits rigolos qui veulent modifier le code, et relancer les tests, il faudra d'abord recrée l'exécutable `main.exe` : 
	- Naviguer à la racine de `/Dev` :
		```sh
		pyinstaller --onefile --distpath "../Executable/programme/dist" main.py
		```
9. Et voilà c'est bon !! Maintenant que vous êtes des pros, vous pouvez voir directement [Ici](#lancer-le-projet) pour manipuler les scripts sh sans installation / Python



## Contexte

L'objectif est de l’algorithme suivant une spécification [suivante](#règles-métiers-algorithme) , puis de :
- Définir un plan de test exhaustif
- Définir les cas tests
- Développer un banc de test automatisé en bash
- Valider l’absence de bug de cet algorithme



## Introduction

La Méthode Guillarme est une rééducation basée sur le souffle permettant de retrouver un abdomen et un diaphragme compétents au service de votre périnée, de votre posture, de votre système digestif, de votre esthétique.
L'objectif est d'entraîner le ventre à orienter les pressions vers le haut lors des efforts quotidiens.
Pour fidéliser l’utilisateur, un système de suivi est mis en place pour incrémenter sa série de jour d’affilé pratiqué, ainsi qu’une gestion de vie pour compenser l’absence de pratique. 


## Technologies utilisées
- Python 3.10
	- Dépendances : 
		-	Pandas
		-	Pyinstaller
		-	BeautifulSoup


## Règles Métiers Algorithme

- Un exercice avoir une durée de 5 min (niveau=1) ou de 10 min (niveau=2), et se faire soit assis ou allongé
- Un utilisateur doit effectuer 2 exercices de 5 min ou 1 exercice de 10 min pour compléter une séance.
- Une pratique est un couple séance assis et séance allongé le même jour.
- Chaque jour d’affilé pratiqué incrémente la série de +1.
- L’utilisateur dispose de 2 vies pour pallier l’absence de pratique sur un jour
- Chaque jour sans pratique consomme 1 vie.

- Lorsque l’utilisateur a consommé plus de vie qu’il n’en avait :
	- La série est « cassée » et reprend de 0
	- 2 vies sont recréditées

	

## Contraintes 

Développer un banc de test automatisé en bash «ready to run» incluant les cas test


Les données d’entrée de l’algorithme sont au format csv suivant :

| | | | | | |
|-|-|-|-|-|-|
|Date|Niveau|Allonge|Assis|SessionID|formattedDate|
|1618937885|2|FALSE|TRUE|ed73e2a7|20/04/2021|
|1618937885|2|TRUE|TRUE|ed73e2a7|20/04/2021|

Les données de sortie de l’algorithme sont au format csv suivant :

| | | | | | | |
|-|-|-|-|-|-|-|
|Date|Niveau|Allonge|Assis|SessionID|formattedDate|Serie|
|1618937885|2|FALSE|TRUE|ed73e2a7|20/04/2021|0|
|1618937885|2|TRUE|TRUE|ed73e2a7|20/04/2021|1|

- Date : Timestamps --> Date avec l’heure indiquant quand a été réalisé l’exercice
- Niveau : Integer (1 ou 2) ou vide --> Valeur de l’exercice réalisé de 5 min (niveau=1) ou de 10 min (niveau=2), ou pas de pratique (vide)
- Allonge : Boolean (True/False) --> Si l’exercice a été fait Allongé (True) ou pas (False)
- Assis : Boolean (True/False) --> Si l’exercice a été fait Assis (True) ou pas (False)
- SessionID : String --> Identifiant de l’utilisateur
- formattedDate : Date (JJ/MM/AAAA) --> Date formaté indiquant quand a été réalisé l’exercice
- Serie : Integer >= 0 --> Nombre de jour d’affilé pratiqué



## Lancer le projet

Pas besoin d'IDE, Python ou Cobra, il vous faut simplement naviguer et ouvrir le projet jusqu'au répertoire  `/Executable`

### Windows

#### Programme

En mode vraiment ready to run : Double-cliquez sur `main.sh` pour lancer l'application.
Sinon vous pouvez ouvrir un terminal ou une invite de commande dans `/Executable/Dev` : 
```sh
lancer_main.sh
```

#### Bancs de tests

1. Donnez les permissions d'exécution au script `lancer_main.sh` :
```sh
chmod +x lancer_main.sh
```

2. Exécutez le programme :
```sh
./lancer_main.sh
```

Si problème : Si vous exécutez le script sous un compte utilisateur restreint, essayez de l'exécuter avec des privilèges administratifs. 
- Ouvrez votre terminal en tant qu'administrateur. 



### Unix/Linux/MacOS

#### Programme

1. Ouvrir un terminal ou une invite de commande dans `/Executable/Dev` 

2. Donnez les permissions d'exécution au script `lancer_main.sh` :
```sh
chmod +x lancer_main.sh
```

3. Exécutez le programme :
```sh
./lancer_main.sh
```

#### Bancs de tests

1. Ouvrir un terminal ou une invite de commande dans `/Executable/banc_de_tests` 
2. Donnez les permissions d'exécution au script `lancer_tests.sh` :
    ```sh
    chmod +x lancer_tests.sh
    ```

3. Exécutez les tests :
    ```sh
    ./lancer_tests.sh
    ```
	
Si problème : Si vous exécutez le script sous un compte utilisateur restreint, essayez de l'exécuter avec des privilèges administratifs. 
- Utilisez sudo pour exécuter le script en tant que superutilisateur.

	
	
## Résultats

- L'exécution des tests sera accompagnée d'une sortie en couleur :
	- Vert pour indiquer que tous les tests sont passés.
	- Rouge pour indiquer que certains tests ont échoué.
- Les détails sur les tests échoués seront affichés dans la console
- Un recapitulatif des résultats des tests sera également affichés en console
- Dans \banc_de_tests\results vous trouverez : 
	- Les fichiers csv resultats de chaque tests
	- Un rapport complet en HTML reprenant la console (en plus clair) et de magnifiques tableaux de comparaison pour les tests échoués !


## Documentations

Toute la documentation est disponible dans le git : `/Doc`
- La stratégie de tests / Plan de Tests 
- Les fiches de tests / Plan de Mise en Œuvre des Tests
- CRT
- Quelques exemples de comptes rendus de tests générés après les avoir lancer automatiquement



## Contact 

Clara Vesval M2 Développement Logiciel, Mobile et IOT Ynov Aix (https://clara-1606.github.io/) [![LinkedIn][linkedin-shield]][linkedin-url-clara].  

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url-clara]: https://www.linkedin.com/in/clara-vesval-84b911193/
