# Project Context - SOAP Notice

> Ce fichier contient les règles critiques et patterns de code que les agents AI DOIVENT suivre lors de l'implémentation.

## Projet

**Nom:** SOAP Notice
**Description:** Application de transcription audio pour physiothérapeutes - transforme des enregistrements d'anamnèses en notes SOAP structurées.

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | Vite + React + TailwindCSS |
| Backend | Python FastAPI |
| Speech-to-Text | Deepgram API (WebSocket) |
| LLM Extraction | **Mistral AI** (MVP) → Azure OpenAI (si besoin) |
| Base de données | PostgreSQL EU |

---

## Deepgram - Règles Critiques

### Installation SDK Python

```bash
pip install deepgram-sdk httpx
```

### Modèle et Langues Supportées

- **Modèle recommandé:** `nova-3` (meilleure précision, multilingue)
- **Langues requises:** Français, Allemand, Anglais, Espagnol

| Langue | Code Deepgram | Statut Nova-3 |
|--------|---------------|---------------|
| Français | `fr`, `fr-CA` | ✅ Supporté |
| Allemand | `de`, `de-CH` | ✅ Supporté |
| Anglais | `en`, `en-US`, `en-GB` | ✅ Supporté |
| Espagnol | `es`, `es-419` | ✅ Supporté |
| Multilingue auto | `multi` | ✅ Détection automatique |

```python
# Configuration multilingue
model = "nova-3"
language = "multi"  # Détection automatique de la langue
# OU spécifier explicitement: "fr", "de", "en", "es"
smart_format = True
```

### Pattern de Transcription Live (WebSocket)

```python
# main.py - Pattern de référence Deepgram Live Streaming

import httpx
import threading
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV1SocketClientResponse

def transcribe_audio_stream(audio_source_url: str) -> None:
    """
    Transcrit un flux audio en temps réel via Deepgram WebSocket.

    IMPORTANT:
    - La clé API doit être dans DEEPGRAM_API_KEY (env var)
    - Utiliser nova-3 avec language=fr pour le français
    """
    deepgram = DeepgramClient()  # Lit DEEPGRAM_API_KEY automatiquement

    # Connexion WebSocket avec paramètres optimaux
    # language: "fr", "de", "en", "es" ou "multi" (détection auto)
    with deepgram.listen.v1.connect(
        model="nova-3",
        language="multi",  # Ou langue spécifique selon sélection user
        smart_format=True,
        punctuate=True,
    ) as connection:

        def on_message(message: ListenV1SocketClientResponse) -> None:
            """Callback pour chaque résultat de transcription."""
            if hasattr(message, 'channel') and hasattr(message.channel, 'alternatives'):
                transcript = message.channel.alternatives[0].transcript
                if transcript:  # Ignorer les résultats vides
                    print(f"Transcription: {transcript}")
                    # TODO: Envoyer au LLM pour extraction SOAP

        # Enregistrer les event handlers
        connection.on(EventType.OPEN, lambda _: print("Connexion Deepgram ouverte"))
        connection.on(EventType.MESSAGE, on_message)
        connection.on(EventType.CLOSE, lambda _: print("Connexion fermée"))
        connection.on(EventType.ERROR, lambda err: print(f"Erreur: {err}"))

        # Thread d'écoute
        def listening_thread():
            connection.start_listening()

        listen_thread = threading.Thread(target=listening_thread)
        listen_thread.start()

        # Thread de streaming audio
        def stream_audio():
            with httpx.stream("GET", audio_source_url) as response:
                for chunk in response.iter_bytes():
                    connection.send_media(chunk)

        audio_thread = threading.Thread(target=stream_audio)
        audio_thread.start()

        # Attendre la fin
        audio_thread.join()
        listen_thread.join()
```

### Paramètres WebSocket Importants

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| `model` | `nova-3` | Meilleur modèle pour le français |
| `language` | `fr` | Français |
| `smart_format` | `true` | Formate nombres, dates, emails |
| `punctuate` | `true` | Ajoute la ponctuation |
| `interim_results` | `false` | Résultats finaux uniquement (défaut) |
| `endpointing` | `300` | Délai fin de phrase en ms (optionnel) |

### Structure des Résultats

```python
# Le message reçu contient:
message.channel.alternatives[0].transcript  # Le texte transcrit
message.channel.alternatives[0].confidence  # Score de confiance (0-1)
message.channel.alternatives[0].words       # Liste des mots avec timestamps

# Chaque mot:
word = {
    "word": "bonjour",
    "start": 0.5,      # Timestamp début (secondes)
    "end": 0.8,        # Timestamp fin
    "confidence": 0.98
}
```

### Gestion des Erreurs

