// Jenkinsfile (Declarative)
pipeline {
  agent any

  environment {
    DOCKERHUB_CREDENTIALS = 'dockerhub-creds'      // Jenkins credential id (username/password)
    DOCKER_IMAGE = "yourdockerhubusername/fastapi-jenkins-demo"
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    KUBECONFIG_CRED = 'kubeconfig'                 // Jenkins secret text or file credential id
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Setup Python') {
      steps {
        sh 'python3 -m venv .venv || true'
        sh '. .venv/bin/activate && pip install -r app/requirements.txt'
      }
    }

    stage('Lint (optional)') {
      steps {
        // Add flake8/black if you want
        echo "Skipping lint for now"
      }
    }

    stage('Unit Tests') {
      steps {
        sh '''
          python3 -m venv .venv || true
          . .venv/bin/activate
          pip install pytest pytest-asyncio httpx
          pytest -q
        '''
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'reports/*.xml' // if you produce junit xml
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

    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
          '''
        }
      }
    }

    stage('Deploy to K8s') {
      steps {
        // Write kubeconfig cred to file and use kubectl
        withCredentials([file(credentialsId: "${KUBECONFIG_CRED}", variable: 'KUBECONFIG_FILE')]) {
          sh '''
            export KUBECONFIG=$KUBECONFIG_FILE
            # update image in deployment and apply
            kubectl set image deployment/fastapi-demo web=${DOCKER_IMAGE}:${IMAGE_TAG} --record || true
            kubectl apply -f kubernetes/deployment.yaml
            kubectl apply -f kubernetes/service.yaml
            kubectl rollout status deployment/fastapi-demo --timeout=120s
          '''
        }
      }
    }
  }

  post {
    success {
      echo "Pipeline completed successfully. Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
    }
    failure {
      echo "Pipeline failed."
    }
  }
}
