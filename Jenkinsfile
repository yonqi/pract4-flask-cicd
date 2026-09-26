pipeline {
    agent any

    environment {
        REGISTRY = 'localhost:5000'
        IMAGE_NAME = 'flask-cicd-demo'
        IMAGE = "${REGISTRY}/${IMAGE_NAME}"
        VERSION = '1.0.0'

        STAGING_CONTAINER = 'flask-staging'
        STAGING_NETWORK = 'pract4-staging'
        STAGING_PORT = '8081'

        PROD_CONTAINER = 'flask-prod'
        PROD_NETWORK = 'pract4-prod'
        PROD_PORT = '8082'
    }

    stages {

        stage('1. Checkout') {
            steps {
                checkout scm

                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Commit: ${env.GIT_COMMIT_SHORT}"
                    echo "Build: ${env.BUILD_NUMBER}"
                }

                sh 'docker version'
            }
        }

        stage('2. Build Image') {
            steps {
                sh """
                    docker build \
                        --target runtime \
                        --build-arg APP_VERSION=${VERSION} \
                        --build-arg BUILD_NUMBER=${BUILD_NUMBER} \
                        --build-arg GIT_COMMIT=${GIT_COMMIT_SHORT} \
                        -t ${IMAGE}:${BUILD_NUMBER} \
                        -t ${IMAGE}:latest \
                        .
                """
            }
        }

        stage('3. Unit Tests') {
            steps {
                sh """
                    docker build \
                        --target test \
                        -t ${IMAGE}:test-${BUILD_NUMBER} \
                        .

                    docker run --rm \
                        ${IMAGE}:test-${BUILD_NUMBER} \
                        pytest -q
                """
            }
        }

        stage('4. Smoke Test') {
            steps {
                sh """
                    docker rm -f flask-smoke 2>/dev/null || true

                    docker run -d \
                        --name flask-smoke \
                        -p 8090:5000 \
                        -e APP_ENV=smoke \
                        -e APP_VERSION=${VERSION} \
                        -e BUILD_NUMBER=${BUILD_NUMBER} \
                        -e GIT_COMMIT=${GIT_COMMIT_SHORT} \
                        ${IMAGE}:${BUILD_NUMBER}

                    sleep 5

                    curl -f http://localhost:8090/health

                    docker rm -f flask-smoke
                """
            }
        }

        stage('5. Push to Registry') {
            steps {
                sh """
                    docker push ${IMAGE}:${BUILD_NUMBER}
                    docker push ${IMAGE}:latest
                """

                sh """
                    curl -f http://localhost:5000/v2/${IMAGE_NAME}/tags/list
                """
            }
        }

        stage('6. Deploy to Staging') {
            steps {
                sh """
                    docker network inspect ${STAGING_NETWORK} >/dev/null 2>&1 || \
                        docker network create ${STAGING_NETWORK}

                    docker rm -f ${STAGING_CONTAINER} 2>/dev/null || true

                    docker pull ${IMAGE}:${BUILD_NUMBER}

                    docker run -d \
                        --name ${STAGING_CONTAINER} \
                        --network ${STAGING_NETWORK} \
                        -p ${STAGING_PORT}:5000 \
                        -e APP_ENV=staging \
                        -e APP_VERSION=${VERSION} \
                        -e BUILD_NUMBER=${BUILD_NUMBER} \
                        -e GIT_COMMIT=${GIT_COMMIT_SHORT} \
                        ${IMAGE}:${BUILD_NUMBER}
                """
            }
        }

        stage('7. Verify Staging') {
            steps {
                sh """
                    sleep 3

                    curl -f http://localhost:${STAGING_PORT}/health
                    curl -f http://localhost:${STAGING_PORT}/env
                """
            }
        }

        stage('8. Approval for Production') {
            steps {
                script {
                    def approval = input(
                        message: 'Развернуть текущую сборку в production?',
                        ok: 'Deploy to Production',
                        submitterParameter: 'APPROVED_BY'
                    )

                    env.APPROVED_BY = approval
                    echo "Production approved by: ${env.APPROVED_BY}"
                }
            }
        }

        stage('9. Deploy to Production') {
            steps {
                sh """
                    docker network inspect ${PROD_NETWORK} >/dev/null 2>&1 || \
                        docker network create ${PROD_NETWORK}

                    docker rm -f ${PROD_CONTAINER} 2>/dev/null || true

                    docker pull ${IMAGE}:${BUILD_NUMBER}

                    docker run -d \
                        --name ${PROD_CONTAINER} \
                        --network ${PROD_NETWORK} \
                        -p ${PROD_PORT}:5000 \
                        -e APP_ENV=production \
                        -e APP_VERSION=${VERSION} \
                        -e BUILD_NUMBER=${BUILD_NUMBER} \
                        -e GIT_COMMIT=${GIT_COMMIT_SHORT} \
                        ${IMAGE}:${BUILD_NUMBER}
                """
            }
        }

        stage('10. Verify Production') {
            steps {
                sh """
                    sleep 3

                    curl -f http://localhost:${PROD_PORT}/health
                    curl -f http://localhost:${PROD_PORT}/env
                """
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f flask-smoke 2>/dev/null || true
                docker ps -a
            '''
        }

        success {
            echo 'Jenkins Pipeline успешно завершён.'
            echo "Staging: http://localhost:${STAGING_PORT}/"
            echo "Production: http://localhost:${PROD_PORT}/"
        }

        failure {
            echo 'Jenkins Pipeline завершён с ошибкой.'
        }
    }
}
