pipeline {
    agent any
    stages {

        stage('Build') {
            steps {
                sh "sudo pip3 install -r requirements.txt"
            }
        }

        stage('Kill previous') {
            steps {
                sh "sudo killall gunicorn -q | echo 'no process found'"
            }
        }

        stage('Deploy') {
            steps {
                sh "sudo gunicorn -w 1 -k uvicorn.workers.UvicornWorker server:app --bind '0.0.0.0:8000' --daemon"
            }
        }

    }
}