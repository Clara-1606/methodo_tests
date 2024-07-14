import argparse
import os
import sys
import pandas as pd

def lire_donnees_entree(data):
    # Valider les données avant la conversion
    if 'Date' not in data.columns:
        raise ValueError("La colonne 'Date' est manquante dans les données.")
    
    if data['Date'].isnull().any():
        raise ValueError("La colonne 'Date' contient des valeurs nulles.")

    # Vérifier si toutes les valeurs de la colonne 'Date' sont des entiers ou peuvent être converties en entiers
    if not data['Date'].apply(lambda x: isinstance(x, (int, float))).all():
        raise ValueError("Les valeurs de la colonne 'Date' doivent être des entiers ou des floats.")

    #Traiter d'entrée depuis un fichier CSV
    data['Date'] = pd.to_datetime(data['Date'], unit='s')  # Convertir les timestamps en datetime
    
    data = data.sort_values(by='Date')  # Trier par la colonne 'Date'

    return data

def calculer_serie(data):
    """Calculer la série pour chaque SessionID selon les règles spécifiées."""
    series_par_session = {}

    for session_id, session_data in data.groupby('SessionID'):
        series = 0
        nb_serie_actuelle = 0
        dernier_date = None
        nb_vies = 2
        nb_assis = 0
        nb_allonge = 0
        nb_pratiques = 0
        dernier_pratique_valide = False
        jours_sans_pratique = 0
        series_journee = {}
        
        print("*************************")
        print("session data :")
        print(session_data)
        print("*************************")
        
        
        for index, row in session_data.iterrows():
            date_actuelle = row['Date'].date()  
            print("*******",index, "********")
            print()
            print(row)
            print()
            print("vies au départ",nb_vies)
            print()
            print("Date avant :",dernier_date)
            print("date actuelle :",date_actuelle)
            print()
            
            # Si on change de date, traiter la journée précédente
            if dernier_date is not None and dernier_date != date_actuelle:
                if not dernier_pratique_valide:
                    jours_sans_pratique = abs((date_actuelle - dernier_date).days)
                    nb_vies -= jours_sans_pratique
                    if nb_vies < 0:
                        series = 0
                        nb_vies = 2
                else:
                    series += 1
                    if series > 0 and series % 5 == 0 and nb_vies < 2:
                        nb_vies += 1
                        print("uOUIII", nb_vies)
                        
                series_journee = series + 1 if dernier_pratique_valide else series
                    
                # Réinitialiser les compteurs pour la nouvelle date
                # Réinitialiser pour le nouveau jour
                dernier_date = date_actuelle
                nb_assis = 0
                nb_allonge = 0
                nb_pratiques = 0
                dernier_pratique_valide  = False
                #series_journee = {}
            
            series_par_session[index] = series_journee if dernier_pratique_valide else series
            
             # Vérifier si c'est une pratique valide (couple assis et allongé le même jour) 
            if (row['Allonge'] and row['Assis']):
                if (row['Niveau'] == 1):
                    nb_assis +=1
                    nb_allonge +=1
                elif (row['Niveau'] == 2):
                    nb_assis +=2
                    nb_allonge +=2
            elif (not row['Allonge']) and row['Assis']:
                if (row['Niveau'] == 1):
                    nb_assis  +=1
                elif (row['Niveau'] == 2):
                    nb_assis  +=2
            elif row['Allonge'] and (not row['Assis']):
                if (row['Niveau'] == 1):
                    nb_allonge  +=1
                elif (row['Niveau'] == 2):
                    nb_allonge  +=2

            print()
            print("assis :",nb_assis)
            print("allonge :",nb_allonge)
            print()
            if (nb_assis >= 2 and nb_allonge >= 2):
                nb_pratiques  += 1
                dernier_pratique_valide  = True

            print("pratiques :",nb_pratiques)
        
            print()
            
            series_journee = series
        
        for i in series_par_session:
            series_par_session[i] = series_journee
                
    return series_par_session

def generer_sortie(original_data, series_par_session, dossier_sortie):
    timestamp_dir = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    
    # Créer une nouvelle colonne 'Serie' dans les données originales en utilisant les séries calculées
    original_data['Serie'] = original_data.index.map(series_par_session.get)
    
    # Convertir les colonnes en leur type original
    original_data['Serie'] = original_data['Serie'].fillna(0).astype(int)

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
    original_data = pd.read_csv(fichier_entree, dtype={'Niveau': str})  
    
    try: 
        #Traiter fichier d'entrée
        donnees = lire_donnees_entree(data)

        # Calculer la série pour chaque SessionID
        series_par_session = calculer_serie(donnees)

        # Générer le fichier de sortie
        generer_sortie(original_data, series_par_session, dossier_sortie)
    except ValueError as e:
        print(f"Erreur de conversion : {e}")
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")
        sys.exit(1)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculer la série à partir d\'un fichier CSV.')
    parser.add_argument('fichier_entree', type=str,nargs='?', help='Chemin vers le fichier CSV d\'entrée.')
    parser.add_argument('dossier_sortie', type=str, nargs='?', default=None, help='Répertoire de sortie pour les résultats.')
    
    
    args = parser.parse_args()
    main(args.fichier_entree, args.dossier_sortie)

