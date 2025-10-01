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
   Id_ref = set(df_ref_filtre['Identifiant'].dropna().unique())
   df_back["Nom utilisateur"] = df_back["Nom utilisateur"].str.strip().str.upper()
   df_equipe["LISTE DES UTILISATEURS"] = df_equipe["LISTE DES UTILISATEURS"].str.strip().str.upper()
   equipe = df_equipe[df_equipe.iloc[:, 1] == 1]["LISTE DES UTILISATEURS"].tolist()
   df_back_filtre = df_back[df_back["Nom utilisateur"].isin(equipe)]
   resultats = []
   for utilisateur in df_back_filtre["Nom utilisateur"].unique():
       sous_df = df_back_filtre[df_back_filtre["Nom utilisateur"] == utilisateur]
       id_utilisateur_brut = set(sous_df['Identifiant'].dropna().unique())
       id_utilisateur = id_utilisateur_brut & Id_ref
       manquants = Id_ref - id_utilisateur
       present = Id_ref & id_utilisateur
       resultats.append({
           "utilisateur": utilisateur,
           "nb_identifiants_attendus": len(Id_ref),
           "nb_identifiants_present": len(present),
           "nb_identifiants_manquants": len(manquants),
           "identifiants_manquants": ",".join(sorted(manquants))
       })
   df_resultat_global = pd.DataFrame(resultats)
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
   return df_resultat_global, df_resultat_detaille
# streamlit
def main ():
    st.set_page_config(page_title = "Verification des identifiants", layout="wide")
    load_css()

    st.title("Application interne - Verification des identifiants")
    st.markdown("Bienvenue dans l'outil de **Controle des identifiants** par utilisateur.")

    st.subheader("1. Importer vos fichiers")

    col1, col2, col3 = st.columns(3)

    with col1 :
        fichier_ref = st.file_uploader("Identifiant de reference", type =["xlsx"])
    with col2 :
        fichier_back = st.file_uploader("Identifiant Present", type = ["xlsx"])
    with col3 :
        fichier_equipe = st.file_uploader("liste des utilisateurs avec flags", type = ["xlsx"])

    if fichier_ref and fichier_back and fichier_equipe :
        try :
            df_ref = pd.read_excel(fichier_ref)
            df_back = pd.read_excel(fichier_back)
            df_equipe = pd.read_excel(fichier_equipe)

            st.success("Fichiers chargés avec succès.")
            st.subheader("2. Resultats")

            df_global, df_detail = traitement (df_ref, df_back, df_equipe)

            st.write("### Resume par utilisateur")
            st.dataframe(df_global)

            st.write("### Detail des identifiants manquants")
            st.dataframe(df_detail)

            #telechargement du fichier excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine = "openpyxl") as writer:
                df_global.to_excel(writer, index = False, sheet_name = 'global')
                df_detail.to_excel(writer, index = False, sheet_name = 'detail')
            output.seek(0)

            st.download_button(
                label = " Telecharger les resultats(Xlsx)", 
                data = output,
                file_name = "Resultats_identifiants.Xlsx", 
                mime = " application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        except Exception as e :
            st.error(f"Erreur pendant le traitement : {e}")

if __name__ == "__main__":
    main()