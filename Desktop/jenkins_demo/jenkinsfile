pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Downloading source code from GitHub...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building Jenkins Welcome Website...'

                bat '''
                    if not exist index.html (
                        echo ERROR: index.html not found
                        exit /b 1
                    )
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Testing HTML file...'

                script {
                    if (!fileExists('index.html')) {
                        error('HTML file is missing!')
                    }

                    echo 'HTML file test passed!'
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying website to Windows laptop...'

                bat '''
                    if not exist C:\\JenkinsWebsite mkdir C:\\JenkinsWebsite
                    copy /Y index.html C:\\JenkinsWebsite\\index.html
                '''
            }
        }

        stage('Success') {
            steps {
                echo '================================'
                echo 'JENKINS DEPLOYMENT SUCCESSFUL!'
                echo '================================'
                echo 'Website deployed successfully!'
                echo 'Open: http://localhost:8085'
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check the console output.'
        }
    }
}