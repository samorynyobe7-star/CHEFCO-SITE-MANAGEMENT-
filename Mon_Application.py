import sqlite3
import pandas as pd
import streamlit as st
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
    "Mreur / Economiste de la Construction",
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
    "Pisteuret / Terrassier",
    "Électricien BTP",
    "Plombier / Tuyauteur",
    "Sondeur / Forreur",
    "Soudure / Chaudronnier",
    "Pintre / Applicateur de Revêtement",
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
# 5. INITIALISATION DB & MIGRATION AUTOMATIQUE
# ---------------------------------------------------------
def get_connection():
    return sqlite3.connect("chantier_wouri.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table des Utilisateurs du système
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
    
    # Table des Chantiers
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
    
    # Tables du système
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            poste TEXT NOT NULL,
            salaire_mensuel REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_engin TEXT NOT NULL,
            immatriculation TEXT UNIQUE NOT NULL,
            cout_carburant REAL DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            designation TEXT NOT NULL,
            quantite REAL NOT NULL,
            seuil_alerte REAL NOT NULL,
            cout_unitaire REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id INTEGER,
            date_presence DATE,
            statut TEXT,
            FOREIGN KEY(employe_id) REFERENCES employes(id)
        )
    """)
    conn.commit()

    # Migration chantier_id
    for table in ["employes", "engins", "stocks"]:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        if "chantier_id" not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN chantier_id INTEGER REFERENCES chantiers(id)")
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
                <p style="font-size: 16px; opacity: 0.9;">Plateforme complète de gestion, suivi de projets BTP, ressources et budget.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 1.4, 1])

    with col_c:
        tab_login, tab_signup = st.tabs(["🔑 Se Connecter", "📝 Créer un Compte"])
        
        # --- ONGLET 1 : CONNEXION ---
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
                            st.error("Identifiants incorrects ou compte inexistant. Veuillez créer un compte.")
                    else:
                        st.warning("Veuillez remplir tous les champs.")

        # --- ONGLET 2 : CRÉATION DE COMPTE ---
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
                        # Vérification d'existence
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
                            st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter dans l'onglet 'Se Connecter'.")

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
    
    # Sélection du chantier actif
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
        "📦 Stocks & Matériaux"
    ])

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # 1. GESTION DES CHANTIERS
    if navigation == "🏗️ Gestion des Chantiers":
        st.header("🏗️ Création et Fiche d'Information du Chantier")
        
        with st.form("form_chantier", clear_on_submit=True):
            st.subheader("➕ Ajouter un nouveau projet / chantier")
            col1, col2 = st.columns(2)
            
            nom_c = col1.text_input("Nom du Chantier (ex: Remblai Fleuve Wouri)")
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

    # 2. TABLEAU DE BORD
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
        else:
            st.warning("Veuillez d'abord sélectionner ou créer un chantier dans 'Gestion des Chantiers'.")

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
        else:
            st.warning("Veuillez d'abord sélectionner ou créer un chantier.")

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
        else:
            st.warning("Veuillez d'abord sélectionner ou créer un chantier.")

    st.markdown('</div>', unsafe_allow_html=True)
    conn.close()