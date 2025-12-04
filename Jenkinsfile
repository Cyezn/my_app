pipeline {
    agent any  // Runs on your Ubuntu agent

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-creds'  // Docker Hub credentials in Jenkins
        DOCKER_IMAGE = 'yourdockerhubusername/fastapi-jenkins-demo'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        KUBECONFIG_CRED = 'kubeconfig'             // Kubernetes config file in Jenkins
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    # Create Python virtual environment
                    python3 -m venv .venv

                    # Activate and install dependencies
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r app/requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pip install pytest pytest-asyncio httpx
                    pytest -q
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/*.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKERHUB_CREDENTIALS}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: "${KUBECONFIG_CRED}", variable: 'KUBECONFIG')]) {
                    sh '''
                        export KUBECONFIG=$KUBECONFIG
                        kubectl set image deployment/fastapi-demo web=${DOCKER_IMAGE}:${IMAGE_TAG} --record || true
                        kubectl apply -f kubernetes/deployment.yaml
                        kubectl apply -f kubernetes/service.yaml
                        kubectl
