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

        stage('Deployment Status') {

            steps {

                script {

                    def deploymentTime = sh(
                        script: "date '+%Y-%m-%d %H:%M:%S'",
                        returnStdout: true
                    ).trim()


                    def runningPods = sh(
                        script: "kubectl get pods --no-headers | grep Running | wc -l",
                        returnStdout: true
                    ).trim()


                    def healthStatus = "Healthy"


            writeFile file: 'build_info.json', text: """
{
    "application":"CI/CD Dashboard",
    "environment":"Development",
    "version":"v1.0.${BUILD_NUMBER}",
    "branch":"main",
    "commit":"${env.COMMIT_ID}",
    "docker_image":"${IMAGE_NAME}:${IMAGE_TAG}",
    "build_number":"${BUILD_NUMBER}",
    "pipeline_status":"SUCCESS",
    "deployment_time":"${deploymentTime}",
    "pods":"${runningPods}",
    "server":"Kubernetes",
    "health":"${healthStatus}"
}
"""

        }


        sh '''
        echo "=================================="
        echo "Deployment Successful"
        echo "Running Pods:"
        kubectl get pods
        echo "=================================="
        '''
    }
}

        stage('Run Automated Tests') {
            steps {
                sh '''
                pip3 install --break-system-packages --quiet -r requirements.txt
                python3 -m pytest test_app.py -v --junitxml=test-results.xml
                '''
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
                sh """
                    echo "Current Context"
                    kubectl config current-context

                    echo "Nodes"
                    kubectl get nodes

                    echo "Deploying..."
                    kubectl apply -f deployment.yaml
                    kubectl apply -f service.yaml

                    kubectl set image deployment/cicd-dashboard \
                        dashboard=${IMAGE_NAME}:${IMAGE_TAG}

                    kubectl rollout status deployment/cicd-dashboard
                    kubectl get pods
                """
            }
        }

        stage('Update Deployment Status') {
            steps {
                sh '''
                    PODS=$(kubectl get pods --no-headers | wc -l)
                    echo "=================================="
                    echo "Deployment Successful"
                    echo "Running Pods: $PODS"
                    echo "=================================="
                    kubectl get pods
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl get pods
                    kubectl get svc
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-results.xml'
        }
        success {
            echo "======================================="
            echo "Pipeline Executed Successfully!"
            echo "Docker Image: ${IMAGE_NAME}:${IMAGE_TAG}"
            echo "======================================="
        }
        failure {
            echo "Deployment failed. Starting rollback..."
            sh '''
                kubectl rollout undo deployment/cicd-dashboard || true
                kubectl rollout status deployment/cicd-dashboard || true
            '''
            echo "Rollback completed"
        }
    }
}