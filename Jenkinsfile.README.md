# Pipeline Jenkins pour le déploiement Fastline

Ce document explique comment configurer et utiliser le pipeline Jenkins pour déployer l'application Fastline.

## Prérequis

1. Serveur Jenkins avec les plugins suivants :
   - Docker Pipeline
   - Kubernetes CLI
   - Credentials Binding
   - Slack Notification (optionnel)
   - JUnit (pour les rapports de test)

2. Outils requis sur le nœud Jenkins :
   - Docker
   - kubectl
   - Helm (pour le déploiement de l'ingress controller)
   - Git

## Configuration des identifiants

### 1. Identifiants Docker
Créez des identifiants Jenkins pour accéder au registre Docker :
1. Allez dans Jenkins > Credentials > System > Global credentials
2. Ajoutez des identifiants avec l'ID `docker-hub-credentials` contenant :
   - Username : votre nom d'utilisateur Docker
   - Password : votre mot de passe/jeton d'accès

### 2. Configuration Kubernetes
Ajoutez votre fichier kubeconfig :
1. Allez dans Jenkins > Credentials > System > Global credentials
2. Ajoutez un fichier avec l'ID `kube-config` contenant votre fichier kubeconfig

### 3. Variables d'environnement
Copiez le fichier `.env.example` vers `.env` et configurez les variables nécessaires.

## Étapes du pipeline

1. **Préparation**
   - Charge les variables d'environnement
   - Vérifie les dépendances

2. **Build des images**
   - Construit les images Docker pour app1 et app2 en parallèle
   - Tagge les images avec le numéro de build et 'latest'

3. **Tests**
   - Exécute les tests unitaires pour app1 et app2
   - Génère des rapports JUnit

4. **Publication des images**
   - Se connecte au registre Docker
   - Push les images vers le registre

5. **Déploiement sur Kubernetes**
   - Configure kubectl
   - Met à jour les numéros de version dans les déploiements
   - Applique les configurations Kubernetes
   - Vérifie le statut des déploiements

6. **Tests d'intégration**
   - Attend que les services soient prêts
   - Exécute les tests d'intégration

## Configuration du webhook (optionnel)

Pour déclencher automatiquement le pipeline lors d'un push sur GitHub :

1. Dans Jenkins, allez dans la configuration du job
2. Activez "GitHub hook trigger for GITScm polling"
3. Dans votre dépôt GitHub, ajoutez un webhook pointant vers `http://<votre-jenkins>/github-webhook/`

## Personnalisation

Vous pouvez personnaliser le pipeline en modifiant :
- Les commandes de test dans l'étape "Tests"
- Les notifications Slack dans la section `post`
- Les commandes de déploiement dans "Déploiement sur Kubernetes"

## Dépannage

- Si le déploiement échoue, vérifiez les logs avec :
  ```bash
  kubectl logs -n fastline <nom-du-pod>
  ```
- Pour voir les événements Kubernetes :
  ```bash
  kubectl get events -n fastline
  ```
- Vérifiez l'état des pods :
  ```bash
  kubectl get pods -n fastline
  ```
