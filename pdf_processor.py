import os
from pdf2image import convert_from_path
from PIL import Image
import tempfile

class PDFProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def convert_pdf_to_images(self, pdf_path, output_folder):
        """
        Convertit un fichier PDF en images PNG
        Retourne une liste d'informations sur les images créées
        """
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Fichier PDF non trouvé: {pdf_path}")
            
            # Créer le dossier de sortie s'il n'existe pas
            os.makedirs(output_folder, exist_ok=True)
            
            # Convertir le PDF en images
            images = convert_from_path(pdf_path, dpi=300)
            
            images_info = []
            base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for i, image in enumerate(images):
                # Nom du fichier image
                image_filename = f"{base_filename}_page_{i+1:03d}.png"
                image_path = os.path.join(output_folder, image_filename)
                
                # Sauvegarder l'image
                image.save(image_path, 'PNG', quality=95)
                
                # Ajouter les informations de l'image
                images_info.append({
                    'page': i + 1,
                    'path': image_path,
                    'filename': image_filename,
                    'size': os.path.getsize(image_path),
                    'dimensions': image.size
                })
            
            return images_info
            
        except Exception as e:
            raise Exception(f"Erreur lors de la conversion PDF: {str(e)}")
    
    def get_pdf_info(self, pdf_path):
        """
        Récupère les informations de base du PDF
        """
        try:
            images = convert_from_path(pdf_path, dpi=300)
            return {
                'page_count': len(images),
                'file_size': os.path.getsize(pdf_path)
            }
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du PDF: {str(e)}")
    
    def extract_specific_page(self, pdf_path, page_number, output_folder):
        """
        Extrait une page spécifique du PDF
        """
        try:
            images = convert_from_path(pdf_path, dpi=300, first_page=page_number, last_page=page_number)
            
            if not images:
                raise Exception(f"Page {page_number} non trouvée")
            
            image = images[0]
            base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            image_filename = f"{base_filename}_page_{page_number:03d}.png"
            image_path = os.path.join(output_folder, image_filename)
            
            image.save(image_path, 'PNG', quality=95)
            
            return {
                'page': page_number,
                'path': image_path,
                'filename': image_filename,
                'size': os.path.getsize(image_path),
                'dimensions': image.size
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction de la page {page_number}: {str(e)}") 