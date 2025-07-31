import os
import base64
import requests
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AzureAIProcessor:
    def __init__(self):
        self.endpoint = os.getenv('AZURE_AI_ENDPOINT')
        self.api_key = os.getenv('AZURE_AI_API_KEY')
        self.deployment_name = os.getenv('AZURE_AI_DEPLOYMENT_NAME', 'gpt-4-vision-preview')
        
        if not self.endpoint or not self.api_key:
            raise ValueError("AZURE_AI_ENDPOINT et AZURE_AI_API_KEY doivent être définis dans .env")
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode une image en base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Analyse une image avec Azure AI Vision
        """
        try:
            # Encoder l'image en base64
            base64_image = self.encode_image_to_base64(image_path)
            
            # Préparer les headers
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            # Préparer le payload
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Appeler l'API Azure
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version=2024-02-15-preview"
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parser la réponse
            result = response.json()
            
            # Extraire le contenu de la réponse
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Essayer de parser comme JSON si possible
                try:
                    parsed_content = json.loads(content)
                    return {
                        'success': True,
                        'content': parsed_content,
                        'raw_content': content,
                        'usage': result.get('usage', {})
                    }
                except json.JSONDecodeError:
                    # Si ce n'est pas du JSON, retourner le texte brut
                    return {
                        'success': True,
                        'content': content,
                        'raw_content': content,
                        'usage': result.get('usage', {})
                    }
            else:
                return {
                    'success': False,
                    'error': 'Aucune réponse valide de l\'API',
                    'raw_response': result
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Erreur de requête: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de l\'analyse: {str(e)}'
            }
    
    def extract_structured_data(self, image_path: str, extraction_prompt: str) -> Dict[str, Any]:
        """
        Extrait des données structurées d'une image
        """
        structured_prompt = f"""
        {extraction_prompt}
        
        Veuillez répondre avec un JSON structuré contenant les informations extraites.
        Format attendu:
        {{
            "type_document": "string",
            "date": "YYYY-MM-DD",
            "montant": "number",
            "devise": "string",
            "emetteur": "string",
            "destinataire": "string",
            "numero_document": "string",
            "autres_informations": {{}}
        }}
        """
        
        return self.analyze_image(image_path, structured_prompt)
    
    def validate_extraction_result(self, result: Dict[str, Any]) -> bool:
        """
        Valide si le résultat d'extraction est correct
        """
        if not result.get('success', False):
            return False
        
        content = result.get('content', {})
        
        # Vérifier si c'est un dictionnaire
        if not isinstance(content, dict):
            return False
        
        # Vérifier les champs requis (à adapter selon vos besoins)
        required_fields = ['type_document', 'date', 'montant']
        return all(field in content for field in required_fields) 