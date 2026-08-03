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

        stage('Update Build Information') {

            steps {

                sh '''
                COMMIT_ID=$(git rev-parse --short HEAD)

                cat > build_info.json <<EOF
                {
                "application":"CI/CD Dashboard",
                "environment":"Development",
                "version":"v1.0.${BUILD_NUMBER}",
                "branch":"main",
                "commit":"${COMMIT_ID}",
                "docker_image":"${IMAGE_NAME}:${IMAGE_TAG}",
                "build_number":"${BUILD_NUMBER}",
                "pipeline_status":"BUILDING",
                "deployment_time":"Not Deployed",
                "pods":"0",
                "server":"Kubernetes",
                "health":"Healthy"
                }
                EOF
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

        withCredentials([
            file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
        ]) {

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
}
        stage('Update Deployment Status') {

            steps {

                sh '''
                PODS=$(kubectl get pods --no-headers | wc -l)

                python3 - <<EOF
                import json

                with open("build_info.json") as f:
                data=json.load(f)

                data["pipeline_status"]="SUCCESS"
                data["deployment_time"]="Deployed"
                data["pods"]="$PODS"

                with open("build_info.json","w") as f:
                json.dump(data,f,indent=4)

                EOF
                '''
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