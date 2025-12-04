pipeline {
  agent any

  environment {
    DOCKERHUB_CREDENTIALS = 'dockerhub-creds'
    DOCKER_IMAGE = 'yourdockerhubusername/fastapi-jenkins-demo'
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    KUBECONFIG_CRED = 'kubeconfig'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python Env') {
      steps {
        sh """
          python3 -m venv .venv || true
          . .venv/bin/activate
          pip install -r app/requirements.txt
        """
      }
    }

    stage('Tests') {
      steps {
        sh """
          . .venv/bin/activate
          pip install pytest pytest-asyncio httpx
          pytest -q
        """
      }
      post {
        always { junit testResults: 'reports/*.xml', allowEmptyResults: true }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          dockerImage = docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}")
        }
      }
    }

    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: "${DOCKERHUB_CREDENTIALS}",
          usernameVariable: 'DOCKER_USER',
          passwordVariable: 'DOCKER_PASS'
        )]) {
          sh """
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
          """
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        withCredentials([file(credentialsId: "${KUBECONFIG_CRED}", variable: 'KUBECONFIG')]) {
          sh """
            export KUBECONFIG=$KUBECONFIG
            kubectl set image deployment/fastapi-demo web=${DOCKER_IMAGE}:${IMAGE_TAG} --record || true
            kubectl apply -f kubernetes/deployment.yaml
            kubectl apply -f kubernetes/service.yaml
            kubectl rollout status deployment/fastapi-demo --timeout=120s
          """
        }
      }
    }
  }

  post {
    success { echo "Deployment complete: ${DOCKER_IMAGE}:${IMAGE_TAG}" }
    failure { echo "Pipeline failed." }
  }
}
