import sqlite3
import pandas as pd
import streamlit as st
import altair as alt
import base64
import os

# ---------------------------------------------------------
# 1. CONFIGURATION PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="CHEFCO - Gestion de Chantier", layout="wide")

# ---------------------------------------------------------
# 2. LISTE DES POSTES BTP EXHAUSTIVE
# ---------------------------------------------------------
POSTES_BTP = [
    # Encadrement & Direction
    "Directeur de Travaux",
    "Chef de Projet BTP",
    "Conducteur de Travaux",
    "Ingénieur Génie Civil",
    "Ingénieur Structure",
    "Ingénieur Géotechnicien",
    "Ingénieur Méthodes / OPC",
    "Chef de Chantier",
    "Chef d'Équipe",
    
    # Études & Métré
    "Métreur / Économiste de la Construction",
    "Projeteur / Dessinateur BTP",
    "BIM Manager / Coordinateur BIM",
    
    # Hygiène, Sécurité & Gestion
    "Responsable HSE / Sécurité Chantier",
    "Gestionnaire de Stock / Magasinier",
    "Chef Mécano / Responsable Matériel",
    "Acheteur BTP / Sourcing",
    
    # Topographie & Laboratoire
    "Topographe / Géomètre",
    "Laborantin BTP / Contrôle Qualité",
    
    # Corps d'État & Ouvriers Spécialisés
    "Chef Maçon / Maçon",
    "Coffreur / Bancheur",
    "Ferrailleur",
    "Pisteur / Terrassier",
    "Électricien BTP",
    "Plombier / Tuyauteur",
    "Sondeur / Forreur",
    "Soudure / Chaudronnier",
    "Peintre / Applicateur de Revêtement",
    "Échafaudeur",
    
    # Engins & Logistique
    "Conducteur d'Engins (Pelle, Bulldozer, Grue...)",
    "Chauffeur Toupie / Dumper / Camion",
    "Mécanicien d'Engins BTP",
    "Manœuvre / Ouvrier Polyvalent"
]

# ---------------------------------------------------------
# 3. LOGO CHEFCO & ENCODAGE BASE64
# ---------------------------------------------------------
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

LOGO_PATH = "IMG-20261008-WA7100.jpg"
logo_base64 = get_base64_of_bin_file(LOGO_PATH)

