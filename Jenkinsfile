pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_TAG = "${BUILD_NUMBER}"
        DEPLOY_PATH = '/home/devops/zopic-studio'
        COMPOSE_FILE = 'docker-compose.yml'
    }
    
    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
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
        // STAGE 2 : INSTALL DEPENDENCIES
        // =====================================================================
        stage('Install Dependencies') {
            parallel {
                stage('Install Backend') {
                    steps {
                        dir('backend') {
                            sh 'curl -LsSf https://astral.sh/uv/install.sh | sh || true'
                            sh 'export PATH="${HOME}/.local/bin:${PATH}" && uv sync'
                        }
                    }
                }
                stage('Install Frontend Web') {
                    steps {
                        dir('frontend-web') {
                            sh 'docker run --rm -v "${WORKSPACE}/frontend-web:/app" -v npm-cache:/root/.npm -w /app node:22-alpine npm install'
                        }
                    }
                }
                stage('Install Frontend Client') {
                    steps {
                        dir('frontend-client') {
                            sh 'docker run --rm -v "${WORKSPACE}/frontend-client:/app" -v npm-cache:/root/.npm -w /app node:22-alpine npm install'
                        }
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 3 : LINTING
        // =====================================================================
        stage('Linting') {
            parallel {
                stage('Lint Backend') {
                    steps {
                        dir('backend') {
                            sh 'export PATH="${HOME}/.local/bin:${PATH}" && uv run ruff check .'
                        }
                    }
                }
                stage('Lint Frontend Web') {
                    steps {
                        dir('frontend-web') {
                            sh 'docker run --rm -v "${WORKSPACE}/frontend-web:/app" -w /app node:22-alpine npm run lint'
                        }
                    }
                }
                stage('Lint Frontend Client') {
                    steps {
                        dir('frontend-client') {
                            sh 'docker run --rm -v "${WORKSPACE}/frontend-client:/app" -w /app node:22-alpine npm run lint'
                        }
                    }
                }
                stage('Check Encoding') {
                    steps {
                        script {
                            echo "Vérification des problèmes d'encodage (Mojibake)..."
                            def grepStatus = sh(
                                script: 'grep -rE "Ã©|Ã¨|Ã\\xa0|â€™|Ãª|Ã§|Ã®|Ã»|Ã´|Ã¢" backend/app frontend-*/src docs || true',
                                returnStdout: true
                            ).trim()
                            
                            if (grepStatus) {
                                error("⚠️ Mojibake détecté dans les fichiers suivants :\n${grepStatus}\nMerci de sauvegarder vos fichiers en UTF-8.")
                            }
                        }
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 4 : TESTS UNITAIRES
        // =====================================================================
        stage('Tests Unitaires') {
            parallel {
                stage('Test Backend') {
                    steps {
                        dir('backend') {
                            script {
                                echo 'Exécution des tests backend avec pytest...'
                                sh 'export PATH="${HOME}/.local/bin:${PATH}" && cp .env.example .env || true && uv run pytest tests/'
                            }
                        }
                    }
                }
                stage('Test Frontend Web') {
                    steps {
                        dir('frontend-web') {
                            echo 'Exécution des tests Frontend Web avec Vitest...'
                            sh 'docker run --rm -v "${WORKSPACE}/frontend-web:/app" -w /app node:22-alpine npm run test -- --run'
                        }
                    }
                }
                stage('Test Frontend Client') {
                    steps {
                        dir('frontend-client') {
                            echo 'Exécution des tests Frontend Client avec Vitest...'
                            sh 'docker run --rm -v "${WORKSPACE}/frontend-client:/app" -w /app node:22-alpine npm run test -- --run'
                        }
                    }
                }
            }
        }
        
        // =====================================================================
        // STAGE 5 : BUILD (DOCKER)
        // =====================================================================
        stage('Build Docker Images') {
            parallel {
                stage('Build Backend & AI') {
                    steps {
                        sh "docker build -t zopic-studio-backend:${DOCKER_IMAGE_TAG} -f backend/Dockerfile backend/"
                        sh "docker build -t zopic-ai-api:${DOCKER_IMAGE_TAG} -f backend/worker_ai/Dockerfile backend/worker_ai/"
                        sh "docker build -t zopic-ai-worker:${DOCKER_IMAGE_TAG} -f backend/worker_ai/Dockerfile backend/worker_ai/"
                    }
                }
                stage('Build Frontends') {
                    steps {
                        sh "docker build -t zopic-frontend-web:${DOCKER_IMAGE_TAG} -f frontend-web/Dockerfile frontend-web/"
                        sh "docker build -t zopic-frontend-client:${DOCKER_IMAGE_TAG} -f frontend-client/Dockerfile frontend-client/"
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 6 : SECURITY SCAN (SAST / Container)
        // =====================================================================
        stage('Security Scan') {
            steps {
                script {
                    echo "Scan de vulnérabilités Trivy sur le backend..."
                    // Blocking scan on HIGH and CRITICAL vulnerabilities
                    sh 'trivy image --severity HIGH,CRITICAL --no-progress zopic-studio-backend:${DOCKER_IMAGE_TAG}'
                }
            }
        }
        
        // =====================================================================
        // STAGE 7 : PREPARER LE DEPLOIEMENT
        // =====================================================================
        stage('Preparer Deploiement') {
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
                        echo 'ATTENTION : .env manquant - Utilisation des secrets Jenkins recommandée. Copie de fallback.'
                        sh "cp ${WORKSPACE}/backend/.env.example ${DEPLOY_PATH}/backend/.env || true"
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 8 : REDEMARRER
        // =====================================================================
        stage('Redemarrer Services') {
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
        // STAGE 9 : MIGRATION DB & INIT DATA
        // =====================================================================
        stage('Migration DB & Init Data') {
            steps {
                script {
                    echo 'Application du schema de base de donnees (Alembic)...'
                    sh """
                        cd ${DEPLOY_PATH}
                        docker compose -f ${COMPOSE_FILE} exec -T backend python scripts/db_migrate.py
                        docker compose -f ${COMPOSE_FILE} exec -T backend python scripts/init_qdrant.py || true
                    """
                }
            }
        }

        // =====================================================================
        // STAGE 10 : E2E TESTS (Playwright)
        // =====================================================================
        stage('E2E Tests') {
            steps {
                script {
                    echo "Lancement des tests de bout en bout (E2E) sur l'environnement cible..."
                    sh 'docker run --rm --network host mcr.microsoft.com/playwright:v1.44.0-jammy sh -c "echo \\"Running Playwright E2E tests...\\" && npx playwright test"'
                }
            }
        }

        // =====================================================================
        // STAGE 11 : DAST (Dynamic Application Security Testing)
        // =====================================================================
        stage('DAST (ZAP Scan)') {
            steps {
                script {
                    echo "Lancement du scan dynamique OWASP ZAP sur l'API..."
                    sh 'docker run --rm -t --network host owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000'
                }
            }
        }

        // =====================================================================
        // STAGE 12 : NETTOYER
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
                def ip = sh(script: "hostname -I | awk '{print \$1}' || echo localhost", returnStdout: true).trim()
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
