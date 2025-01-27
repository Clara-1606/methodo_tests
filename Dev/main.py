import argparse
import os
import sys

import pandas as pd

# Fonction de nettoyage pour la colonne 'Assis'
def nettoyer_booloean(valeur):
    if valeur == True or valeur == 'True' or valeur == 'true':
        return True
    else:
        return False

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
    
    # Appliquer la fonction de nettoyage à la colonne 'Assis'
    data['Assis'] = data['Assis'].apply(nettoyer_booloean)
    data['Allonge'] = data['Allonge'].apply(nettoyer_booloean)
    
    data.reset_index(drop=False)

    return data

def calculer_serie(data):
    """Calculer la série pour chaque SessionID selon les règles spécifiées."""
    series_par_session = {}

    for session_id, session_data in data.groupby('SessionID'):
        series = 0
        nb_serie_actuelle = 0
        dernier_date = None
        prochaine_date = None
        nb_vies = 2
        nb_assis = 0
        nb_allonge = 0
        nb_pratiques = 0

        print("session data :")
        print(session_data)
        print("*************************")
        
        for i, (index, row) in enumerate(session_data.iterrows()):
            date_actuelle = row['Date'].date()  
            prochaine_date = session_data.iloc[i+1]['Date'].date() if i < len(session_data)-1 else None
            print("******* index intiale",index, "********")
            print("******* index nouveau",i, "********")
            print()
            print(row)
            print()
            print("vies au départ",nb_vies)
            print()
            print("Date avant :",dernier_date)
            print("date actuelle :",date_actuelle)
            print("Date suivante :",prochaine_date)
            print()
            
            if dernier_date is not None and dernier_date != date_actuelle:          
                nb_assis = 0
                nb_allonge = 0
                nb_pratiques = 0
            
             # Vérifier si c'est une pratique valide (couple assis et allongé le même jour) 
            if (row['Allonge'] and row['Assis']) :
                if (row['Niveau'] == 1):
                    nb_assis +=1
                    nb_allonge +=1
                elif (row['Niveau'] == 2):
                    nb_assis +=2
                    nb_allonge +=2
            elif ((not row['Allonge']) and row['Assis']):
                if (row['Niveau'] == 1):
                    nb_assis  +=1
                elif (row['Niveau'] == 2):
                    nb_assis  +=2
            elif (row['Allonge'] and (not row['Assis'])):
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

            print("pratiques :",nb_pratiques)
        
            print()
                         
            if dernier_date is not None and dernier_date != date_actuelle :
                print()
                print("nouveau jour!")
                print("avant",dernier_date)
                print("Maintenant",date_actuelle)
                print()
                # Vérifier si les conditions de pratique sont remplies pour ce jour
                jour_ecart = abs((date_actuelle - dernier_date).days)
                print("jour d'écart",jour_ecart)

                if nb_vies >= jour_ecart - 1 :
                    if jour_ecart == 1 :
                        if prochaine_date is None or prochaine_date != date_actuelle :
                            if nb_pratiques != 1:
                                nb_vies -= jour_ecart 
                                print()
                                print("vie après sans pratique",nb_vies)  
                            else :
                                series += 1 
                                print("nb serie même jour",series)
                    else :
                        nb_vies -= jour_ecart - 1
                        print()
                        print("vie après jour absence",nb_vies)
                        if nb_pratiques == 1 :
                            series += 1 
                            print("nb serie même jour",series) 
                        elif prochaine_date is None or prochaine_date != date_actuelle:
                            if nb_pratiques != 1 :
                                nb_vies -= 1
                                print()
                                print("vie après sans pratique",nb_vies)

                else : 
                    series = 0
                    nb_vies = 2
                    
            elif (dernier_date is None or dernier_date == date_actuelle) :
                if prochaine_date is not None and prochaine_date != date_actuelle:
                    if nb_pratiques != 1 :
                        nb_vies -= 1
                        print()
                        print("vie après sans pratique",nb_vies) 
                    else :
                        series += 1 
                        print("nb serie même jour",series) 
                else :
                    if nb_pratiques == 1 :
                        series += 1 
                        print("nb serie même jour",series) 
     
            
            if series > 0 and nb_serie_actuelle != series and series % 5 == 0 and nb_vies < 2:
                nb_vies += 1
                print("uOUIII", nb_vies)  
                          
            print()
            print("series",series)
            print("series",nb_serie_actuelle)
            print()
                
            
            nb_serie_actuelle = series          
            dernier_date = date_actuelle 
                
            series_par_session[index] = series  
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

