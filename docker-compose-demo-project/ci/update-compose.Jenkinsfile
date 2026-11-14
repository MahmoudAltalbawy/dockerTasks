pipeline {
  agent any

  options { disableConcurrentBuilds() }

  parameters {
    string(name: 'SERVICE',   defaultValue: '', description: 'e.g. wave-frontend')
    string(name: 'IMAGE_TAG', defaultValue: '', description: 'e.g. 15')
  }

  environment {
    GIT_CREDS    = credentials('github')
    COMPOSE_FILE = 'docker-compose-demo-project/docker-compose.yml'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Update compose tag') {
      steps {
        sh '''
          BRANCH=${GIT_BRANCH#origin/}

          git config user.email "jenkins@ci.local"
          git config user.name  "Jenkins"
          git fetch origin $BRANCH
          git checkout -B $BRANCH origin/$BRANCH

          sed -i "s|\\(image: .*/$SERVICE:\\).*|\\1$IMAGE_TAG|" $COMPOSE_FILE

          git add $COMPOSE_FILE
          git diff --cached --quiet && echo "No change" && exit 0
          git commit -m "ci: update $SERVICE image tag to $IMAGE_TAG"

          REPO_HOST=$(git config --get remote.origin.url | sed 's|https://||')
          git push https://$GIT_CREDS_USR:$GIT_CREDS_PSW@$REPO_HOST HEAD:$BRANCH
        '''
      }
    }
  }
}