pipeline {
    agent { node { label ''; customWorkspace '/c/jenkins-ws/campus-polling' } }
    options { timestamps() }
    triggers { githubPush() }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Syntax Check') {
            steps {
                sh 'python3 -m py_compile backend/app.py'
                sh 'docker compose config -q'
            }
        }
        stage('Build Image') {
            steps { sh 'docker compose build' }
        }
        stage('Automated Deployment') {
            steps { sh 'docker compose up -d --remove-orphans' }
        }
        stage('Health Check') {
            steps {
                sh '''
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                      if docker compose exec -T frontend wget -qO- http://localhost/api/votes > /dev/null 2>&1; then
                        echo "Health check OK (Nginx -> Backend)"; exit 0
                      fi
                      echo "Menunggu service siap ($i/10)..."; sleep 3
                    done
                    echo "Health check GAGAL"; docker compose logs --tail=50; exit 1
                '''
            }
        }
    }
    post {
        success { echo 'Deploy sukses: http://localhost:8080' }
        failure { echo 'Pipeline gagal, cek console output.' }
    }
}
