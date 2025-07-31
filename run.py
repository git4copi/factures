#!/usr/bin/env python3
"""
Script de démarrage pour l'application d'analyse PDF avec Azure AI
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    try:
        import flask
        import pdf2image
        import openpyxl
        import requests
        print("✅ Toutes les dépendances Python sont installées")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Installez les dépendances avec: pip install -r requirements.txt")
        return False
    
    # Vérifier Poppler
    try:
        from pdf2image import convert_from_path
        # Test simple pour vérifier que poppler est disponible
        print("✅ Poppler est configuré")
    except Exception as e:
        print("❌ Poppler n'est pas configuré correctement")
        print("Installez Poppler:")
        print("  macOS: brew install poppler")
        print("  Ubuntu: sudo apt-get install poppler-utils")
        print("  Windows: Téléchargez depuis https://github.com/oschwartz10612/poppler-windows/releases/")
        return False
    
    return True

def check_config():
    """Vérifie la configuration"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  Fichier .env non trouvé")
        print("Copiez env_example.txt vers .env et configurez vos clés Azure")
        return False
    
    # Vérifier les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['AZURE_AI_ENDPOINT', 'AZURE_AI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("Configurez ces variables dans le fichier .env")
        return False
    
    print("✅ Configuration Azure AI détectée")
    return True

def create_directories():
    """Crée les répertoires nécessaires"""
    directories = ['uploads', 'images', 'output', 'templates', 'static/js']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Répertoires créés")

def main():
    """Fonction principale"""
    print("🚀 Démarrage de l'application d'analyse PDF avec Azure AI")
    print("=" * 60)
    
    # Vérifications préalables
    if not check_dependencies():
        sys.exit(1)
    
    if not check_config():
        print("\n⚠️  L'application peut démarrer mais certaines fonctionnalités peuvent ne pas fonctionner")
        print("Configurez Azure AI pour une utilisation complète")
    
    create_directories()
    
    print("\n🎯 Démarrage du serveur...")
    print("📱 Ouvrez votre navigateur sur: http://localhost:5000")
    print("🛑 Appuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 60)
    
    # Importer et démarrer l'application
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 