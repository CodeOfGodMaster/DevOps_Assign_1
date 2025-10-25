pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
  }

  environment {
    AWS_DEFAULT_REGION = 'us-east-1'
    ECR_REPOSITORY     = 's3-to-rds-glue-pipe'
    AWS_ACCOUNT_ID     = '045984465447'

    // derived (for clarity; used below but do not change behavior)
    ECR_REGISTRY       = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
    ECR_URI            = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
    LOCAL_IMAGE_NAME   = "s3-to-rds-glue"
  }

  stages {

    stage('clean workspace') {
      steps {
        echo '🧹 cleaning workspace...'
        cleanWs()
      }
    }

    stage('Git Checkout') {
      steps {
        echo '📥 git checkout (branch: main)'
        git branch: 'main', url: 'https://github.com/CodeOfGodMaster/DevOps-Assignment_1.git'
      }
    }

    // STAGE 1 (Terraform Part 1): Creates ECR, IAM, S3, RDS Subnet Group
    stage('Terraform Init & Infra Creation') {
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credential-id']]) {
          sh '''#!/usr/bin/env bash
            set -euxo pipefail

            echo "==> terraform init (non-interactive)"
            terraform init -input=false -no-color

            echo "==> validating toolchain"
            which aws
            which docker
            which terraform

            echo "==> targeted apply (ECR, IAM, S3, RDS subnet group) — Lambda intentionally skipped"
            terraform apply -auto-approve -input=false -no-color \
              -target=aws_ecr_repository.repo \
              -target=aws_iam_role.lambda_exec_role \
              -target=aws_s3_bucket.data_bucket \
              -target=aws_db_subnet_group.rds_subnet_group
          '''
        }
      }
    }

    // STAGE 2: Authenticate (ECR Repository now exists in AWS)
    stage('Authenticate with AWS and ECR') {
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credential-id']]) {
          sh '''#!/usr/bin/env bash
            set -euo pipefail
            echo "==> logging into ECR: ${ECR_REGISTRY}"
            aws ecr get-login-password --region "${AWS_DEFAULT_REGION}" | \
              docker login --username AWS --password-stdin "${ECR_REGISTRY}"
          '''
        }
      }
    }

    // STAGE 3: Build & Push Image (The ECR Repository is ready)
    stage('Build, Tag & Push Docker Image') {
      steps {
        script {
          def IMAGE_TAG = "1.0.${currentBuild.number}"

          sh """#!/usr/bin/env bash
            set -euxo pipefail

            echo "==> docker build"
            docker build --pull -t ${LOCAL_IMAGE_NAME}:latest .

            echo "==> docker tag -> ${ECR_URI}:${IMAGE_TAG} and ${ECR_URI}:latest"
            docker tag ${LOCAL_IMAGE_NAME}:latest ${ECR_URI}:${IMAGE_TAG}
            docker tag ${LOCAL_IMAGE_NAME}:latest ${ECR_URI}:latest

            echo "==> docker push"
            docker push ${ECR_URI}:${IMAGE_TAG}
            docker push ${ECR_URI}:latest

            echo "==> wait briefly for image to be discoverable by Lambda"
            sleep 8
          """
        }
      }
    }

    // STAGE 4 (Terraform Part 2): Create Lambda (Image is now available)
    stage('Final Terraform Apply & Lambda Deployment') {
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credential-id']]) {
          sh '''#!/usr/bin/env bash
            set -euxo pipefail

            echo "==> final terraform apply (creates/updates Lambda using ECR image)"
            terraform apply -auto-approve -input=false -no-color
          '''
        }
      }
    }
  }

  post {
    always {
      echo "Build result: ${currentBuild.currentResult}"
    }
  }
}
