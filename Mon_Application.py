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
# 4. CSS DESIGN CORRIGÉ & LISIBLE
# ---------------------------------------------------------
def inject_custom_css():
    st.markdown(
        f"""
        <style>
        header {{visibility: hidden;}}
        .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 3rem !important;
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
            border-bottom: 4px solid #f39c12;
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
        .auth-card {{
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            margin-top: 20px;
        }}
        .app-header-bar {{
            background-color: #0b5fa5;
            color: white;
            padding: 15px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 4px solid #f39c12;
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
            poste TEXT NOT NULL
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
        CREATE TABLE IF NOT EXISTS presences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id INTEGER,
            date_presence DATE,
            statut TEXT,
            FOREIGN KEY(employe_id) REFERENCES employes(id)
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
# 7. PAGE DE CONNEXION LISIBLE ET PROPRE
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
                <p style="font-size: 16px; opacity: 0.9;">Plateforme professionnelle de suivi de projets BTP, ressources, laboratoire et budget.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_l, col_c, col_r = st.columns([1, 1.4, 1])

    with col_c:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #0f172a; margin-bottom: 20px;'>🔑 Accès à votre espace</h3>", unsafe_allow_html=True)
        with st.form("form_connexion_simple"):
            nom_input = st.text_input("Nom de famille :").strip()
            prenom_input = st.text_input("Prénom :").strip()
            poste_input = st.selectbox("Votre poste dans le génie civil / BTP :", POSTES_BTP)
            
            btn_entrer = st.form_submit_button("Accéder au Chantier", use_container_width=True)
            
            if btn_entrer:
                if nom_input and prenom_input:
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute("""
                            SELECT id FROM utilisateurs 
                            WHERE LOWER(nom) = LOWER(?) AND LOWER(prenom) = LOWER(?)
                        """, (nom_input, prenom_input))
                        user_exist = cursor.fetchone()
                        
                        if not user_exist:
                            cursor.execute("""
                                INSERT INTO utilisateurs (nom, prenom, poste)
                                VALUES (?, ?, ?)
                            """, (nom_input, prenom_input, poste_input))
                        else:
                            cursor.execute("""
                                UPDATE utilisateurs SET poste = ? 
                                WHERE LOWER(nom) = LOWER(?) AND LOWER(prenom) = LOWER(?)
                            """, (poste_input, nom_input, prenom_input))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        # Gestion de rattrapage en cas de conflit d'intégrité
                        cursor.execute("""
                            UPDATE utilisateurs SET poste = ? 
                            WHERE LOWER(nom) = LOWER(?) AND LOWER(prenom) = LOWER(?)
                        """, (poste_input, nom_input, prenom_input))
                        conn.commit()
                    finally:
                        conn.close()
                    
                    st.session_state.authenticated = True
                    st.session_state.username = f"{prenom_input} {nom_input}"
                    st.session_state.user_role = poste_input
                    st.success(f"Bienvenue, {st.session_state.username} !")
                    st.rerun()
                else:
                    st.warning("Veuillez renseigner votre nom et votre prénom.")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. APPLICATION PRINCIPALE CONNECTÉE
# ---------------------------------------------------------
else:
    conn = get_connection()
    
    logo_html = f'<img src="data:image/jpeg;base64,{logo_base64}" class="btp-logo-img" style="height:35px;" alt="Logo">' if logo_base64 else '<span class="btp-header-title">CHEFCO</span>'
    
    st.markdown(
        f"""
        <div class="app-header-bar">
            <div style="display:flex; align-items:center; gap:12px;">
                {logo_html}
                <span style="font-size:18px; font-weight:700;">CHEFCO CONSTRUCTION - SUIVI DE CHANTIER</span>
            </div>
            <div style="color:white; font-weight:500;">👤 {st.session_state.username} | 💼 {st.session_state.user_role}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    col_ch, col_btn = st.columns([4, 1])
    
    df_chantiers = pd.read_sql_query("SELECT id, nom_chantier FROM chantiers", conn)
    
    if not df_chantiers.empty:
        chantier_list = df_chantiers["nom_chantier"].tolist()
        chantier_selected_name = col_ch.selectbox("🏗️ **Sélectionner un Chantier actif :**", chantier_list)
        chantier_id = int(df_chantiers[df_chantiers["nom_chantier"] == chantier_selected_name]["id"].values[0])
    else:
        chantier_selected_name = "Aucun chantier enregistré"
        chantier_id = None
        col_ch.warning("⚠️ Aucun chantier créé. Veuillez en créer un dans l'onglet 'Gestion des Chantiers'.")

    if col_btn.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    navigation = st.radio(
        "📂 **Navigation de l'application :**",
        [
            "📊 Tableau de Bord", 
            "🏗️ Gestion des Chantiers", 
            "👷 Employés & Présences", 
            "🚜 Engins & Carburant", 
            "📦 Stocks & Matériaux",
            "🧪 Labo & Contrôle Qualité",
            "📝 Journal de Chantier (Météo)"
        ],
        horizontal=True
    )

    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #cbd5e1;'>", unsafe_allow_html=True)

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
        st.subheader("📋 Liste des Chantiers Enregistrés & Répartition")
        df_all_chantiers = pd.read_sql_query("""
            SELECT id AS ID, nom_chantier AS 'Nom du Chantier', localisation AS 'Localisation', 
                   maitre_ouvrage AS 'Client', budget AS 'Budget (FCFA)', 
                   date_debut AS 'Début', date_fin AS 'Fin', statut AS 'Statut' 
            FROM chantiers
        """, conn)
        st.dataframe(df_all_chantiers, use_container_width=True)

        if not df_all_chantiers.empty:
            st.markdown("### 📈 Diagramme Fonctionnel : Budgets par Chantier")
            chart_data = df_all_chantiers.set_index('Nom du Chantier')['Budget (FCFA)']
            st.bar_chart(chart_data)

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

            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.subheader("🔵 Répartition Circulaire des Dépenses")
                df_depenses = pd.DataFrame({
                    "Catégorie": ["Salaires", "Carburant Engins", "Matériaux Stock"],
                    "Montant (FCFA)": [total_salaires, total_carburant, total_materiaux]
                })
                st.bar_chart(df_depenses.set_index("Catégorie"))

            with col_chart2:
                st.subheader("📈 Courbe Récapitulative du Suivi Financier")
                df_suivi = pd.DataFrame({
                    "Indicateur": ["Budget Total", "Dépenses Globales", "Solde Restant"],
                    "Montant": [budget_total, cout_global, solde_restant]
                })
                st.line_chart(df_suivi.set_index("Indicateur"))

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
                df_postes = df_emp.groupby("Poste")["Salaire (FCFA)"].sum()
                st.bar_chart(df_postes)
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

            if not df_eng.empty:
                st.markdown("### 📊 Répartition du Coût Carburant par Engin")
                st.bar_chart(df_eng.set_index("Engin")["Carburant (FCFA)"])
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

            if not df_st.empty:
                st.markdown("### 📊 Répartition des Quantités par Matériau")
                st.bar_chart(df_st.set_index("Matériau")["Quantité"])
        else:
            st.warning("Veuillez d'abord sélectionner ou créer un chantier.")

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
                st.markdown("### 📊 Évolution des Résistances (7j vs 28j)")
                st.line_chart(df_labo.set_index("Élément")[["R 7j (MPa)", "R 28j (MPa)"]])
        else:
            st.warning("Veuillez sélectionner un chantier.")

    # 7. JOURNAL DE CHANTIER & MÉTÉO
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
                st.markdown("### 📊 Hauteur de Pluie Cumulée par Date")
                st.bar_chart(df_jour.set_index("Date")["Pluie (mm)"])
        else:
            st.warning("Veuillez sélectionner un chantier.")

    st.markdown('</div>', unsafe_allow_html=True)
    conn.close()