```python
# Messages de contrôle WebSocket
# Envoyer pour garder la connexion active:
connection.send({"type": "KeepAlive"})

# Pour terminer proprement:
connection.send({"type": "CloseStream"})

# Pour forcer le flush des résultats:
connection.send({"type": "Finalize"})
```

### Variables d'Environnement Requises

```bash
DEEPGRAM_API_KEY=your_api_key_here
```

---

## Contraintes Projet

### Multilingue
- **Langues MVP:** Français, Allemand, Anglais, Espagnol
- L'utilisateur peut sélectionner la langue OU utiliser la détection automatique (`multi`)
- L'interface utilisateur doit supporter ces 4 langues
- Les notes SOAP générées sont dans la langue de la transcription

### RGPD / Données de Santé
- Serveurs EU uniquement pour PostgreSQL
- Pas de stockage permanent des audio (transcription uniquement)
- Chiffrement des données en transit et au repos

### UX
- Interface minimaliste : 1 bouton enregistrer, 1 bouton copier
- Latence acceptable : < 30s pour 10min d'audio
- Édition post-transcription obligatoire
- Sélecteur de langue visible

### Architecture
- Pas de sur-ingénierie
- Flux linéaire MVP : Record → Transcribe → Extract → Display → Copy

---

## Mistral AI - Extraction SOAP

### Installation SDK Python

```bash
pip install mistralai
```

### Configuration

```python
from mistralai.client import MistralClient

# Initialisation (clé API en env var)
client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
```

### Pattern d'Extraction SOAP

```python
# extraction_service.py
from mistralai.client import MistralClient
import os

def extract_soap_note(transcript: str, template: str, language: str = "fr") -> str:
    """
    Extrait une note SOAP structurée à partir d'une transcription.

    Args:
        transcript: Texte transcrit de l'anamnèse
        template: Template SOAP (4 sections)
        language: Langue de la note (fr, de, en)

    Returns:
        Note SOAP formatée en markdown
    """
    client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

    system_prompt = f"""Tu es un assistant médical expert en documentation clinique.
Extrais les informations de la transcription et structure-les selon le template SOAP fourni.

Règles CRITIQUES:
- Utilise UNIQUEMENT les informations présentes dans la transcription
- N'invente JAMAIS d'informations cliniques
- Respecte strictement la structure du template
- Génère la note en {language}
- Si une section manque d'informations, écris "Non documenté" ou "À compléter"
"""

    user_prompt = f"""Template SOAP:
{template}

Transcription de l'anamnèse:
{transcript}

Génère la note SOAP complète en respectant strictement le template."""

    response = client.chat(
        model="mistral-large-2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  # Faible pour cohérence
        max_tokens=2000
    )

    return response.choices[0].message.content
```

### Architecture Switchable LLM

**IMPORTANT:** Utiliser une abstraction pour permettre le switch Mistral → Azure OpenAI facilement.

```python
# llm_provider.py
from abc import ABC, abstractmethod
from enum import Enum
import os

class LLMProvider(Enum):
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"

class BaseLLMClient(ABC):
    @abstractmethod
    def extract_soap_note(self, transcript: str, template: str, language: str) -> str:
        pass

class MistralClient(BaseLLMClient):
    def __init__(self):
        from mistralai.client import MistralClient as MC
        self.client = MC(api_key=os.getenv("MISTRAL_API_KEY"))

    def extract_soap_note(self, transcript: str, template: str, language: str) -> str:
        # Implémentation Mistral (voir ci-dessus)
        pass

class AzureOpenAIClient(BaseLLMClient):
    def __init__(self):
        from openai import AzureOpenAI
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01"
        )

    def extract_soap_note(self, transcript: str, template: str, language: str) -> str:
        # Implémentation Azure OpenAI
        pass

# Factory
def get_llm_client() -> BaseLLMClient:
    provider = LLMProvider(os.getenv("LLM_PROVIDER", "mistral"))
    if provider == LLMProvider.MISTRAL:
        return MistralClient()
    elif provider == LLMProvider.AZURE_OPENAI:
        return AzureOpenAIClient()
```

### Variables d'Environnement

```bash
# MVP
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your_mistral_api_key

# Si switch vers Azure
LLM_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_azure_key
```

### Paramètres Critiques

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| `model` | `mistral-large-2` | Meilleur modèle Mistral pour extraction structurée |
| `temperature` | `0.3` | Faible = cohérence et précision (pas de créativité) |
| `max_tokens` | `2000` | Suffisant pour note SOAP complète |

---

## Format de Sortie SOAP

Le template cible pour l'extraction LLM se trouve dans:
`docs/templates/physiotherapy-note-template.md`

Sections principales:
1. **Subjective Assessment** - Plainte, historique, impact fonctionnel
2. **Objective Assessment** - Observations, examen physique
3. **Clinical Reasoning** - Diagnostic, mesures
4. **Management Plan** - Traitement, programme domicile, suivi
