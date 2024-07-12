#!/bin/bash

# Obtenir le chemin absolu du répertoire où se trouve le script shell
script_dir=$(dirname "$(readlink -f "$0")")

TEST_EXE="./dist/run_tests"

# Fonction pour afficher une animation de chargement
function show_progress() {
    local bar_width=50
    local delay=0.1
    local chars=("▏" "▎" "▍" "▌" "▋" "▊" "▉" "█")
    local idx=0
     # Temps de départ de la boucle
    local start_time=$(date +%s)
    
    while ps -p $test_pid > /dev/null; do
		if ! kill -0 $test_pid 2>/dev/null; then
            break  # Sortir de la boucle si le processus n'est plus actif
        fi
        local current_time=$(date +%s)
        local elapsed_time=$((current_time - start_time))
             
        for ((i = 0; i < bar_width; i++)); do
			if ! kill -0 $test_pid 2>/dev/null; then
				break  # Sortir de la boucle si le processus n'est plus actif
			fi
            local progress=$((idx % ${#chars[@]}))
            printf "\r"
            for ((j = 0; j <= i; j++)); do
				if ! kill -0 $test_pid 2>/dev/null; then
					break  # Sortir de la boucle si le processus n'est plus actif
				fi
                printf "${chars[$progress]}"
            done
            for ((j = i + 1; j < bar_width; j++)); do
				if ! kill -0 $test_pid 2>/dev/null; then
					break  # Sortir de la boucle si le processus n'est plus actif
				fi
                printf " "
            done
			if ! kill -0 $test_pid 2>/dev/null; then
				break  # Sortir de la boucle si le processus n'est plus actif
			fi
            printf ""
            idx=$((idx + 1))
            sleep $delay
        done
    done
	echo ""
    
    printf "\n"
	echo ""
}

while true; do
    # Demander à l'utilisateur le nom du fichier d'entrée
	echo ""
    echo "Quels tests voulez vous lancer ? "
	echo "Appuyez directement sur entrée si vous voulez tous les lancer"
    read test_name
	
	if [[ -z "$test_name" ]]; then
		echo ""
        echo " --> Lancement de TOUS les tests en cours ! Veuillez patienter... "
		echo ""
		
		# Exécuter les tests automatisés avec test_script
		"$TEST_EXE" &
		test_pid=$!

		# Afficher la barre de progression pendant que fichier.exe s'exécute
		show_progress &
        progress_pid=$!
		
		wait $test_pid  # Attendre la fin de run_tests
		
		kill $progress_pid >/dev/null 2>&1
		
		break
		
    else
        # Construire le chemin absolu du fichier d'entrée
        chemin_fichier=$script_dir"/tests/in/"$test_name".csv"

        # Vérifier si le fichier existe
        if [ -f "$chemin_fichier" ]; then
			echo ""
			echo "Le test '$test_name' est trouvé !"
			echo ""
			echo " --> Lancement du test '$test_name' en cours ! Veuillez patienter..."
			echo ""
			
			# Exécuter les tests automatisés avec test_script
			"$TEST_EXE" "$test_name" &
			test_pid=$!

			# Afficher la barre de progression pendant que fichier.exe s'exécute
			show_progress $test_pid &
			progress_pid=$!
			
			wait $test_pid  # Attendre la fin de run_tests
			
			kill $progress_pid >/dev/null 2>&1

            break  # Sortir de la boucle si le fichier existe
        else
			echo ""
            echo "Erreur : Le test '$test_name' n'existe pas."
			echo ""

        fi
    fi
done

echo ""
read -p "Appuyez sur Entrée pour fermer cette fenêtre..."