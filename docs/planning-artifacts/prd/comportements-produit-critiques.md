# Comportements Produit Critiques

## Langue de Génération des Notes

**Règle absolue :** La note SOAP générée est **TOUJOURS** dans la langue de l'application de l'utilisateur, **jamais** dans la langue de la transcription audio.

| Langue app utilisateur | Langue patient/audio | Langue note générée |
|------------------------|---------------------|---------------------|
| Français | Allemand | **Français** |
| Allemand | Français | **Allemand** |
| Anglais | Espagnol | **Anglais** |

**Cas d'usage :** Un kiné suisse francophone reçoit un patient germanophone. L'enregistrement est en allemand, mais sa note clinique est générée en français car c'est sa langue de travail.

## Gestion Historique (Max 10 Notes)

**Comportement lors de l'atteinte de la limite :**

1. L'utilisateur a 10 notes sauvegardées
2. Il génère une nouvelle note (11ème)
3. **Avant sauvegarde** : Notification apparaît :
   > *"Vous avez atteint la limite de 10 notes. La note la plus ancienne (du [date]) sera supprimée. Continuer ?"*
4. **[Confirmer]** → Note ancienne supprimée, nouvelle note sauvegardée
5. **[Annuler]** → L'utilisateur peut copier/exporter manuellement avant de confirmer

**Rationale :** Éviter la suppression silencieuse de données potentiellement importantes pour l'utilisateur.
