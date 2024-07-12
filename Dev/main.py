import argparse
import os
import sys
import pandas as pd

def lire_donnees_entree(data):
    #Traiter d'entrée depuis un fichier CSV
    data['Date'] = pd.to_datetime(data['Date'], unit='s')  # Convertir les timestamps en datetime
    data = data.sort_values(by='Date')  # Trier par la colonne 'Date'
    data.reset_index(drop=True, inplace=True)  # Réinitialiser l'index après le tri
    return data

def calculer_serie(data):
    """Calculer la série pour chaque SessionID selon les règles spécifiées."""
    series_par_session = {}

    for session_id, session_data in data.groupby('SessionID'):
        series = 0
        dernier_date = None
        nb_vies = 2
        nb_assis = 0
        nb_allonge = 0
        jours_sans_pratique = 0 
        nb_pratiques = 0
        
        print("session data",session_data)
        print("sessionçid",session_id)
        
        for index, row in session_data.iterrows():
            date_actuelle = row['Date'].date()  
            
            print("index",index)
            print("row",row)
            print("date actu",date_actuelle)
                       
             # Vérifier si c'est une pratique valide (couple assis et allongé le même jour) 
            if (row['Allonge'] and row['Assis']):
                if (row['Niveau'] == 1):
                    nb_assis +=1
                    nb_allonge +=1
                elif (row['Niveau'] == 2):
                    nb_pratiques =+1
            elif not (row['Allonge'] and row['Assis']):
                if (row['Niveau'] == 1):
                    nb_assis  +=1
                elif (row['Niveau'] == 2):
                    nb_assis  +=2
            elif (row['Allonge'] and not row['Assis']):
                if (row['Niveau'] == 1):
                    nb_allonge  +=1
                elif (row['Niveau'] == 2):
                    nb_allonge  +=2
            else:
                jours_sans_pratique +=1

            print(" assis",nb_assis,"allonge",nb_allonge,"pratiques",nb_pratiques)
            if (nb_assis >= 2 and nb_allonge >= 2):
                nb_pratiques  =+1

            print("pratiques",nb_pratiques)
                        
            if dernier_date is not None and (date_actuelle != dernier_date):
                print("nouveau jour!", date_actuelle)
                print("avant",dernier_date)
                # Vérifier si les conditions de pratique sont remplies pour ce jour
                jour_ecart = abs((date_actuelle - dernier_date).days)

                if nb_vies >= jour_ecart :
                    nb_vies -= jour_ecart
                    if (nb_pratiques >=1) :
                        series += 1 
                else : 
                    series = 0
                    nb_vies = 2
                    
                nb_assis = 0
                nb_allonge = 0
                jours_sans_pratique = 0 
                nb_pratiques = 0
            else :      
                if (nb_pratiques >=1) :
                    series += 1      
                           
            dernier_date = date_actuelle 
            
            series_par_session[index] = series
           
    return series_par_session

def generer_sortie(original_data, series_par_session, dossier_sortie):
    timestamp_dir = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    
    # Créer une nouvelle colonne 'Serie' dans les données originales en utilisant les séries calculées
    original_data['Serie'] = original_data.index.map(series_par_session.get)

    # Enregistrer les résultats dans un fichier CSV
    output_csv = os.path.join(dossier_sortie, f'result_test.csv')
    
    # Utiliser le chemin absolu pour éviter les problèmes de chemin relatif
    output_dir = os.path.abspath(output_csv)
    
    if os.path.exists(output_dir):
        print()
        print(f"Attention : Le fichier '{output_dir}' existe déjà. Un nouveau dossier va être crée")
        print()
        # Créer timestamp_dir à l'intérieur de RESULT_DIR
        os.makedirs(os.path.join(dossier_sortie, timestamp_dir), exist_ok=True)
        new_output_dir = os.path.join(dossier_sortie, timestamp_dir, f'result_test.csv')
    
        # Utiliser le chemin absolu pour éviter les problèmes de chemin relatif
        output_dir = os.path.abspath(new_output_dir)
        
 
    original_data.to_csv(output_dir, index=False)
    print(f'Resultats sauvegardés dans {output_dir}')


def main(fichier_entree, dossier_sortie):
    try:    
        if dossier_sortie is None : 
            dossier_sortie = "resultats"
            os.makedirs(dossier_sortie, exist_ok=True)
        else : 
            os.makedirs(dossier_sortie, exist_ok=True)
        
        # Lire les données d'entrée
        data = pd.read_csv(fichier_entree)
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{fichier_entree}' n'est pas trouvé.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier '{fichier_entree}': {e}")
        sys.exit(1)
        
    # Créer une copie des données originales pour conserver l'ordre initial
    original_data = data.copy()
    
    try: 
        #Traiter fichier d'entrée
        donnees = lire_donnees_entree(data)

        # Calculer la série pour chaque SessionID
        series_par_session = calculer_serie(donnees)

        # Générer le fichier de sortie
        generer_sortie(original_data, series_par_session, dossier_sortie)
    except Exception as e:
        print(f"Error processing data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculer la série à partir d\'un fichier CSV.')
    parser.add_argument('fichier_entree', type=str,nargs='?', help='Chemin vers le fichier CSV d\'entrée.')
    parser.add_argument('dossier_sortie', type=str, nargs='?', default=None, help='Répertoire de sortie pour les résultats.')
    
    
    args = parser.parse_args()
    main(args.fichier_entree, args.dossier_sortie)