# ---------------------------------------------------------
# 4. CSS PERSONNALISÉ
# ---------------------------------------------------------
def inject_custom_css():
    st.markdown(
        f"""
        <style>
        header {{visibility: hidden;}}
        .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }}
        .btp-header {{
            background-color: #0b5fa5;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px 40px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
        }}
        .btp-logo-img {{
            height: 50px;
            background-color: #ffffff;
            padding: 5px 12px;
            border-radius: 6px;
        }}
        .btp-header-title {{
            color: #ffffff;
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        .hero-section {{
            background: linear-gradient(135deg, #0b5fa5 0%, #1e3c72 100%);
            padding: 40px 40px;
            color: white;
            border-bottom: 4px solid #f39c12;
        }}
        .hero-title {{
            font-size: 36px;
            font-weight: 800;
            color: #ffffff;
        }}
        .hero-subtitle {{
            font-size: 16px;
            color: #f39c12;
            font-weight: 600;
        }}
        .main-content {{
            padding: 20px 40px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

inject_custom_css()

# ---------------------------------------------------------
# 5. INITIALISATION DB
# ---------------------------------------------------------
def get_connection():
    return sqlite3.connect("chantier_wouri.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            sexe TEXT NOT NULL,
            age INTEGER NOT NULL,
            poste TEXT NOT NULL,
            mot_de_passe TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chantiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_chantier TEXT NOT NULL,
            localisation TEXT,
            maitre_ouvrage TEXT,
            budget REAL DEFAULT 0,
            date_debut DATE,
            date_fin DATE,
            statut TEXT DEFAULT 'En Cours'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chantier_id INTEGER,
            nom TEXT NOT NULL,
            poste TEXT NOT NULL,
            salaire_mensuel REAL NOT NULL,
            FOREIGN KEY(chantier_id) REFERENCES chantiers(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chantier_id INTEGER,
            nom_engin TEXT NOT NULL,
            immatriculation TEXT UNIQUE NOT NULL,
            cout_carburant REAL DEFAULT 0,
            FOREIGN KEY(chantier_id) REFERENCES chantiers(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chantier_id INTEGER,
            designation TEXT NOT NULL,
            quantite REAL NOT NULL,
            seuil_alerte REAL NOT NULL,
            cout_unitaire REAL NOT NULL,
            FOREIGN KEY(chantier_id) REFERENCES chantiers(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_chantier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chantier_id INTEGER,
            date_jour DATE,
            meteo TEXT,
            hauteur_pluie_mm REAL DEFAULT 0,
            incidents TEXT,
            travaux_realises TEXT,
            FOREIGN KEY(chantier_id) REFERENCES chantiers(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS labo_beton (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chantier_id INTEGER,
            date_essai DATE,
            element_coule TEXT,
            slump_test_mm REAL,
            resistance_7j REAL,
            resistance_28j REAL,
            statut TEXT,
            FOREIGN KEY(chantier_id) REFERENCES chantiers(id)
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# 6. GESTION DES SESSIONS
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# ---------------------------------------------------------
# 7. AUTHENTIFICATION & CREATION DE COMPTE
# ---------------------------------------------------------
if not st.session_state.authenticated:
    logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" class="btp-logo-img">' if logo_base64 else '<span class="btp-header-title">CHEFCO</span>'
    
    st.markdown(
        f"""
        <div class="btp-header">
            <div>{logo_html}</div>
            <div class="btp-header-title">CHEFCO CONSTRUCTION</div>
            <div style="color:white; font-weight:500;">ESPACE DE GESTION DE CHANTIER</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-section">
            <div style="max-width: 1200px; margin: 0 auto;">
                <div class="hero-subtitle">CHEFCO - CONSTRUCTION SITE MANAGEMENT</div>
                <div class="hero-title">Du cœur à l'ouvrage</div>
                <p style="font-size: 16px; opacity: 0.9;">Plateforme complète de gestion, suivi de projets BTP, ressources, laboratoire et budget.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 1.4, 1])

    with col_c:
        tab_login, tab_signup = st.tabs(["🔑 Se Connecter", "📝 Créer un Compte"])
        
        with tab_login:
            st.subheader("Connexion à votre espace")
            with st.form("form_login"):
                nom_login = st.text_input("Nom de famille :").strip()
                prenom_login = st.text_input("Prénom :").strip()
                pass_login = st.text_input("Mot de passe :", type="password")
                
                btn_login = st.form_submit_button("Se Connecter", use_container_width=True)
                
                if btn_login:
                    if nom_login and prenom_login and pass_login:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT nom, prenom, poste FROM utilisateurs 
                            WHERE LOWER(nom) = LOWER(?) AND LOWER(prenom) = LOWER(?) AND mot_de_passe = ?
                        """, (nom_login, prenom_login, pass_login))
                        user = cursor.fetchone()
                        conn.close()
                        
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.username = f"{user[1]} {user[0]}"
                            st.session_state.user_role = user[2]
                            st.success(f"Bienvenue {st.session_state.username}")
                            st.rerun()
                        else:
                            st.error("Identifiants incorrects ou compte inexistant.")
                    else:
                        st.warning("Veuillez remplir tous les champs.")

        with tab_signup:
            st.subheader("Créer un nouveau compte")
            with st.form("form_signup", clear_on_submit=True):
                col1, col2 = st.columns(2)
                nom_new = col1.text_input("Nom :").strip()
                prenom_new = col2.text_input("Prénom :").strip()
                
                col3, col4 = st.columns(2)
                sexe_new = col3.selectbox("Sexe :", ["Masculin", "Féminin"])
                age_new = col4.number_input("Âge :", min_value=18, max_value=80, value=25)
                
                poste_new = st.selectbox("Poste / Fonction sur le chantier :", POSTES_BTP)
                pass_new = st.text_input("Créer un Mot de passe :", type="password")
                pass_confirm = st.text_input("Confirmer le Mot de passe :", type="password")
                
                btn_signup = st.form_submit_button("Créer mon compte", use_container_width=True)
                
                if btn_signup:
                    if not nom_new or not prenom_new or not pass_new:
                        st.error("Veuillez remplir tous les champs obligatoires.")
                    elif pass_new != pass_confirm:
                        st.error("Les mots de passe ne correspondent pas.")
                    else:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM utilisateurs WHERE LOWER(nom) = LOWER(?) AND LOWER(prenom) = LOWER(?)", (nom_new, prenom_new))
                        if cursor.fetchone():
                            st.error("Un utilisateur avec ce Nom et Prénom existe déjà.")
                            conn.close()
                        else:
                            cursor.execute("""
                                INSERT INTO utilisateurs (nom, prenom, sexe, age, poste, mot_de_passe)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (nom_new, prenom_new, sexe_new, age_new, poste_new, pass_new))
                            conn.commit()
                            conn.close()
                            st.success("Compte créé avec succès ! Connectez-vous.")

