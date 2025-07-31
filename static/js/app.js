// Variables globales
let uploadedFiles = {
    pdf_path: null,
    excel_path: null
};

let currentResults = null;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
    setupFileInputs();
});

// Configuration du drag and drop
function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        handleDroppedFiles(files);
    });
}

// Configuration des inputs de fichiers
function setupFileInputs() {
    const pdfFile = document.getElementById('pdfFile');
    const excelFile = document.getElementById('excelFile');
    
    pdfFile.addEventListener('change', function(e) {
        validateFile(e.target, '.pdf');
    });
    
    excelFile.addEventListener('change', function(e) {
        validateFile(e.target, '.xlsx,.xls');
    });
}

// Gestion des fichiers déposés
function handleDroppedFiles(files) {
    for (let file of files) {
        if (file.type === 'application/pdf') {
            document.getElementById('pdfFile').files = new FileList([file]);
        } else if (file.type.includes('spreadsheet') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
            document.getElementById('excelFile').files = new FileList([file]);
        }
    }
}

// Validation des fichiers
function validateFile(input, acceptedTypes) {
    const file = input.files[0];
    if (file) {
        const isValid = acceptedTypes.split(',').some(type => 
            file.name.toLowerCase().endsWith(type.trim())
        );
        
        if (!isValid) {
            showAlert('Type de fichier non supporté. Veuillez sélectionner un fichier valide.', 'error');
            input.value = '';
        }
    }
}

// Upload et traitement des fichiers
async function uploadFiles() {
    const pdfFile = document.getElementById('pdfFile').files[0];
    const excelFile = document.getElementById('excelFile').files[0];
    const prompt = document.getElementById('promptInput').value;
    
    if (!pdfFile || !excelFile) {
        showAlert('Veuillez sélectionner un fichier PDF et un fichier Excel.', 'error');
        return;
    }
    
    if (!prompt.trim()) {
        showAlert('Veuillez saisir un prompt d\'analyse.', 'error');
        return;
    }
    
    // Désactiver le bouton et afficher la progression
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="loading-spinner me-2"></span>Traitement en cours...';
    
    showProgress();
    
    try {
        // Étape 1: Upload des fichiers
        updateProgress(10, 'Upload des fichiers...');
        const uploadResult = await uploadFilesToServer(pdfFile, excelFile);
        
        if (!uploadResult.success) {
            throw new Error(uploadResult.error);
        }
        
        uploadedFiles = {
            pdf_path: uploadResult.pdf_path,
            excel_path: uploadResult.excel_path
        };
        
        // Étape 2: Traitement avec Azure AI
        updateProgress(30, 'Conversion PDF en images...');
        const processResult = await processFilesWithAI(uploadedFiles.pdf_path, uploadedFiles.excel_path, prompt);
        
        if (!processResult.success) {
            throw new Error(processResult.error);
        }
        
        currentResults = processResult;
        
        // Étape 3: Affichage des résultats
        updateProgress(100, 'Traitement terminé!');
        setTimeout(() => {
            hideProgress();
            showResults(processResult.results);
            resetUploadButton();
        }, 1000);
        
    } catch (error) {
        console.error('Erreur:', error);
        showAlert(`Erreur lors du traitement: ${error.message}`, 'error');
        hideProgress();
        resetUploadButton();
    }
}

// Upload des fichiers vers le serveur
async function uploadFilesToServer(pdfFile, excelFile) {
    const formData = new FormData();
    formData.append('pdf_file', pdfFile);
    formData.append('excel_file', excelFile);
    
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    if (!response.ok) {
        throw new Error(result.error || 'Erreur lors de l\'upload');
    }
    
    return result;
}

// Traitement avec Azure AI
async function processFilesWithAI(pdfPath, excelPath, prompt) {
    const response = await fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            pdf_path: pdfPath,
            excel_path: excelPath,
            prompt: prompt
        })
    });
    
    const result = await response.json();
    
    if (!response.ok) {
        throw new Error(result.error || 'Erreur lors du traitement');
    }
    
    return result;
}

// Affichage des résultats
function showResults(results) {
    const container = document.getElementById('resultsContainer');
    const resultsList = document.getElementById('resultsList');
    
    resultsList.innerHTML = '';
    
    results.forEach((result, index) => {
        const card = createResultCard(result, index);
        resultsList.appendChild(card);
    });
    
    container.style.display = 'block';
    container.scrollIntoView({ behavior: 'smooth' });
}

// Création d'une carte de résultat
function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    const aiResult = result.ai_result;
    const content = aiResult.content || {};
    
    let statusClass = 'status-info';
    let statusText = 'Analysé';
    
    if (aiResult.success === false) {
        statusClass = 'status-error';
        statusText = 'Erreur';
    } else if (aiResult.success === true) {
        statusClass = 'status-success';
        statusText = 'Succès';
    }
    
    card.innerHTML = `
        <div class="row">
            <div class="col-md-3">
                <h5 class="fw-bold">
                    <i class="fas fa-file-image me-2"></i>Page ${result.page}
                </h5>
                <img src="/images/${result.image_path.split('/').pop()}" 
                     class="image-preview" alt="Page ${result.page}">
            </div>
            <div class="col-md-9">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <h6 class="fw-bold">Résultats de l'analyse</h6>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Type de document:</strong> ${content.type_document || 'Non détecté'}</p>
                        <p><strong>Date:</strong> ${content.date || 'Non détectée'}</p>
                        <p><strong>Montant:</strong> ${content.montant || 'Non détecté'}</p>
                        <p><strong>Devise:</strong> ${content.devise || 'Non détectée'}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Émetteur:</strong> ${content.emetteur || 'Non détecté'}</p>
                        <p><strong>Destinataire:</strong> ${content.destinataire || 'Non détecté'}</p>
                        <p><strong>Numéro document:</strong> ${content.numero_document || 'Non détecté'}</p>
                    </div>
                </div>
                
                ${aiResult.success === false ? 
                    `<div class="alert alert-danger mt-2">
                        <strong>Erreur:</strong> ${aiResult.error}
                    </div>` : ''
                }
            </div>
        </div>
    `;
    
    return card;
}

// Téléchargement des résultats
function downloadResults() {
    if (currentResults && currentResults.output_excel) {
        const filename = currentResults.output_excel.split('/').pop();
        window.open(`/download/${filename}`, '_blank');
    } else {
        showAlert('Aucun fichier à télécharger.', 'error');
    }
}

// Gestion de la progression
function showProgress() {
    document.getElementById('progressContainer').style.display = 'block';
}

function hideProgress() {
    document.getElementById('progressContainer').style.display = 'none';
}

function updateProgress(percentage, text) {
    document.getElementById('progressBar').style.width = percentage + '%';
    document.getElementById('progressText').textContent = percentage + '%';
    
    // Mettre à jour le texte si fourni
    if (text) {
        document.querySelector('#progressContainer .fw-bold').textContent = text;
    }
}

// Réinitialisation du bouton d'upload
function resetUploadButton() {
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = false;
    uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Traiter les fichiers';
}

// Affichage des alertes
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.main-container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss après 5 secondes
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Classe FileList pour la compatibilité
class FileList {
    constructor(files) {
        this.files = files;
        this.length = files.length;
    }
    
    item(index) {
        return this.files[index];
    }
    
    [Symbol.iterator]() {
        return this.files[Symbol.iterator]();
    }
} 