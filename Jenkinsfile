pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_NAME = 'zopic-studio-backend'
        DOCKER_IMAGE_TAG = "${BUILD_NUMBER}"
        DEPLOY_PATH = '/home/devops/zopic-studio'
        COMPOSE_FILE = 'docker-compose.yml'
    }
    
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
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
        // STAGE 2 : TESTS UNITAIRES
        // =====================================================================
        stage('Tests Unitaires') {
            steps {
                script {
                    echo 'Exécution des tests unitaires mockés avant le build...'
                    // Installation ou mise à jour de uv (si non présent sur l'agent)
                    sh 'curl -LsSf https://astral.sh/uv/install.sh | sh || true'
                    env.PATH = "${HOME}/.local/bin:${env.PATH}"
                    sh 'uv sync'
                    sh 'cp .env.example .env'
                    sh 'uv run pytest tests/'
                }
            }
        }
        
        // =====================================================================
        // STAGE 3 : BUILD
        // =====================================================================
        stage('Build') {
            steps {
                script {
                    echo "Construction : ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} -f Dockerfile ."
                }
            }
        }
        
        // =====================================================================
        // STAGE 4 : PREPARER
        // =====================================================================
        stage('Preparer') {
            steps {
                script {
                    sh """
                        mkdir -p ${DEPLOY_PATH}/logs
                        mkdir -p ${DEPLOY_PATH}/scripts

                        cp ${WORKSPACE}/${COMPOSE_FILE}              ${DEPLOY_PATH}/
                        cp ${WORKSPACE}/scripts/init_qdrant.py       ${DEPLOY_PATH}/scripts/
                        cp ${WORKSPACE}/scripts/db_migrate.py        ${DEPLOY_PATH}/scripts/
                    """

                    def envExists = sh(
                        script: "test -f ${DEPLOY_PATH}/.env && echo yes || echo no",
                        returnStdout: true
                    ).trim()

                    if (envExists == 'no') {
                        echo 'ATTENTION : .env manquant - Creez-le sur la VM : nano /home/devops/zopic-studio/.env'
                        sh "cp ${WORKSPACE}/.env.example ${DEPLOY_PATH}/.env"
                    } else {
                        echo '.env conserve'
                    }
                }
            }
        }

        // =====================================================================
        // STAGE 5 : REDEMARRER
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
        // STAGE 6 : VERIFIER
        // =====================================================================
        stage('Verifier') {
            steps {
                script {
                    def ok = false
                    for (int i = 0; i < 20; i++) {
                        def status = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo 000",
                            returnStdout: true
                        ).trim()
                        if (status == '200') {
                            ok = true
                            echo "Service healthy (tentative ${i + 1})"
                            break
                        }
                        sleep(time: 3, unit: 'SECONDS')
                    }
                    if (!ok) error("Service non healthy apres 20 tentatives")
                }
            }
        }

        // =====================================================================
        // STAGE 7 : MIGRATION DB (hybrid create_all + alembic)
        // =====================================================================
        stage('Migration DB') {
            steps {
                script {
                    echo 'Application du schema de base de donnees (hybride create_all + Alembic)...'
                    sh """
                        cd ${DEPLOY_PATH}
                        docker compose -f ${COMPOSE_FILE} exec -T backend uv run python scripts/db_migrate.py
                    """
                    echo 'Schema OK'
                }
            }
        }

        // =====================================================================
        // STAGE 8 : INIT DATA
        // =====================================================================
        stage('Init Data') {
            steps {
                script {
                    // Initialiser Qdrant
                    sh """
                        cd ${DEPLOY_PATH}
                        docker compose -f ${COMPOSE_FILE} exec -T backend \
                            uv run python scripts/init_qdrant.py || true
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
     DEPLOIEMENT ZO PIC STUDIO REUSSI !
========================================
  API     : http://${ip}:8000/health
  Docs    : http://${ip}:8000/docs
========================================"""
            }
        }
        failure {
            sh "cd ${DEPLOY_PATH} && docker compose -f ${COMPOSE_FILE} logs --tail 30 || true"
        }
    }
}
