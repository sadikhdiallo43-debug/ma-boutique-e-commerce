from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3
import datetime
import socket
import requests
import os
from threading import Thread
import time
import hashlib

app = Flask(__name__)
app.secret_key = 'devnet_exam_secret_key'

# Configuration de la base de données
DATABASE = '/app/data/chat.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # S'assurer que le répertoire de la base de données existe
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    with app.app_context():
        db = get_db()
        
        # Tables pour le chat (existant)
        db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                container_id TEXT
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                container_id TEXT,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tables pour la boutique
        db.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                description TEXT,
                prix REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                image_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        db.execute('''
            CREATE TABLE IF NOT EXISTS commandes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_nom TEXT NOT NULL,
                client_email TEXT NOT NULL,
                client_telephone TEXT,
                total REAL NOT NULL,
                statut TEXT DEFAULT 'en_attente',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notification_envoyee BOOLEAN DEFAULT FALSE
            )
        ''')
        
        db.execute('''
            CREATE TABLE IF NOT EXISTS commande_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commande_id INTEGER NOT NULL,
                produit_id INTEGER NOT NULL,
                quantite INTEGER NOT NULL,
                prix_unitaire REAL NOT NULL,
                FOREIGN KEY (commande_id) REFERENCES commandes (id),
                FOREIGN KEY (produit_id) REFERENCES produits (id)
            )
        ''')
        
        db.execute('''
            CREATE TABLE IF NOT EXISTS messages_boutique (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_nom TEXT NOT NULL,
                client_email TEXT NOT NULL,
                sujet TEXT NOT NULL,
                message TEXT NOT NULL,
                statut TEXT DEFAULT 'non_lu',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notification_envoyee BOOLEAN DEFAULT FALSE
            )
        ''')
        
        db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        db.commit()
        
        # Ajouter des produits d'exemple si la table est vide
        init_sample_products()
        
        # Créer un admin par défaut si aucun n'existe
        init_default_admin()

