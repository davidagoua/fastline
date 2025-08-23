pipeline {
    agent any
    
    environment {
        // Configuration du registre Docker
        REGISTRY = "localhost:8082"
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
        
        // Configuration Kubernetes
        KUBE_CONFIG = credentials('kube-config')
        
        // Variables d'environnement
        ENV_FILE = '.env'
    }
    
    stages {
        stage('Préparation') {
            steps {
                script {
                    // Charger les variables d'environnement
                    loadEnv()
                    
                    // Vérifier les dépendances
                    sh '''
                        docker --version
                        kubectl version --client
                        helm version
                    '''
                }
            }
        }
        
        stage('Build des images') {
            parallel {
                stage('Build App1') {
                    steps {
                        sh 'docker build -t ${REGISTRY}/app1:${BUILD_NUMBER} -t ${REGISTRY}/app1:latest ./app1'
                    }
                }
                stage('Build App2') {
                    steps {
                        sh 'docker build -t ${REGISTRY}/app2:${BUILD_NUMBER} -t ${REGISTRY}/app2:latest ./app2'
                    }
                }
            }
        }
        
        stage('Tests') {
            steps {
                script {
                    // Exécuter les tests unitaires
                    sh 'cd app1 && python -m pytest tests/'
                    sh 'cd app2 && python -m pytest tests/'
                }
            }
            post {
                always {
                    junit '**/test-reports/*.xml'
                }
            }
        }
        
        stage('Publication des images') {
            steps {
                script {
                    // Se connecter au registre
                    sh "echo '${DOCKER_CREDENTIALS_PSW}' | docker login -u '${DOCKER_CREDENTIALS_USR}' --password-stdin ${REGISTRY}"
                    
                    // Pousser les images
                    sh 'docker push ${REGISTRY}/app1:${BUILD_NUMBER}'
                    sh 'docker push ${REGISTRY}/app1:latest'
                    sh 'docker push ${REGISTRY}/app2:${BUILD_NUMBER}'
                    sh 'docker push ${REGISTRY}/app2:latest'
                }
            }
        }
        
        stage('Déploiement sur Kubernetes') {
            steps {
                script {
                    // Configurer kubectl
                    writeFile file: "${env.HOME}/.kube/config", text: "${KUBE_CONFIG}"
                    
                    // Mettre à jour les images dans les fichiers de déploiement
                    sh """
                        sed -i 's|image: ${REGISTRY}/app1:.*|image: ${REGISTRY}/app1:${BUILD_NUMBER}|g' charts/app1-deployment.yaml
                        sed -i 's|image: ${REGISTRY}/app2:.*|image: ${REGISTRY}/app2:${BUILD_NUMBER}|g' charts/app2-deployment.yaml
                    """
                    
                    // Appliquer les configurations Kubernetes
                    sh 'kubectl apply -f charts/fastline-namespace.yaml'
                    sh 'kubectl apply -f charts/db-claim0-persistentvolumeclaim.yaml'
                    sh 'kubectl apply -f charts/db-deployment.yaml'
                    sh 'kubectl apply -f charts/db-service.yaml'
                    sh 'kubectl apply -f charts/app1-deployment.yaml'
                    sh 'kubectl apply -f charts/app1-service.yaml'
                    sh 'kubectl apply -f charts/app2-deployment.yaml'
                    sh 'kubectl apply -f charts/app2-service.yaml'
                    
                    // Déployer l'ingress
                    sh 'kubectl apply -f charts/ingress.yaml'
                    
                    // Vérifier le statut des déploiements
                    sh 'kubectl get pods -n fastline'
                }
            }
        }
        
        stage('Tests d\'intégration') {
            steps {
                script {
                    // Attendre que les services soient prêts
                    sh '''
                        kubectl wait --for=condition=available --timeout=300s deployment/app1 -n fastline
                        kubectl wait --for=condition=available --timeout=300s deployment/app2 -n fastline
                    '''
                    
                    // Exécuter des tests d'intégration
                    // Remplacez par vos commandes de test d'intégration
                    echo 'Exécution des tests d\'intégration...'
                }
            }
        }
    }
    
    post {
        success {
            echo 'Déploiement réussi!'
            // Notification de succès
            slackSend channel: '#deployments',
                     color: 'good',
                     message: "Déploiement réussi: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}"
        }
        failure {
            echo 'Échec du déploiement!'
            // Notification d'échec
            slackSend channel: '#deployments',
                     color: 'danger',
                     message: "Échec du déploiement: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}"
        }
        always {
            // Nettoyage
            sh 'docker logout ${REGISTRY}'
            // Archivage des artefacts si nécessaire
            archiveArtifacts artifacts: '**/target/*.jar', allowEmptyArchive: true
        }
    }
}

// Fonction utilitaire pour charger les variables d'environnement
def loadEnv() {
    def envFile = readFile(env.ENV_FILE)
    envFile.split('\n').each { line ->
        if (line.trim() && !line.startsWith('#')) {
            def (key, value) = line.split('=', 2)
            if (key && value) {
                env[key.trim()] = value.trim().replaceAll('^"|"$', '')
            }
        }
    }
}
