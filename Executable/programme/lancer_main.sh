#!/bin/bash

# Obtenir le chemin absolu du répertoire où se trouve le script shell
script_dir=$(dirname "$(readlink -f "$0")")
MAIN_EXE="./dist/main.exe"

while true; do
    # Demander à l'utilisateur le nom du fichier d'entrée
    echo "Entrez le nom du fichier d'entrée : "
    read fichier_entree
	
	if [[ -z "$fichier_entree" ]]; then
		echo ""
        echo "Erreur : Vous devez fournir un nom de fichier. "
		
    else
        # Construire le chemin absolu du fichier d'entrée
        chemin_fichier="$script_dir/$fichier_entree"

        # Vérifier si le fichier existe
        if [ -f "$chemin_fichier" ]; then
			echo ""
			echo "--> Le fichier d'entrée '$chemin_fichier' est trouvé !"
            break  # Sortir de la boucle si le fichier existe
        else
			echo ""
            echo "Erreur : Le fichier '$fichier_entree' n'existe pas dans le répertoire du script."
        fi
    fi
done



# Demander à l'utilisateur le dossier de sortie
echo ""
echo "Entrez le chemin pour trouvez vos résultats :"
read dossier_sortie

if [[ -z "$dossier_sortie" ]]; then
	echo ""
	echo "--> Création d'un dossier par défault 'resultats'..."
	echo ""
	"$MAIN_EXE" "$chemin_fichier"
	echo ""
elif [ -f "$dossier_sortie" ]; then
	echo ""
	echo "--> Le dossier de sortie '$dossier_sortie' n'existe pas. Création du dossier..."
	echo ""
	"$MAIN_EXE" "$chemin_fichier" "$dossier_sortie"
	echo ""
else
	echo ""
	echo "--> Le dossier de sortie '$dossier_sortie' validé !"
	echo ""
	"$MAIN_EXE" "$chemin_fichier" "$dossier_sortie"
	echo ""
fi



read -p "Appuyez sur Entrée pour fermer cette fenêtre..."