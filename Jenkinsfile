pipeline {
  agent any

  environment {
    AWS_DEFAULT_REGION = 'us-east-1'
    ECR_REPOSITORY = 's3-to-rds-glue-pipe' // MATCHES NEW NAME IN main.tf
    AWS_ACCOUNT_ID = '045045984465447'
  }
  stages {
      stage('clean workspace') {
          steps { cleanWs() }
      }
      stage('Git Checkout') {
          steps { git branch: 'main', url: 'https://github.com/GaniDynamo/Devops_Engineer_Assignment1-Rablo-.git' }
      }
// STAGE 1 (Terraform Part 1): Creates ECR, IAM, S3, RDS Subnet Group (Crucial dependencies for Docker push)
      stage('Terraform Init & Infra Creation') {
    steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credential-id']]) {
            script {
                sh '''
                    terraform init

                    echo "Running partial Terraform Apply, skipping Lambda function creation..."
                    # Targets ensure ECR and other prerequisites are created.
                    # The Lambda resource (aws_lambda_function.my_lambda) is intentionally skipped here.
                    terraform apply -auto-approve -target=aws_ecr_repository.repo -target=aws_iam_role.lambda_exec_role -target=aws_s3_bucket.data_bucket -target=aws_db_subnet_group.rds_subnet_group
                '''
            }
        }
    }
}
// STAGE 2: Authenticate (ECR Repository now exists in AWS)
      stage('Authenticate with AWS and ECR') {
    steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credential-id']]) {
            sh '''
                echo "Authenticating with AWS for ECR Login..."
                export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

                aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
                docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
            '''
        }
    }
}

// STAGE 3: Build & Push Image (The ECR Repository is ready)
      stage('Build, Tag & Push Docker Image') {
    steps {
        script {
            def IMAGE_TAG = "1.0.${currentBuild.number}"
            def ECR_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPOSITORY}"

            sh """
                echo "Building Docker image..."
                docker build -t s3-to-rds-glue:latest .

                echo "Tagging image with ${IMAGE_TAG} and latest..."
                docker tag s3-to-rds-glue:latest ${ECR_URI}:${IMAGE_TAG}
                docker tag s3-to-rds-glue:latest ${ECR_URI}:latest

                echo "Pushing images to ECR..."
                docker push ${ECR_URI}:${IMAGE_TAG}
                docker push ${ECR_URI}:latest
                sleep 10
            """
        }
    }
}

// STAGE 4 (Terraform Part 2): Create Lambda (Image is now available)
      stage('Final Terraform Apply & Lambda Deployment') {
    steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credential-id']]) {
            script {
                sh '''
                    echo "Running final Terraform Apply to deploy Lambda function..."
                    # This final apply will create the Lambda resource and complete the deployment.
                    terraform apply -auto-approve
                '''
            }
        }
    }
}

      }
  }
