pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.13'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    // Installation ou mise à jour de uv (si non présent sur l'agent)
                    sh 'curl -LsSf https://astral.sh/uv/install.sh | sh || true'
                    
                    // Ajout de uv au PATH local
                    env.PATH = "${HOME}/.local/bin:${env.PATH}"
                    
                    // Synchronisation des dépendances
                    sh 'uv venv'
                    sh 'uv sync'
                }
            }
        }

        stage('Tests Unitaires') {
            steps {
                script {
                    // Exécution des tests mockés
                    sh 'uv run pytest tests/ --junitxml=test-results.xml'
                }
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Déploiement sur VM Ubuntu') {
            steps {
                script {
                    // TODO: À configurer selon que Jenkins tourne SUR la VM ou se connecte en SSH
                    // Si Jenkins est sur la VM avec accès Docker :
                    // sh 'docker-compose up -d --build'
                    
                    echo "Déploiement en attente de la confirmation de l'architecture Jenkins/VM."
                }
            }
        }
    }
    
    post {
        success {
            echo "Pipeline exécuté avec succès ! 🎉"
        }
        failure {
            echo "Échec du pipeline. Veuillez vérifier les logs. ❌"
        }
    }
}
