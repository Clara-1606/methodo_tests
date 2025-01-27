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
MAIN_EXE_DIR = "../../Executable/programme/dist/main.exe" 

# Couleurs ANSI
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


# Fonction pour comparer deux fichiers CSV
def compare_csv(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    df1['Niveau'] = df1['Niveau'].apply(lambda x: pd.NA if pd.isna(x) else int(x))
    df1['Niveau'] = df1['Niveau'].astype(pd.Int64Dtype())  # Utiliser un type entier nullable
    
    df2['Niveau'] = df2['Niveau'].apply(lambda x: pd.NA if pd.isna(x) else int(x))
    df2['Niveau'] = df2['Niveau'].astype(pd.Int64Dtype())
    
    if df1.equals(df2):
        return True, None
    else:
        differences = df1.compare(df2, align_axis=0, keep_shape=True, keep_equal=True)
        
        return False, differences 


# Fonction pour exécuter un test spécifique
def run_test(test_name, timestamp_dir):

    input_dir = os.path.abspath(TEST_INPUT_DIR)

    input_file = os.path.join(input_dir, f"{test_name}.csv")

    excepted_dir = os.path.abspath(TEST_EXPECTED_DIR)
    expected_file = os.path.join(excepted_dir, f'expected_{test_name}.csv')
           
    # Créer le répertoire RESULT_DIR/timestamp_dir s'il n'existe pas
    result_dir = os.path.abspath(RESULT_DIR)
    os.makedirs(os.path.join(result_dir, timestamp_dir, test_name), exist_ok=True)

    main_exe_path = os.path.abspath(MAIN_EXE_DIR)

    # Construction de la commande à exécuter
    command = [
        main_exe_path,
        input_file,
        os.path.join(result_dir, timestamp_dir,test_name)
    ]

    
    # Exécuter la commande
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Vérifier le statut de l'exécution
    if process.returncode == 0:
        result_file = os.path.join(RESULT_DIR, timestamp_dir, test_name, f'result_test.csv')
        if(not os.path.exists(result_file)):
            print(f"Erreur: Le fichier '{result_file}' n'existe pas.")
            print(f" L'exécution du test {test_name} a été spécifiée une erreur :")
            print(stdout.decode())
            sys.exit(1)
        print()
        print()
        print(f" Exécution du test {test_name} en cours...")
        print()
        
        # Comparaison des résultats obtenus aux résultats attendus
        success, differences = compare_csv(expected_file,result_file)
        if success:
            result = f"{GREEN}Test {test_name} réussi !{RESET}"
            print(result)
            print()
            print(" --> Ficher de sortie :",result_file)
            return True, stdout.decode(), stderr.decode(), None
        else:
            result = f"{RED}Test {test_name} échoué !{RESET}"
            print(result)
            print()
            print(" --> Ficher de sortie :",result_file)
            print(differences)
  
            return False , stdout.decode(), stderr.decode(), differences
        
        
    else:
        print(f"Erreur lors de l'exécution du test {test_name}:")
        print(stderr.decode())

        return False, stdout.decode(), stderr.decode(), None


# Fonction principale pour exécuter tous les tests
def run_all_tests(timestamp_dir, test_name):    
    total_tests = 0
    tests_ok = 0
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    test_results = []
    
    out_dir = os.path.abspath(timestamp_dir)
    
    
    if test_name is not None:
        file_output= os.path.join(out_dir,test_name, f'result_test.csv')
        total_tests += 1
        result, stdout, stderr, differences = run_test(test_name, timestamp_dir)
        if result :
            tests_ok += 1
        test_results.append((test_name, result, stdout, stderr, differences, file_output))

    else : 
        # Liste des noms de fichiers CSV sans extension
        tests = [os.path.splitext(f)[0] for f in os.listdir(TEST_INPUT_DIR) if f.endswith('.csv')]

        for test in tests:
            file_output= os.path.join(out_dir,test, f'result_test.csv')
            total_tests += 1
            result, stdout, stderr,differences = run_test(test, timestamp_dir)
            if result :
                tests_ok += 1
            test_results.append((test, result, stdout, stderr, differences, file_output))
                
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
        <br/>
    """
    # Utilisation d'un compteur pour alterner les classes CSS
    row_number = 0
    for test_name, result, stdout, stderr, differences, file_output in test_results:
        row_number += 1
        if not result:
            if differences is None:
                html_template += f"""
                        <li>
                            <h3 class="failure">Test {test_name} : Échoué</h3>
                            <pre>{stderr}</pre>
                            <br/><br/>
                            <strong> Logs :</strong>
                            <pre>{stdout}</pre>
                        </li>
                    """
            else:
                html_template += f"""
                    <li>
                        <h3 class="failure">Test {test_name} : Échoué</h3>
                        <pre>{stderr}</pre>
                        <strong> Différences :</strong>
                        <br/><br/>
                        {format_dataframe_diff_html(differences)}
                        <br/><br/>
                        <strong> Logs :</strong>
                        <pre>{stdout}</pre>
                    </li>
                """
        else:
            html_template += f"""
                <li>
                    <h3 class="success"> Test {test_name} : Réussi !</h3>
                    <pre> Resultats sauvegardés dans {file_output}</pre>
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
    html = differences.to_html(classes='diff-table', escape=False)
        # Ajout de la classe 'diff' aux cellules contenant des différences
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')
        
        # Remplacer 'self' par 'Obtenu' dans le th
    for th in soup.find_all('th'):
        if th.text == 'self':
            th.string = 'Attendu'
        elif th.text == 'other':
            th.string = 'Obtenu'
            
        # Supprimer l'attribut 'valign'
        if 'valign' in th.attrs:
            del th.attrs['valign']

        # Iterate over rows in pairs
    for i in range(1, len(rows), 2):
        self_row = rows[i].find_all('td')
        other_row = rows[i + 1].find_all('td')

        for j in range(len(self_row)):
            if self_row[j].text != other_row[j].text:
                self_row[j]['class'] = self_row[j].get('class', []) + ['self']
                other_row[j]['class'] = other_row[j].get('class', []) + ['diff']
            else :
                other_row[j]['class'] = other_row[j].get('class', []) + ['equal']
        
        # Insert an empty row after the pair of rows
        empty_row = soup.new_tag('tr')
        empty_td = soup.new_tag('td', colspan=len(self_row) + 1)
        empty_row.append(empty_td)
        rows[i + 1].insert_after(empty_row)

    # Output modified HTML
    modified_html = str(soup)
    return modified_html



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
            
    print(f'==> Rapport complet sauvegardé dans {result_dir}')
    print()