# ---------------------------------------------------------
# 8. APPLICATION PRINCIPALE CONNECTÉE
# ---------------------------------------------------------
else:
    conn = get_connection()
    
    st.sidebar.markdown(f"👤 **Utilisateur :** {st.session_state.username}")
    st.sidebar.markdown(f"💼 **Poste :** {st.session_state.user_role}")
    if st.sidebar.button("Déconnexion"):
        st.session_state.authenticated = False
        st.rerun()
        
    st.sidebar.markdown("---")
    
    df_chantiers = pd.read_sql_query("SELECT id, nom_chantier FROM chantiers", conn)
    
    if not df_chantiers.empty:
        chantier_selected_name = st.sidebar.selectbox("🏗️ **Sélectionner un Chantier :**", df_chantiers["nom_chantier"].tolist())
        chantier_id = int(df_chantiers[df_chantiers["nom_chantier"] == chantier_selected_name]["id"].values[0])
    else:
        chantier_selected_name = "Aucun chantier enregistré"
        chantier_id = None
        st.sidebar.warning("⚠️ Aucun chantier créé.")

    st.sidebar.markdown("---")

    navigation = st.sidebar.radio("Navigation", [
        "📊 Tableau de Bord", 
        "🏗️ Gestion des Chantiers", 
        "👷 Employés & Présences", 
        "🚜 Engins & Carburant", 
        "📦 Stocks & Matériaux",
        "🧪 Labo & Contrôle Qualité",
        "📝 Journal de Chantier (Météo)"
    ])

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # 1. GESTION DES CHANTIERS
    if navigation == "🏗️ Gestion des Chantiers":
        st.header("🏗️ Création et Fiche d'Information du Chantier")
        
        with st.form("form_chantier", clear_on_submit=True):
            st.subheader("➕ Ajouter un nouveau projet / chantier")
            col1, col2 = st.columns(2)
            
            nom_c = col1.text_input("Nom du Chantier (ex: Aménagement Digue Wouri)")
            loc_c = col2.text_input("Localisation / Ville")
            maitre_c = col1.text_input("Maître d'Ouvrage / Client")
            budget_c = col2.number_input("Budget Total Alloué (FCFA)", min_value=0.0, step=100000.0)
            
            col_d1, col_d2, col_d3 = st.columns(3)
            d_debut = col_d1.date_input("Date de début")
            d_fin = col_d2.date_input("Date prévisionnelle de fin")
            statut_c = col_d3.selectbox("Statut", ["En Cours", "En Attente", "Terminé"])
            
            btn_creer = st.form_submit_button("Créer le Chantier")
            
            if btn_creer and nom_c:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chantiers (nom_chantier, localisation, maitre_ouvrage, budget, date_debut, date_fin, statut)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nom_c, loc_c, maitre_c, budget_c, str(d_debut), str(d_fin), statut_c))
                conn.commit()
                st.success(f"Chantier '{nom_c}' enregistré avec succès !")
                st.rerun()

        st.markdown("---")
        st.subheader("📋 Liste des Chantiers Enregistrés")
        df_all_chantiers = pd.read_sql_query("""
            SELECT id AS ID, nom_chantier AS 'Nom du Chantier', localisation AS 'Localisation', 
                   maitre_ouvrage AS 'Client', budget AS 'Budget (FCFA)', 
                   date_debut AS 'Début', date_fin AS 'Fin', statut AS 'Statut' 
            FROM chantiers
        """, conn)
        st.dataframe(df_all_chantiers, use_container_width=True)
        
        # Diagramme de répartition des budgets par chantier
        if not df_all_chantiers.empty:
            st.markdown("### 📊 Analyse des Budgets par Chantier")
            chart_chantiers = alt.Chart(df_all_chantiers).mark_bar(color="#0b5fa5").encode(
                x=alt.X('Nom du Chantier:N', sort='-y'),
                y=alt.Y('Budget (FCFA):Q', title='Budget (FCFA)'),
                tooltip=['Nom du Chantier', 'Budget (FCFA)', 'Statut']
            ).properties(height=300)
            st.altair_chart(chart_chantiers, use_container_width=True)

    # 2. TABLEAU DE BORD (Avec Diagramme Circulaire et Courbe)
    elif navigation == "📊 Tableau de Bord":
        st.header(f"📊 Tableau de Bord - {chantier_selected_name}")
        
        if chantier_id:
            info_c = pd.read_sql_query("SELECT * FROM chantiers WHERE id = ?", conn, params=(chantier_id,))
            if not info_c.empty:
                c_data = info_c.iloc[0]
                st.info(f"📍 **Localisation :** {c_data['localisation']} | 👤 **Client :** {c_data['maitre_ouvrage']} | 📅 **Période :** du {c_data['date_debut']} au {c_data['date_fin']}")
            
            df_emp = pd.read_sql_query("SELECT * FROM employes WHERE chantier_id = ?", conn, params=(chantier_id,))
            df_eng = pd.read_sql_query("SELECT * FROM engins WHERE chantier_id = ?", conn, params=(chantier_id,))
            df_stock = pd.read_sql_query("SELECT * FROM stocks WHERE chantier_id = ?", conn, params=(chantier_id,))
            
            total_salaires = df_emp["salaire_mensuel"].sum() if not df_emp.empty else 0.0
            total_carburant = df_eng["cout_carburant"].sum() if not df_eng.empty else 0.0
            total_materiaux = (df_stock["quantite"] * df_stock["cout_unitaire"]).sum() if not df_stock.empty else 0.0
            cout_global = total_salaires + total_carburant + total_materiaux
            
            budget_total = c_data['budget'] if not info_c.empty else 0.0
            solde_restant = budget_total - cout_global

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Budget Alloué", f"{budget_total:,.0f} FCFA")
            col2.metric("📉 Dépenses Totales", f"{cout_global:,.0f} FCFA")
            col3.metric("💵 Solde Budget", f"{solde_restant:,.0f} FCFA", delta_color="normal" if solde_restant >= 0 else "inverse")
            col4.metric("👷 Effectif Actif", f"{len(df_emp)} Employés")

            st.markdown("---")
            
            # --- DIAGRAMMES DU TABLEAU DE BORD ---
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("🍩 Répartition Circulaire des Dépenses")
                df_depenses = pd.DataFrame({
                    'Catégorie': ['Salaires Personnel', 'Carburant Engins', 'Matériaux Stock'],
                    'Montant': [total_salaires, total_carburant, total_materiaux]
                })
                if df_depenses['Montant'].sum() > 0:
                    # Diagramme circulaire (Donut chart)
                    pie_chart = alt.Chart(df_depenses).mark_arc(innerRadius=60).encode(
                        theta=alt.Theta(field="Montant", type="quantitative"),
                        color=alt.Color(field="Catégorie", type="nominal", scale=alt.Scale(scheme='tableau10')),
                        tooltip=['Catégorie', alt.Tooltip('Montant:Q', format=',.0f')]
                    ).properties(height=300)
                    st.altair_chart(pie_chart, use_container_width=True)
                else:
                    st.info("Aucune dépense enregistrée pour afficher le graphique circulaire.")

            with col_chart2:
                st.subheader("📈 Courbe d'Évolution de la Pluviométrie")
                df_pluie = pd.read_sql_query("SELECT date_jour, hauteur_pluie_mm FROM journal_chantier WHERE chantier_id = ? ORDER BY date_jour", conn, params=(chantier_id,))
                if not df_pluie.empty:
                    # Courbe (Line chart)
                    line_chart = alt.Chart(df_pluie).mark_line(point=True, color="#f39c12").encode(
                        x=alt.X('date_jour:T', title='Date'),
                        y=alt.Y('hauteur_pluie_mm:Q', title='Hauteur Pluie (mm)'),
                        tooltip=['date_jour', 'hauteur_pluie_mm']
                    ).properties(height=300)
                    st.altair_chart(line_chart, use_container_width=True)
                else:
                    st.info("Aucune donnée météo enregistrée pour tracer la courbe.")
        else:
            st.warning("Veuillez créer un chantier dans le menu 'Gestion des Chantiers'.")

    # 3. EMPLOYÉS
    elif navigation == "👷 Employés & Présences":
        st.header(f"👷 Personnel du Chantier : {chantier_selected_name}")
        
        if chantier_id:
            with st.form("form_emp", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                nom_e = col1.text_input("Nom & Prénom")
                poste_e = col2.selectbox("Poste", POSTES_BTP)
                salaire_e = col3.number_input("Salaire Mensuel (FCFA)", min_value=0.0, step=5000.0)
                
                if st.form_submit_button("Ajouter à ce chantier") and nom_e:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO employes (chantier_id, nom, poste, salaire_mensuel) VALUES (?, ?, ?, ?)",
                                   (chantier_id, nom_e, poste_e, salaire_e))
                    conn.commit()
                    st.success(f"{nom_e} ajouté au chantier !")
                    st.rerun()

            df_emp = pd.read_sql_query("SELECT id AS ID, nom AS Nom, poste AS Poste, salaire_mensuel AS 'Salaire (FCFA)' FROM employes WHERE chantier_id = ?", conn, params=(chantier_id,))
            st.dataframe(df_emp, use_container_width=True)

            if not df_emp.empty:
                st.markdown("### 📊 Répartition des Salaires par Poste")
                chart_emp = alt.Chart(df_emp).mark_bar(color="#1e3c72").encode(
    x=alt.X('Poste:N', sort='-y'),
    y=alt.Y('sum(Salaire (FCFA)):Q', title='Total Salaire (FCFA)'),
    tooltip=['Poste', alt.Tooltip('sum(Salaire (FCFA)):Q', format=',.0f')]
).properties(height=280)
                st.altair_chart(chart_emp, use_container_width=True)
        else:
            st.warning("Veuillez sélectionner un chantier.")

    # 4. ENGINS
    elif navigation == "🚜 Engins & Carburant":
        st.header(f"🚜 Engins Affectés au Chantier : {chantier_selected_name}")
        
        if chantier_id:
            with st.form("form_engin", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                nom_eng = col1.text_input("Nom / Type d'Engin (ex: Bulldozer CAT)")
                immat = col2.text_input("Immatriculation / Code")
                carburant = col3.number_input("Coût Carburant (FCFA)", min_value=0.0, step=2000.0)
                
                if st.form_submit_button("Enregistrer Engin") and nom_eng:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO engins (chantier_id, nom_engin, immatriculation, cout_carburant)
                        VALUES (?, ?, ?, ?)
                    """, (chantier_id, nom_eng, immat, carburant))
                    conn.commit()
                    st.success("Engin enregistré !")
                    st.rerun()

            df_eng = pd.read_sql_query("SELECT id AS ID, nom_engin AS Engin, immatriculation AS Immat, cout_carburant AS 'Carburant (FCFA)' FROM engins WHERE chantier_id = ?", conn, params=(chantier_id,))
            st.dataframe(df_eng, use_container_width=True)

            if not df_eng.empty:
                st.markdown("### 📊 Coût du Carburant par Engin")
                chart_eng = alt.Chart(df_eng).mark_bar(color="#e67e22").encode(
                    x=alt.X('Engin:N', sort='-y'),
                    y=alt.Y('Carburant (FCFA):Q'),
                    tooltip=['Engin', 'Immat', alt.Tooltip('Carburant (FCFA):Q', format=',.0f')]
                ).properties(height=280)
                st.altair_chart(chart_eng, use_container_width=True)
        else:
            st.warning("Veuillez sélectionner un chantier.")

    # 5. STOCKS
    elif navigation == "📦 Stocks & Matériaux":
        st.header(f"📦 Stocks du Chantier : {chantier_selected_name}")
        
        if chantier_id:
            with st.form("form_stock", clear_on_submit=True):
                col1, col2, col3, col4 = st.columns(4)
                mat = col1.text_input("Désignation Matériau (ex: Ciment CPJ 42.5)")
                qte = col2.number_input("Quantité", min_value=0.0)
                seuil = col3.number_input("Seuil Alerte", min_value=0.0)
                pu = col4.number_input("Prix Unitaire (FCFA)", min_value=0.0)
                
                if st.form_submit_button("Ajouter en Stock") and mat:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO stocks (chantier_id, designation, quantite, seuil_alerte, cout_unitaire) VALUES (?, ?, ?, ?, ?)",
                                   (chantier_id, mat, qte, seuil, pu))
                    conn.commit()
                    st.success(f"Article {mat} ajouté !")
                    st.rerun()

            df_st = pd.read_sql_query("SELECT id AS ID, designation AS Matériau, quantite AS Quantité, seuil_alerte AS 'Seuil Alerte', cout_unitaire AS 'PU (FCFA)' FROM stocks WHERE chantier_id = ?", conn, params=(chantier_id,))
            st.dataframe(df_st, use_container_width=True)

            if not df_st.empty:
                st.markdown("### 📊 Niveaux des Stocks Actuels")
                chart_st = alt.Chart(df_st).mark_bar(color="#27ae60").encode(
                    x=alt.X('Matériau:N', sort='-y'),
                    y=alt.Y('Quantité:Q'),
                    tooltip=['Matériau', 'Quantité', 'Seuil Alerte']
                ).properties(height=280)
                st.altair_chart(chart_st, use_container_width=True)
        else:
            st.warning("Veuillez sélectionner un chantier.")

    # 6. LABO & CONTRÔLE QUALITÉ
    elif navigation == "🧪 Labo & Contrôle Qualité":
        st.header(f"🧪 Suivi Laboratoire & Béton : {chantier_selected_name}")
        
        if chantier_id:
            with st.form("form_labo", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                date_e = col1.date_input("Date de l'essai / coulage")
                element = col2.text_input("Élément concerné (ex: Radier Semelle S1)")
                slump = col3.number_input("Affaissement Cône d'Abrams (Slump en mm)", min_value=0.0, value=120.0)
                
                col4, col5, col6 = st.columns(3)
                res_7 = col4.number_input("Résist. 7j (MPa)", min_value=0.0, value=0.0)
                res_28 = col5.number_input("Résist. 28j (MPa)", min_value=0.0, value=0.0)
                statut_qualite = col6.selectbox("Validation", ["Conforme", "Non Conforme", "En attente 28j"])
                
                if st.form_submit_button("Enregistrer les données labo"):
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO labo_beton (chantier_id, date_essai, element_coule, slump_test_mm, resistance_7j, resistance_28j, statut)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (chantier_id, str(date_e), element, slump, res_7, res_28, statut_qualite))
                    conn.commit()
                    st.success("Résultat de laboratoire enregistré !")
                    st.rerun()

            df_labo = pd.read_sql_query("""
                SELECT id AS ID, date_essai AS Date, element_coule AS Élément, 
                       slump_test_mm AS 'Slump (mm)', resistance_7j AS 'R 7j (MPa)', 
                       resistance_28j AS 'R 28j (MPa)', statut AS Statut 
                FROM labo_beton WHERE chantier_id = ?
            """, conn, params=(chantier_id,))
            st.dataframe(df_labo, use_container_width=True)

            if not df_labo.empty:
                st.markdown("### 📊 Évolution des Résistances du Béton (MPa)")
                df_melted = df_labo.melt(id_vars=['Élément'], value_vars=['R 7j (MPa)', 'R 28j (MPa)'], var_name='Échéance', value_name='Résistance (MPa)')
                chart_labo = alt.Chart(df_melted).mark_bar().encode(
                    x=alt.X('Élément:N'),
                    y=alt.Y('Résistance (MPa):Q'),
                    color='Échéance:N',
                    tooltip=['Élément', 'Échéance', 'Résistance (MPa)']
                ).properties(height=280)
                st.altair_chart(chart_labo, use_container_width=True)
        else:
            st.warning("Veuillez sélectionner un chantier.")

    # 7. JOURNAL DE CHANTIER (MÉTÉO)
    elif navigation == "📝 Journal de Chantier (Météo)":
        st.header(f"📝 Journal Quotidien & Météo : {chantier_selected_name}")
        
        if chantier_id:
            with st.form("form_journal", clear_on_submit=True):
                col1, col2 = st.columns(2)
                date_j = col1.date_input("Date du rapport journalier")
                meteo = col2.selectbox("Conditions Météo", ["Ensoleillé", "Nuageux", "Pluvieux", "Orageux"])
                
                pluie = st.number_input("Hauteur de pluie estimée (mm)", min_value=0.0, step=1.0)
                travaux = st.text_area("Travaux réalisés dans la journée")
                incidents = st.text_area("Incidents ou arrêts de chantier notables")
                
                if st.form_submit_button("Valider le rapport journalier"):
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO journal_chantier (chantier_id, date_jour, meteo, hauteur_pluie_mm, incidents, travaux_realises)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (chantier_id, str(date_j), meteo, pluie, incidents, travaux))
                    conn.commit()
                    st.success("Rapport journalier enregistré avec succès !")
                    st.rerun()

            df_jour = pd.read_sql_query("""
                SELECT date_jour AS Date, meteo AS Météo, hauteur_pluie_mm AS 'Pluie (mm)', 
                       travaux_realises AS 'Travaux Réalisés', incidents AS Incidents 
                FROM journal_chantier WHERE chantier_id = ?
            """, conn, params=(chantier_id,))
            st.dataframe(df_jour, use_container_width=True)

            if not df_jour.empty:
                st.markdown("### 📊 Historique de la Pluviométrie Journalière")
                chart_meteo = alt.Chart(df_jour).mark_line(point=True, color="#2980b9").encode(
                    x=alt.X('Date:T'),
                    y=alt.Y('Pluie (mm):Q'),
                    tooltip=['Date', 'Météo', 'Pluie (mm)']
                ).properties(height=280)
                st.altair_chart(chart_meteo, use_container_width=True)
        else:
            st.warning("Veuillez sélectionner un chantier.")

    st.markdown('</div>', unsafe_allow_html=True)
    conn.close()
