# Bancs de tests automatiques

import os
import subprocess
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import sys
from datetime import datetime

TEST_INPUT_DIR = "./tests/in"
TEST_EXPECTED_DIR = "./tests/out"
RESULT_DIR = "./results"
MAIN_EXE_DIR = "../dist/main.exe" 

# Couleurs ANSI
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


# Fonction pour comparer deux fichiers CSV
def compare_csv(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    if df1.equals(df2):
        return True, None
    else:
        differences = df1.compare(df2, align_axis=0, keep_shape=True, keep_equal=True)
        
        return False, differences 


# Fonction pour exécuter un test spécifique
def run_test(test_name, timestamp_dir):
    input_file = os.path.join(TEST_INPUT_DIR, f"{test_name}.csv")
    expected_file = os.path.join(TEST_EXPECTED_DIR, f'expected_{test_name}.csv')
    
    # Créer le répertoire RESULT_DIR/timestamp_dir s'il n'existe pas
    os.makedirs(os.path.join(RESULT_DIR, timestamp_dir, test_name), exist_ok=True)
    
    # Chemin absolu vers l'exécutable main.exe
    main_exe = os.path.abspath(os.path.join(os.path.dirname(__file__), MAIN_EXE_DIR))
    
    # Construction de la commande à exécuter
    command = [
        main_exe,
        input_file,
        os.path.join(RESULT_DIR, timestamp_dir,test_name)
    ]
    
    # Exécuter la commande
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    # Vérifier le statut de l'exécution
    if process.returncode == 0:

        result_file = os.path.join(RESULT_DIR, timestamp_dir, test_name, f'result_test.csv')
        
        print()
        print()
        print(f"- Exécution du test {test_name} en cours...")
        print()
        

        # Comparaison des résultats obtenus aux résultats attendus
        
        success, differences = compare_csv(result_file, expected_file)
        if success:
            result = f"{GREEN}Test {test_name} réussi !{RESET}"
            print(result)
            print()
            print("--> Ficher de sortie :",result_file)
            return True, stdout.decode(), stderr.decode(), None
        else:
            result = f"{RED}Test {test_name} échoué !{RESET}"
            print(result)
            print()
            print("--> Ficher de sortie :",result_file)
  
            return False , stdout.decode(), stderr.decode(), differences
        
        
    else:
        print(f"Erreur lors de l'exécution du test {test_name}:")
        print(stderr.decode())

        return False, stdout.decode(), stderr.decode()


# Fonction principale pour exécuter tous les tests
def run_all_tests(timestamp_dir, test_name):    
    total_tests = 0
    tests_ok = 0
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    test_results = []
    
    if test_name is not None:
        total_tests += 1
        result, stdout, stderr, differences = run_test(test, timestamp_dir)
        if result :
            tests_ok += 1
        test_results.append((test, result, stdout, stderr, differences))

    else : 
        # Liste des noms de fichiers CSV sans extension
        tests = [os.path.splitext(f)[0] for f in os.listdir(TEST_INPUT_DIR) if f.endswith('.csv')]

        for test in tests:
            total_tests += 1
            result, stdout, stderr,differences = run_test(test, timestamp_dir)
            if result :
                tests_ok += 1
            test_results.append((test, result, stdout, stderr, differences))
                
    # Calcul du pourcentage de réussite
    success_rate = tests_ok / total_tests * 100
    test_echoue = total_tests - tests_ok
    
    # Détermination de la couleur en fonction du pourcentage de réussite      
    if tests_ok >= 1 :
        color = GREEN
    else:
        color = RED
  
            
    # Affichage du résumé des tests 
    resume1 = f"\nRésumé des tests :"
    resume2 = f"Nombre total de tests : {total_tests}{RESET}"   
    resume3 = f"Tests réussis :{color} {tests_ok} {RESET}"
    
    if test_echoue == 0 :
        color = GREEN
    else:
        color = RED
    
    resume4 = f"Tests échoués : {color} {test_echoue}{RESET}"
    
    if success_rate == 100 :
        color = GREEN
    else:
        color = RED
    
    resume5 = f"Pourcentage de réussite : {color} {success_rate:.2f}%{RESET}"

    print()
    print(resume1)  
    print(resume2)
    print(resume3)
    print(resume4)
    print(resume5)
    print()
    
    generate_html_report(current_time, timestamp_dir, total_tests, tests_ok, success_rate, test_results)
        

def generate_html_report(timestamp, timestamp_dir, total_tests, tests_ok, success_rate, test_results):
    html_template = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rapport de tests - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            .diff-table {{ border-collapse: collapse; width: 100%; }}
            .diff-table th, .diff-table td {{ border: 1px solid black; padding: 8px; }}
            .diff-table th {{ background-color: #f2f2f2; }}
            .diff-table td {{ text-align: left; }}
            .diff-table th, .diff-table td {{ text-align: center; }}
            .diff {{ background-color: lightcoral; font-weight: bold; }}
            .equal {{ background-color: lightgreen; font-weight: normal; }}
            .self {{ background-color: green; color: white; }}
            td  {{ font-weight: bold; }}
            
        </style>
    </head>
    <body>
        <h1>Rapport de tests généré le {timestamp}</h1>
        <h2>Résumé des tests :</h2>
        <p>Nombre total de tests : {total_tests}</p>
        <p>Tests réussis : <span class="success"> {tests_ok}</span></p>
        <p>Tests échoués : <span class="{ 'success' if total_tests - tests_ok == 0 else 'failure' }">{total_tests - tests_ok}</span></p>
        <p>Pourcentage de réussite : <span class="{ 'success' if success_rate == 100 else 'failure' }">{success_rate:.2f}%</span></p>
        <h2>Détails des tests :</h2>
        <ul>
    """
    # Utilisation d'un compteur pour alterner les classes CSS
    row_number = 0
    for test_name, result, stdout, stderr, differences in test_results:
        row_number += 1
        if not result:
            html_template += f"""
                <li>
                    <h3 class="failure">Test {test_name} : Échoué</h3>
                    <pre>{stderr}</pre>
                    <strong class="failure">Différences :</strong>
                    <br/><br/>
                    {format_dataframe_diff_html(differences)}
                </li>
            """
        else:
            html_template += f"""
                <li class="success">
                    Test {test_name} : Réussi !
                    <pre>{stdout}</pre>
                </li>
            """

    html_template += """
            </ul>
        </body>
        </html>
    """
    
    # Écrire le rapport HTML dans un fichier
    with open(os.path.join(RESULT_DIR, timestamp_dir, f'rapport_complet.html'), 'w') as f:
        f.write(html_template)
        

def format_dataframe_diff_html(differences):
    if isinstance(differences, pd.DataFrame):
        html = '<table class="diff-table">\n'
        html += '<thead>\n<tr>'
        
        # Ajouter les en-têtes de colonne
        for column in differences.columns.get_level_values(0).unique():
            html += f'<th>{column}</th>'
        html += '</tr>\n</thead>\n<tbody>\n'
        
       
        # Ajouter les lignes de données
        for index, row in differences.iterrows():
            
            html += '<tr>'
            # Vérifier que ce n'est pas la dernière ligne
            for index in range(len(differences) - 1):  # Parcourir jusqu'à l'avant-dernière ligne
                row_current = differences.iloc[index]
                row_next = differences.iloc[index + 1]
                
                for col_name in differences.columns.get_level_values(0).unique():
                    cell_value_self = row_current[col_name]
                    cell_value_other = row_next[col_name]
                         
                    print(cell_value_self, cell_value_other)
 
                # Comparer les valeurs self et other et appliquer le style en conséquence
                    if pd.isna(cell_value_self) and pd.isna(cell_value_other):
                        html += '<td></td>'
                    elif cell_value_self != cell_value_other:
                        html += f'<td class="diff">{cell_value_other}</td>'
                    else:
                        html += f'<td>{cell_value_self}</td>'
                html += '</tr>\n'
        html += '</tbody>\n</table>'
        return html
    return str(differences)


if __name__ == "__main__": 
    timestamp_dir = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    
    # Créer RESULT_DIR s'il n'existe pas
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    # Créer timestamp_dir à l'intérieur de RESULT_DIR
    os.makedirs(os.path.join(RESULT_DIR, timestamp_dir), exist_ok=True)
    
    result_dir = os.path.join(RESULT_DIR, timestamp_dir, f'rapport_complet.html')

    if len(sys.argv) == 1 :
        run_all_tests(timestamp_dir, None)
    else:
        test_name = sys.argv[1]
        run_all_tests(timestamp_dir,test_name)
            
    print(f'--> Rapport complet sauvegardé dans {result_dir}')
    print()