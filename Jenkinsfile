pipeline {

    agent any

    environment {
        IMAGE_NAME = "nikitabalwada/cicd-dashboard"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Source Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t cicd-dashboard:${IMAGE_TAG} ."
            }
        }

        stage('Tag Docker Image') {
            steps {
                sh "docker tag cicd-dashboard:${IMAGE_TAG} ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {

                    sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }

        stage('Deploy to Kubernetes') {

            steps {

                withCredentials([
                file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
            ]) {

                sh '''
                kubectl get nodes

                kubectl apply -f deployment.yaml

                kubectl apply -f service.yaml

                kubectl set image deployment/cicd-dashboard \
                cicd-dashboard=${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }
    }


        stage('Verify Deployment') {

            steps {

                withCredentials([
                file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
            ]) {

                sh '''
                kubectl get pods
                kubectl get svc
                '''
            }
        }
    }

    }

    post {

        success {
            echo "======================================="
            echo "Pipeline Executed Successfully!"
            echo "Docker Image: ${IMAGE_NAME}:${IMAGE_TAG}"
            echo "======================================="
        }

        failure {
            echo "======================================="
            echo "Pipeline Failed!"
            echo "Check Console Output."
            echo "======================================="
        }

    }

}