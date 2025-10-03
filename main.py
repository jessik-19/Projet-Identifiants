import streamlit as st
import pandas as pd
import os
from io import BytesIO
# CSS personnalisé
def load_css():
   with open("style.css") as f:
       st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# Traitement principal
def traitement(df_ref, df_back, df_equipe):

    # Nettoyage

    df_ref_filtre = df_ref[df_ref["Date de fin"].isna()]

    # Extraire les 3 colonnes de référence : Identifiant (colonne A), JUR (colonne B), SOUS JUR (colonne D)

    liste_identifiants = df_ref_filtre["Identifiant"].dropna().astype(str).unique()

    liste_jur = df_ref_filtre.iloc[:, 1].dropna().astype(str).unique()         # Colonne B

    liste_sousjur = df_ref_filtre.iloc[:, 3].dropna().astype(str).unique()    # Colonne D

    # Union des 3 ensembles

    Id_ref = set(liste_identifiants) | set(liste_jur) | set(liste_sousjur)

    # Nettoyage des noms utilisateurs

    df_back["Nom utilisateur"] = df_back["Nom utilisateur"].str.strip().str.upper()

    df_back["Identifiant"] = df_back["Identifiant"].astype(str).str.strip()

    df_equipe["LISTE DES UTILISATEURS "] = df_equipe["LISTE DES UTILISATEURS "].str.strip().str.upper()
    

    # Liste des utilisateurs actifs (flag = 1)

    equipe = df_equipe[df_equipe.iloc[:, 1] == 1]["LISTE DES UTILISATEURS "].tolist()

    # Filtrer df_back uniquement sur les utilisateurs actifs

    df_back_filtre = df_back[df_back["Nom utilisateur"].isin(equipe)]

    # Résultats globaux

    resultats = []

    for utilisateur in df_back_filtre["Nom utilisateur"].unique():

        sous_df = df_back_filtre[df_back_filtre["Nom utilisateur"] == utilisateur]

        id_utilisateur_brut = set(sous_df['Identifiant'].dropna().astype(str).unique())

        id_utilisateur = id_utilisateur_brut & Id_ref

        manquants = Id_ref - id_utilisateur

        presents = Id_ref & id_utilisateur

        resultats.append({

            "utilisateur": utilisateur,

            "nb_identifiants_attendus": len(Id_ref),

            "nb_identifiants_present": len(presents),

            "nb_identifiants_manquants": len(manquants),

            "identifiants_manquants": ", ".join(sorted(manquants))

        })

    df_resultat_global = pd.DataFrame(resultats)

    # Résultats détaillés

    lignes_detaillées = []

    for row in resultats:

        utilisateur = row["utilisateur"]

        identifiants = row["identifiants_manquants"]

        identifiants_list = [i.strip() for i in identifiants.split(",") if i.strip()]

        if identifiants_list:

            for identifiant in identifiants_list:

                lignes_detaillées.append({

                    "utilisateur": utilisateur,

                    "identifiant_manquant": identifiant

                })

        else:

            lignes_detaillées.append({

                "utilisateur": utilisateur,

                "identifiant_manquant": ""

            })

    df_resultat_detaille = pd.DataFrame(lignes_detaillées)

    # Identifiants en trop (non attendus), par utilisateur
    lignes_en_trop = []
    for utilisateur in df_back_filtre["Nom utilisateur"].unique():
       sous_df = df_back_filtre[df_back_filtre["Nom utilisateur"] == utilisateur]
       id_utilisateur_brut = set(sous_df['Identifiant'].dropna().astype(str).unique())
       id_en_trop = id_utilisateur_brut - Id_ref
       for identifiant in id_en_trop:
           lignes_en_trop.append({
               "utilisateur": utilisateur,
               "identifiant_non_attendu": identifiant
           })
    df_resultat_en_trop = pd.DataFrame(lignes_en_trop)

    return df_resultat_global, df_resultat_detaille, df_resultat_en_trop

# streamlit
def main ():
    st.set_page_config(page_title = "Verification des identifiants", layout="wide")
    load_css()

    col1, col2 = st.columns([1, 4])  # Logo à gauche, texte à droite
    with col1:
        st.image("logo_accor.png", width=120)
    with col2:
        st.markdown("""
    <div style='padding-top: 15px;'>
    <h1 style='text-align: center;margin-bottom: 0;'>Application interne - Vérification des identifiants</h1>
    </div>
    """, unsafe_allow_html=True)
    # Texte "Bienvenue" centré
    st.markdown("""
    <div style='text-align: center; margin-top: -10px; font-size: 18px;'>
        Bienvenue dans l'outil de <strong>Contrôle des identifiants</strong> par utilisateur.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)#ajoutez de l'espace 

    st.subheader("1. Importer vos fichiers")

    st.markdown("<br>", unsafe_allow_html=True)#ajoutez de l'espace 

    col1, col2, col3 = st.columns(3)

    with col1 :
        fichier_ref = st.file_uploader("Identifiant de reference", type =["xlsx"])
        st.caption("Fichiers de référence contenant tous les identifiants attendus.")
        st.image("images/exemple_ref.png", use_container_width=True)
    with col2 :
        fichier_back = st.file_uploader("Identifiant Present", type = ["xlsx"])
        st.caption("Fichier contenant les identifiants réellement utilisés.")
        st.image("images/exemple_back.png", use_container_width=True)
    with col3 :
        fichier_equipe = st.file_uploader("liste des utilisateurs avec flags", type = ["xlsx"])
        st.caption("Fichiers avec la liste des utilisateurss avec une colonne de flag.")
        st.image("images/exemple_equipe.png", use_container_width=True)

    if fichier_ref and fichier_back and fichier_equipe :
        try :
            df_ref = pd.read_excel(fichier_ref)
            df_back = pd.read_excel(fichier_back)
            df_equipe = pd.read_excel(fichier_equipe)

            st.success("Fichiers chargés avec succès.")
            st.subheader("2. Resultats")

            df_global, df_detail, df_id_trop = traitement (df_ref, df_back, df_equipe)

            st.write("### Resume par utilisateur")
            st.dataframe(df_global)

            st.write("### Detail des identifiants manquants")
            st.dataframe(df_detail)

            st.write("### Identifiants non attendus")
            st.dataframe(df_id_trop)           

            # 🎯 AJOUT ICI : Tri des DataFrames avant export
            df_global = df_global.sort_values(by=["utilisateur"])
            df_detail = df_detail.sort_values(by=["utilisateur", "identifiant_manquant"])
            df_id_trop = df_id_trop.sort_values(by=["utilisateur", "identifiant_non_attendu"]) 

            #telechargement du fichier excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine = "openpyxl") as writer:
                df_global.to_excel(writer, index=False, sheet_name="Résumé")
                df_detail.to_excel(writer, index=False, sheet_name="Manquants")
                df_id_trop.to_excel(writer, index=False, sheet_name="En trop")
            output.seek(0)

            st.download_button(
                label = " Telecharger les resultats(Xlsx)", 
                data = output,
                file_name = "Resultats_identifiants.Xlsx", 
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        except Exception as e :
            st.error(f"Erreur pendant le traitement : {e}")

if __name__ == "__main__":
    main()