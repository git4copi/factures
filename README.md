# Analyse PDF avec Azure AI

Une application web moderne pour convertir des fichiers PDF en images et les analyser avec Azure AI Vision.

## 🚀 Fonctionnalités

- **Conversion PDF vers PNG** : Convertit automatiquement chaque page du PDF en image haute qualité
- **Analyse IA** : Utilise Azure AI Vision pour extraire des informations structurées des images
- **Interface moderne** : Interface web responsive avec drag & drop
- **Export Excel** : Génère automatiquement un fichier Excel avec les résultats analysés
- **Prompt personnalisable** : Permet de définir des instructions spécifiques pour l'analyse

## 📋 Prérequis

- Python 3.8+
- Compte Azure avec accès à Azure AI Services
- Poppler (pour la conversion PDF)

### Installation de Poppler

**macOS :**
```bash
brew install poppler
```

**Ubuntu/Debian :**
```bash
sudo apt-get install poppler-utils
```

**Windows :**
Téléchargez depuis [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)

## 🛠️ Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd factures
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp env_example.txt .env
```

Éditez le fichier `.env` avec vos informations Azure :
```env
AZURE_AI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_AI_API_KEY=your-azure-ai-api-key-here
AZURE_AI_DEPLOYMENT_NAME=gpt-4-vision-preview
```

## 🚀 Utilisation

1. **Démarrer l'application**
```bash
python app.py
```

2. **Ouvrir votre navigateur**
```
http://localhost:5000
```

3. **Utiliser l'interface**
   - Glissez-déposez ou sélectionnez un fichier PDF
   - Glissez-déposez ou sélectionnez un fichier Excel
   - Saisissez votre prompt d'analyse
   - Cliquez sur "Traiter les fichiers"

## 📁 Structure du projet

```
factures/
├── app.py                 # Serveur Flask principal
├── pdf_processor.py       # Conversion PDF vers images
├── azure_ai_processor.py  # Intégration Azure AI
├── excel_processor.py     # Traitement des fichiers Excel
├── requirements.txt       # Dépendances Python
├── templates/
│   └── index.html        # Interface utilisateur
├── static/
│   └── js/
│       └── app.js        # Logique JavaScript
├── uploads/              # Fichiers uploadés
├── images/               # Images converties
└── output/               # Fichiers de sortie
```

## 🔧 Configuration Azure AI

1. **Créer une ressource Azure AI**
   - Allez sur le portail Azure
   - Créez une ressource "Azure OpenAI"
   - Notez l'endpoint et la clé API

2. **Déployer un modèle**
   - Dans votre ressource Azure OpenAI
   - Déployez un modèle GPT-4 Vision
   - Notez le nom du déploiement

3. **Configurer les variables**
   - Mettez à jour le fichier `.env` avec vos informations

## 📊 Format des données

L'application extrait automatiquement les informations suivantes :
- Type de document
- Date
- Montant
- Devise
- Émetteur
- Destinataire
- Numéro de document
- Autres informations

## 🎨 Personnalisation

### Modifier les colonnes Excel

Éditez `excel_processor.py` pour changer les en-têtes par défaut :

```python
self.default_headers = [
    'Page',
    'Type Document',
    'Date',
    'Montant',
    # Ajoutez vos colonnes personnalisées
]
```

### Personnaliser le prompt

Modifiez le prompt par défaut dans `templates/index.html` :

```html
<textarea class="form-control" id="promptInput" rows="3" 
          placeholder="Votre prompt personnalisé...">Votre prompt par défaut</textarea>
```

### Ajouter des validations

Étendez `azure_ai_processor.py` pour ajouter des validations personnalisées :

```python
def validate_extraction_result(self, result: Dict[str, Any]) -> bool:
    # Ajoutez vos règles de validation
    required_fields = ['votre_champ_requis']
    return all(field in result.get('content', {}) for field in required_fields)
```

## 🐛 Dépannage

### Erreur de conversion PDF
- Vérifiez que Poppler est installé
- Assurez-vous que le fichier PDF n'est pas corrompu

### Erreur Azure AI
- Vérifiez vos clés API dans le fichier `.env`
- Assurez-vous que votre déploiement Azure est actif
- Vérifiez les quotas de votre ressource Azure

### Erreur de mémoire
- Réduisez la résolution des images dans `pdf_processor.py`
- Traitez les fichiers par petits lots

## 📝 Licence

Ce projet est sous licence MIT.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## 📞 Support

Pour toute question ou problème :
1. Vérifiez la section dépannage
2. Consultez les issues GitHub
3. Créez une nouvelle issue si nécessaire 