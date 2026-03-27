📘 README.md — Freebox Ultra (NetworkControl) pour Home Assistant

  logo.svg

Freebox Ultra – NetworkControl Integration
Intégration complète des profils Freebox Ultra OS 15 dans Home Assistant
Cette intégration apporte à Home Assistant un support avancé pour la Freebox Ultra (Freebox OS 15) en exploitant le module NetworkControl, encore non documenté officiellement mais totalement fonctionnel en API REST.
Elle permet :


🔍 Découverte automatique des profils NetworkControl
🔄 Mise à jour en temps réel via DataUpdateCoordinator
🎚 Création automatique d’un switch par profil
🔌 Pause / Reprise d’Internet pour chaque profil
🖼 Icônes Freebox personnalisées (profil + entité)
📡 Attributs enrichis : appareils, MACs, modes, planning
🔐 Authentification v8 par HMAC SHA1
🛠 Compatibilité totale Home Assistant 2025–2026

Cette intégration n’est pas affiliée à Free.
Elle s’adresse aux utilisateurs avancés souhaitant exploiter pleinement leur Freebox Ultra via Home Assistant.

🚀 Fonctionnalités
✔ Découverte automatique des profils
L’intégration identifie tous les profils déclarés dans Freebox OS via :
GET /api/v8/network_control/
✔ Switchs automatiques
Un switch est créé pour chaque profil :
switch.freebox_profile_pc_caro  
switch.freebox_profile_tv_salon  
switch.freebox_profile_bloque_nuit  
switch.freebox_profile_mathis

✔ Icônes dynamiques

Icônes Freebox Ultra (entity_picture)
Icône MDI fallback :

🔓 allowed → mdi:account-check
🔒 denied → mdi:account-lock



✔ Attributs HA enrichis
Chaque entité expose :

Liste des MACs du profil
Liste des appareils connectés
current_mode / override_mode
rule_mode / planning
icône Freebox native
état override

Exemple dans Developer Tools :
YAMLmacs:  - D8:0F:99:6C:FB:7Dhosts:  - DELL-Carooverride: falsecurrent_mode: allowedoverride_mode: allowedprofile_icon: /resources/images/profile/profile_12.pngAfficher plus de lignes
✔ Commandes Internet

ON = Internet autorisé
OFF = Internet bloqué
Basé sur l’API Ultra :
PUT /api/v8/network_control/{profile_id}


🔐 Authentification Freebox Ultra
L’intégration utilise l’auth v8 officielle :

Challenge →
HMAC SHA1 (app_token) →
Session Freebox OS →
Header : X-Fbx-App-Auth

Le token est stocké dans Home Assistant via config_flow.

📦 Installation (manuelle)
1. Copier les fichiers
Copier le dossier :
custom_components/freebox_ultra/

dans :
/config/custom_components/

2. Redémarrer Home Assistant
3. Ajouter l’intégration
Dans HA :
Paramètres → Appareils & Services → Ajouter → Freebox Ultra

Appuyer sur la flèche de la Freebox Ultra pour valider.

🧠 Architecture technique
API :
✔ GET /api/v8/network_control/
✔ GET /api/v8/network_control/{id}
✔ PUT /api/v8/network_control/{id}
Configuration :

__init__.py → initialisation API + coordinator
api.py → client REST Freebox Ultra
coordinator.py → update régulier des profils
switch.py → entités automatiques
config_flow.py → authentification Freebox Ultra
logo.svg, icon.svg, info.md → support HACS


🧩 Schéma des entités
Freebox Ultra
 ├── switch.freebox_profile_pc_caro
 ├── switch.freebox_profile_tv_salon
 ├── switch.freebox_profile_bloque_nuit
 └── switch.freebox_profile_mathis

Chaque switch contrôle :

override_mode
override
current_mode

Et expose toutes les infos réseau liées.

🛠 Dépannage
Problème : “Liste d’adresses MAC manquante”
Le PUT doit renvoyer l’objet complet → corrigé dans l’intégration.
Problème : “cannot_connect”
Assurez-vous que l’authentification a été validée sur la Freebox (bouton flèche).
Problème : Les profils ne se mettent pas à jour
Vérifier que HA atteint Freebox Ultra en HTTPS (https://{api_domain}:{port}).

❤️ Crédits

Freebox Ultra (Free SAS)
Home Assistant
Développement : intégration personnalisée spécialisée Freebox Ultra OS 15
Icônes : design original, style Home Assistant + Freebox Ultra


🔮 Roadmap

Ajout des sensors WiFi / débit Freebox Ultra
Support complet WebSocket Freebox OS
Entités énergie (si Free expose)
Support HACS officiel


📄 Licence
MIT License.
Utilisable librement, modification encouragée.