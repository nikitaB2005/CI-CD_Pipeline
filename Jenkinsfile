pipeline {
    agent any

    stages {

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t cicd-dashboard:v1 .'
            }
        }

    }

    post {
        success {
            echo 'Docker image built successfully!'
        }

        failure {
            echo 'Docker image build failed!'
        }
    }
}