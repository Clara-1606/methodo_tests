# Bancs de tests automatiques

import os
import subprocess
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
        differences = df1.compare(df2, keep_equal=True)

        # Transformer les colonnes MultiIndex en une liste de chaînes de caractères appropriées
        differences.columns = [f"{col[0]} ({'Attendu' if col[1] == 'self' else 'Obtenu'})" for col in differences.columns]
        
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
    if success_rate == 100 :
        color = GREEN
    else:
        color = RED
        
    if tests_ok >= 1 :
        color = GREEN
    else:
        color = RED
        
    if test_echoue == 0 :
        color = GREEN
    else:
        color = RED
            
    # Affichage du résumé des tests 
    resume1 = f"\nRésumé des tests :"
    resume2 = f"Nombre total de tests : {total_tests}{RESET}"
    resume3 = f"Tests réussis :{color} {tests_ok} {RESET}"
    resume4 = f"Tests échoués : {color} {test_echoue}{RESET}"
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
            .expected {{ background-color: lightgreen; }}
            .obtained {{ background-color: lightcoral; }}
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
    for test_name, result, stdout, stderr,differences in test_results:
        if not result :
            html_template += f"""
               <li class="failure">
                    Test {test_name} : Échoué
                    <pre>{stderr}</pre>
                    <strong>Différences :</strong>
                    <br/>
                    {differences.to_html(classes='diff-table', index=False).replace('class="Attendu"', 'class="expected"').replace('class="Obtenu"', 'class="obtained"') if differences is not None else ""}
                </li>
            """
        else : 
             html_template += f"""
                <li class="success">
                    Test {test_name} : Réussi !'
                    <pre> {stdout}</pre>
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