def init_sample_products():
    """Ajouter des produits d'exemple pour démonstration"""
    db = get_db()
    count = db.execute('SELECT COUNT(*) as count FROM produits').fetchone()['count']
    
    if count == 0:
        sample_products = [
            {
                'nom': 'Robe Élégante Soie',
                'description': 'Robe longue en soie avec design floral, parfaite pour occasions spéciales',
                'prix': 45000,
                'stock': 12,
                'image_url': 'https://images.unsplash.com/photo-1594633312681-ba9d7b5f5c3f?w=300&h=400&fit=crop'
            },
            {
                'nom': 'Blazer Chic',
                'description': 'Blazer moderne coupe ajustée en laine mélangée, idéal pour le bureau',
                'prix': 65000,
                'stock': 18,
                'image_url': 'https://images.unsplash.com/photo-1554568218-0f1715e72254?w=300&h=400&fit=crop'
            },
            {
                'nom': 'Jean Slim Fit',
                'description': 'Jean slim de haute qualité avec stretch, disponible en plusieurs couleurs',
                'prix': 28000,
                'stock': 35,
                'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=400&fit=crop'
            },
            {
                'nom': 'Chemise en Lin',
                'description': 'Chemise légère en lin parfait pour l\'été, coupe moderne et élégante',
                'prix': 22000,
                'stock': 25,
                'image_url': 'https://images.unsplash.com/photo-1596755094514-f87e5ccf6e6d?w=300&h=400&fit=crop'
            },
            {
                'nom': 'Veste en Cuir',
                'description': 'Veste en cuir véritable style motard, doublure confortable',
                'prix': 85000,
                'stock': 8,
                'image_url': 'https://images.unsplash.com/photo-1551488831-008076e2dcba?w=300&h=400&fit=crop'
            },
            {
                'nom': 'Pull en Cashmere',
                'description': 'Pull luxueux en cachemire, doux et chaud pour l\'hiver',
                'prix': 72000,
                'stock': 15,
                'image_url': 'https://images.unsplash.com/photo-1578922772014-3c5e5a14e4f5?w=300&h=400&fit=crop'
            },
            {
                'nom': 'Jupe Plissée',
                'description': 'Jupe plissée tendance, longueur midi, tissu fluide et élégant',
                'prix': 32000,
                'stock': 20,
                'image_url': 'https://images.unsplash.com/photo-1595775456939-3a8b5b1c3e4e?w=300&h=400&fit=crop'
            },
            {
                'nom': 'Pantalon Chino',
                'description': 'Pantalon chino classique, polyvalent et confortable pour toutes occasions',
                'prix': 35000,
                'stock': 30,
                'image_url': 'https://images.unsplash.com/photo-1594633312681-ba9d7b5f5c3f?w=300&h=400&fit=crop'
            }
        ]
        
        for product in sample_products:
            db.execute('''
                INSERT INTO produits (nom, description, prix, stock, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (product['nom'], product['description'], product['prix'], 
                  product['stock'], product['image_url']))
        
        db.commit()
        print("Produits d'exemple ajoutes avec succes!")

def init_default_admin():
    """Creer un admin par defaut si aucun n'existe"""
    db = get_db()
    count = db.execute('SELECT COUNT(*) as count FROM admins').fetchone()['count']
    
    if count == 0:
        # Mot de passe par defaut: admin123
        default_password = 'admin123'
        password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        
        db.execute('''
            INSERT INTO admins (username, password_hash) VALUES (?, ?)
        ''', ('admin', password_hash))
        
        db.commit()
        print("Admin par defaut cree (username: admin, password: admin123)!")

# Initialiser la base de données au démarrage de l'application
init_db()

def get_container_info():
    """Récupère les informations du conteneur actuel"""
    try:
        hostname = socket.gethostname()
        container_id = os.environ.get('HOSTNAME', hostname)
        return container_id
    except:
        return "unknown"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/boutique')
def boutique():
    return render_template('boutique.html')

@app.route('/admin')
def admin():
    # Vérifier si l'admin est connecté
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Veuillez remplir tous les champs', 'error')
            return render_template('login.html')
        
        db = get_db()
        admin = db.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        
        if admin:
            # Vérifier le mot de passe
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == admin['password_hash']:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                flash('Connexion réussie!', 'success')
                return redirect(url_for('admin'))
        
        flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('admin_login'))

def admin_required(f):
    """Décorateur pour protéger les routes admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            return jsonify({'error': 'Authentification requise'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/chat')
def chat():
    container_id = get_container_info()
    return render_template('chat.html', container_id=container_id)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    db = get_db()
    messages = db.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 50').fetchall()
    return jsonify([dict(msg) for msg in messages])

@app.route('/api/messages', methods=['POST'])
def post_message():
    data = request.get_json()
    username = data.get('username')
    message = data.get('message')
    container_id = get_container_info()
    
    if not username or not message:
        return jsonify({'error': 'Username and message required'}), 400
    
    db = get_db()
    db.execute(
        'INSERT INTO messages (username, message, container_id) VALUES (?, ?, ?)',
        (username, message, container_id)
    )
    db.commit()
    
    return jsonify({'success': True})

@app.route('/api/users', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    container_id = get_container_info()
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (username, container_id) VALUES (?, ?)',
            (username, container_id)
        )
        db.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/api/users', methods=['GET'])
def get_users():
    db = get_db()
    users = db.execute('SELECT * FROM users ORDER BY joined_at DESC').fetchall()
    return jsonify([dict(user) for user in users])

@app.route('/api/network/status')
def network_status():
    """Vérifie le statut du réseau et des autres conteneurs"""
    container_id = get_container_info()
    
    # Simuler la découverte d'autres conteneurs
    other_containers = []
    try:
        # Dans un vrai environnement, ceci scannerait le réseau Docker
        # Pour la démo, nous retournons des informations simulées
        db = get_db()
        users = db.execute('SELECT DISTINCT container_id FROM users WHERE container_id != ? AND container_id IS NOT NULL', 
                          (container_id,)).fetchall()
        other_containers = [user['container_id'] for user in users]
    except:
        pass
    
    return jsonify({
        'current_container': container_id,
        'other_containers': other_containers,
        'network_mode': 'docker_bridge',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/sync', methods=['POST'])
def sync_data():
    """Endpoint pour synchroniser les données entre conteneurs"""
    data = request.get_json()
    source_container = data.get('source_container')
    
    # Dans une implémentation réelle, ceci synchroniserait les bases de données
    # Pour la démo, nous retournons juste un succès
    return jsonify({
        'success': True,
        'synced_at': datetime.datetime.now().isoformat(),
        'message': f'Data synchronized from {source_container}'
    })

# ===== API POUR LA BOUTIQUE =====

@app.route('/api/produits', methods=['GET'])
def get_produits():
    """Récupérer tous les produits"""
    db = get_db()
    produits = db.execute('SELECT * FROM produits ORDER BY created_at DESC').fetchall()
    return jsonify([dict(p) for p in produits])

@app.route('/api/produits', methods=['POST'])
@admin_required
def add_produit():
    """Ajouter un nouveau produit"""
    data = request.get_json()
    nom = data.get('nom')
    description = data.get('description')
    prix = data.get('prix')
    stock = data.get('stock', 0)
    image_url = data.get('image_url')
    
    if not nom or not prix:
        return jsonify({'error': 'Nom et prix requis'}), 400
    
    db = get_db()
    db.execute(
        'INSERT INTO produits (nom, description, prix, stock, image_url) VALUES (?, ?, ?, ?, ?)',
        (nom, description, float(prix), int(stock), image_url)
    )
    db.commit()
    
    return jsonify({'success': True})

@app.route('/api/produits/<int:produit_id>', methods=['PUT'])
@admin_required
def update_produit(produit_id):
    """Mettre à jour un produit"""
    data = request.get_json()
    db = get_db()
    
    # Vérifier si le produit existe
    produit = db.execute('SELECT * FROM produits WHERE id = ?', (produit_id,)).fetchone()
    if not produit:
        return jsonify({'error': 'Produit non trouvé'}), 404
    
    # Mettre à jour les champs
    nom = data.get('nom', produit['nom'])
    description = data.get('description', produit['description'])
    prix = data.get('prix', produit['prix'])
    stock = data.get('stock', produit['stock'])
    image_url = data.get('image_url', produit['image_url'])
    
    db.execute(
        'UPDATE produits SET nom = ?, description = ?, prix = ?, stock = ?, image_url = ? WHERE id = ?',
        (nom, description, float(prix), int(stock), image_url, produit_id)
    )
    db.commit()
    
    return jsonify({'success': True})

@app.route('/api/produits/<int:produit_id>', methods=['DELETE'])
@admin_required
def delete_produit(produit_id):
    """Supprimer un produit"""
    db = get_db()
    
    # Vérifier si le produit existe
    produit = db.execute('SELECT * FROM produits WHERE id = ?', (produit_id,)).fetchone()
    if not produit:
        return jsonify({'error': 'Produit non trouvé'}), 404
    
    # Supprimer le produit
    db.execute('DELETE FROM produits WHERE id = ?', (produit_id,))
    db.commit()
    
    return jsonify({'success': True})

@app.route('/api/commandes', methods=['POST'])
def create_commande():
    """Créer une nouvelle commande"""
    data = request.get_json()
    client_nom = data.get('client_nom')
    client_email = data.get('client_email')
    client_telephone = data.get('client_telephone')
    items = data.get('items', [])
    
    if not client_nom or not client_email or not items:
        return jsonify({'error': 'Informations client et articles requis'}), 400
    
    db = get_db()
    
    # Calculer le total et vérifier le stock
    total = 0
    for item in items:
        produit_id = item.get('produit_id')
        quantite = item.get('quantite', 1)
        
        produit = db.execute('SELECT * FROM produits WHERE id = ?', (produit_id,)).fetchone()
        if not produit:
            return jsonify({'error': f'Produit {produit_id} non trouvé'}), 400
        
        if produit['stock'] < quantite:
            return jsonify({'error': f'Stock insuffisant pour {produit["nom"]}'}), 400
        
        total += produit['prix'] * quantite
    
    # Créer la commande
    cursor = db.execute(
        'INSERT INTO commandes (client_nom, client_email, client_telephone, total) VALUES (?, ?, ?, ?)',
        (client_nom, client_email, client_telephone, total)
    )
    commande_id = cursor.lastrowid
    
    # Ajouter les items et mettre à jour le stock
    for item in items:
        produit_id = item.get('produit_id')
        quantite = item.get('quantite', 1)
        
        produit = db.execute('SELECT * FROM produits WHERE id = ?', (produit_id,)).fetchone()
        
        db.execute(
            'INSERT INTO commande_items (commande_id, produit_id, quantite, prix_unitaire) VALUES (?, ?, ?, ?)',
            (commande_id, produit_id, quantite, produit['prix'])
        )
        
        db.execute(
            'UPDATE produits SET stock = stock - ? WHERE id = ?',
            (quantite, produit_id)
        )
    
    db.commit()
    
    # Envoyer une notification (simulation)
    envoyer_notification_commande(commande_id, client_nom, total)
    
    return jsonify({
        'success': True,
        'commande_id': commande_id,
        'total': total
    })

@app.route('/api/commandes', methods=['GET'])
@admin_required
def get_commandes():
    """Récupérer toutes les commandes"""
    db = get_db()
    commandes = db.execute('''
        SELECT c.*, 
               COUNT(ci.id) as nb_items
        FROM commandes c
        LEFT JOIN commande_items ci ON c.id = ci.commande_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
    ''').fetchall()
    return jsonify([dict(c) for c in commandes])

@app.route('/api/commandes/<int:commande_id>/items', methods=['GET'])
@admin_required
def get_commande_items(commande_id):
    """Récupérer les items d'une commande"""
    db = get_db()
    items = db.execute('''
        SELECT ci.*, p.nom as produit_nom
        FROM commande_items ci
        JOIN produits p ON ci.produit_id = p.id
        WHERE ci.commande_id = ?
    ''', (commande_id,)).fetchall()
    return jsonify([dict(i) for i in items])

@app.route('/api/commandes/<int:commande_id>/statut', methods=['PUT'])
@admin_required
def update_commande_statut(commande_id):
    """Mettre à jour le statut d'une commande"""
    data = request.get_json()
    statut = data.get('statut')
    
    if not statut:
        return jsonify({'error': 'Statut requis'}), 400
    
    db = get_db()
    db.execute(
        'UPDATE commandes SET statut = ? WHERE id = ?',
        (statut, commande_id)
    )
    db.commit()
    
    return jsonify({'success': True})

@app.route('/api/messages-boutique', methods=['POST'])
def create_message_boutique():
    """Créer un nouveau message de client"""
    data = request.get_json()
    client_nom = data.get('client_nom')
    client_email = data.get('client_email')
    sujet = data.get('sujet')
    message = data.get('message')
    
    if not client_nom or not client_email or not sujet or not message:
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    
    db = get_db()
    cursor = db.execute(
        'INSERT INTO messages_boutique (client_nom, client_email, sujet, message) VALUES (?, ?, ?, ?)',
        (client_nom, client_email, sujet, message)
    )
    message_id = cursor.lastrowid
    db.commit()
    
    # Envoyer une notification (simulation)
    envoyer_notification_message(message_id, client_nom, sujet)
    
    return jsonify({
        'success': True,
        'message_id': message_id
    })

@app.route('/api/messages-boutique', methods=['GET'])
@admin_required
def get_messages_boutique():
    """Récupérer tous les messages de la boutique"""
    db = get_db()
    messages = db.execute('SELECT * FROM messages_boutique ORDER BY created_at DESC').fetchall()
    return jsonify([dict(m) for m in messages])

@app.route('/api/messages-boutique/<int:message_id>/lu', methods=['PUT'])
@admin_required
def mark_message_lu(message_id):
    """Marquer un message comme lu"""
    db = get_db()
    db.execute(
        'UPDATE messages_boutique SET statut = ? WHERE id = ?',
        ('lu', message_id)
    )
    db.commit()
    
    return jsonify({'success': True})

@app.route('/api/notifications', methods=['GET'])
@admin_required
def get_notifications():
    """Récupérer les notifications non lues"""
    db = get_db()
    
    # Commandes non notifiées
    commandes_non_notifiees = db.execute(
        'SELECT * FROM commandes WHERE notification_envoyee = FALSE'
    ).fetchall()
    
    # Messages non notifiés
    messages_non_notifies = db.execute(
        'SELECT * FROM messages_boutique WHERE notification_envoyee = FALSE'
    ).fetchall()
    
    return jsonify({
        'commandes': [dict(c) for c in commandes_non_notifiees],
        'messages': [dict(m) for m in messages_non_notifies]
    })

def envoyer_notification_commande(commande_id, client_nom, total):
    """Simuler l'envoi d'une notification pour une nouvelle commande"""
    total_formate = f"{total:,.0f} FCFA".replace(',', ' ')
    print(f"🔔 NOUVELLE COMMANDE #{commande_id}")
    print(f"Client: {client_nom}")
    print(f"Total: {total_formate}")
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    
    # Marquer comme notifié
    db = get_db()
    db.execute(
        'UPDATE commandes SET notification_envoyee = TRUE WHERE id = ?',
        (commande_id,)
    )
    db.commit()

def envoyer_notification_message(message_id, client_nom, sujet):
    """Simuler l'envoi d'une notification pour un nouveau message"""
    print(f"💬 NOUVEAU MESSAGE DE #{message_id}")
    print(f"Client: {client_nom}")
    print(f"Sujet: {sujet}")
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    
    # Marquer comme notifié
    db = get_db()
    db.execute(
        'UPDATE messages_boutique SET notification_envoyee = TRUE WHERE id = ?',
        (message_id,)
    )
    db.commit()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
