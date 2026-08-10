pipeline {
    agent { label 'prescripto' }

    stages {
        stage("Installation") {
            steps {
                sh "sudo chmod +x install.sh"
                sh "./install.sh"
            }
        }
        stage('Clone Code') {
            steps {
                sh '''
                if [ -d "prescripto" ]; then
                    echo "Pulling latest code..."
                    git pull origin dev
                else
                    echo "Cloning repo..."
                    git clone -b dev https://github.com/the-sahilsuman/prescripto.git
                fi
                '''
            }
        }
        stage('Check Environment Files') {
            steps {
                sh '''
                cd prescripto
                for dir in backend frontend admin; do
                    if [ ! -f "$dir/.env" ]; then
                        echo "ERROR: $dir/.env missing!"
                        exit 1
                    fi
                done
                '''
            }
        }
        stage('Build and Run Docker Image') {
            steps {
                sh '''
                cd prescripto
                docker-compose down --rmi all -v
                docker system prune -f
                docker-compose build --no-cache
                docker-compose up -d
                docker-compose ps
                echo "Deployment completed successfully!"
                echo "frontend:- user.thesahilsuman.online"
                echo "admin:- admin.thesahilsuman.online"
                '''
            }
        }
        stage("Reverse proxy & ssl setup") {
            steps {
                sh '''
                cd prescripto
                sudo chmod +x deploy.sh
                ./deploy.sh
                '''
            }
        }
    }
}
