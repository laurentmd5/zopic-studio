pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_TAG = "${BUILD_NUMBER}"
        DEPLOY_PATH = '/home/devops/zopic-studio'
        COMPOSE_FILE = 'docker-compose.yml'
    }
    
    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        
        // =====================================================================
        // STAGE 1 : CLONE
        // =====================================================================
        stage('Clone') {
            steps {
                echo 'Clonage du depot GitHub...'
                checkout scm
                script {
                    currentBuild.displayName = "#${BUILD_NUMBER} - ${GIT_COMMIT.take(8)}"
                }
            }
        }

        // =====================================================================
        // STAGE 2 : TESTS UNITAIRES (Backend)
        // =====================================================================
        stage('Tests Unitaires - Backend') {
            steps {
                dir('backend') {
                    script {
                        echo 'Exécution des tests backend avec pytest...'
                        sh 'curl -LsSf https://astral.sh/uv/install.sh | sh || true'
                        env.PATH = "${HOME}/.local/bin:${env.PATH}"
                        sh 'uv sync'
                        sh 'cp .env.example .env'
                        sh 'uv run pytest tests/'
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 3 : TESTS UNITAIRES (Frontend Web)
        // =====================================================================
        stage('Tests Unitaires - Frontend Web (Pro)') {
            steps {
                dir('frontend-web') {
                    script {
                        echo 'Exécution des tests Frontend Web avec Vitest...'
                        sh 'docker run --rm -v "${WORKSPACE}/frontend-web:/app" -w /app node:22-alpine sh -c "npm install && npm run test -- --run"'
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 4 : TESTS UNITAIRES (Frontend Client)
        // =====================================================================
        stage('Tests Unitaires - Frontend Client (PWA)') {
            steps {
                dir('frontend-client') {
                    script {
                        echo 'Exécution des tests Frontend Client avec Vitest...'
                        sh 'docker run --rm -v "${WORKSPACE}/frontend-client:/app" -w /app node:22-alpine sh -c "npm install && npm run test -- --run"'
                    }
                }
            }
        }
        
        // =====================================================================
        // STAGE 5 : BUILD (DOCKER)
        // =====================================================================
        stage('Build Docker Images') {
            steps {
                script {
                    echo "Construction Backend"
                    sh "docker build -t zopic-studio-backend:${DOCKER_IMAGE_TAG} -f backend/Dockerfile backend/"
                    
                    echo "Construction AI API"
                    sh "docker build -t zopic-ai-api:${DOCKER_IMAGE_TAG} -f backend/worker_ai/Dockerfile backend/worker_ai/"

                    echo "Construction AI Worker"
                    sh "docker build -t zopic-ai-worker:${DOCKER_IMAGE_TAG} -f backend/worker_ai/Dockerfile backend/worker_ai/"
                    
                    echo "Construction Frontend Web (Pro)"
                    sh "docker build -t zopic-frontend-web:${DOCKER_IMAGE_TAG} -f frontend-web/Dockerfile frontend-web/"
                    
                    echo "Construction Frontend Client (PWA)"
                    sh "docker build -t zopic-frontend-client:${DOCKER_IMAGE_TAG} -f frontend-client/Dockerfile frontend-client/"
                }
            }
        }
        
        // =====================================================================
        // STAGE 6 : PREPARER LE DEPLOIEMENT
        // =====================================================================
        stage('Preparer') {
            steps {
                script {
                    sh """
                        mkdir -p ${DEPLOY_PATH}/logs
                        mkdir -p ${DEPLOY_PATH}/scripts
                        mkdir -p ${DEPLOY_PATH}/backend

                        cp ${WORKSPACE}/${COMPOSE_FILE}              ${DEPLOY_PATH}/
                        cp ${WORKSPACE}/backend/scripts/init_qdrant.py       ${DEPLOY_PATH}/scripts/
                        cp ${WORKSPACE}/backend/scripts/db_migrate.py        ${DEPLOY_PATH}/scripts/
                    """

                    def envExists = sh(
                        script: "test -f ${DEPLOY_PATH}/backend/.env && echo yes || echo no",
                        returnStdout: true
                    ).trim()

                    if (envExists == 'no') {
                        echo 'ATTENTION : .env manquant - Copie de .env.example'
                        sh "cp ${WORKSPACE}/backend/.env.example ${DEPLOY_PATH}/backend/.env"
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 7 : REDEMARRER
        // =====================================================================
        stage('Redemarrer') {
            steps {
                sh """
                    cd ${DEPLOY_PATH}
                    export DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG}
                    docker compose -f ${COMPOSE_FILE} down --remove-orphans || true
                    docker compose -f ${COMPOSE_FILE} up -d --force-recreate
                """
                sleep(time: 20, unit: 'SECONDS')
            }
        }

        // =====================================================================
        // STAGE 8 : MIGRATION DB & INIT DATA
        // =====================================================================
        stage('Migration DB & Init Data') {
            steps {
                script {
                    echo 'Application du schema de base de donnees (Alembic)...'
                    sh """
                        cd ${DEPLOY_PATH}
                        docker compose -f ${COMPOSE_FILE} exec -T backend uv run python scripts/db_migrate.py
                        docker compose -f ${COMPOSE_FILE} exec -T backend uv run python scripts/init_qdrant.py || true
                    """
                }
            }
        }

        // =====================================================================
        // STAGE 9 : NETTOYER
        // =====================================================================
        stage('Nettoyer') {
            steps {
                sh 'docker image prune -f || true'
            }
        }
    }
    
    post {
        success {
            script {
                def ip = sh(script: "hostname -I | awk '{print \$1}'", returnStdout: true).trim()
                echo """
========================================
     DEPLOIEMENT COMPLET REUSSI !
========================================
  API Backend : http://${ip}:8000/health
  Dashboard   : http://${ip}:5173
  PWA Client  : http://${ip}:5174
========================================"""
            }
        }
        failure {
            sh "cd ${DEPLOY_PATH} && docker compose -f ${COMPOSE_FILE} logs --tail 30 || true"
        }
    }
}
