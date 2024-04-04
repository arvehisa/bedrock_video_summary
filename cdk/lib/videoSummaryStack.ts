import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from "aws-cdk-lib/aws-iam";
import * as s3 from "aws-cdk-lib/aws-s3";
import { Construct } from 'constructs';
import { RemovalPolicy, aws_dynamodb, App, Stack, StackProps } from 'aws-cdk-lib';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import { AttributeType } from 'aws-cdk-lib/aws-dynamodb';
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as sfn from 'aws-cdk-lib/aws-stepfunctions'
import * as ecs_patterns from "aws-cdk-lib/aws-ecs-patterns";
import * as logs from "aws-cdk-lib/aws-logs";
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { Platform } from 'aws-cdk-lib/aws-ecr-assets';

type Props = cdk.StackProps & {
  ecr: ecr.Repository;
}

export class VideoSummaryStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: Props) {
    super(scope, id, props);
    
    const resourceName = "videosum"

    // ddb
    const dynamoDB = new aws_dynamodb.Table(this, 'TranscribeTable', {
      tableName: `${resourceName}-table`,
      partitionKey: { name: 'pk', type: AttributeType.STRING },
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // s3
    const videoInput = new s3.Bucket(this, 'videoInput', {
      bucketName: `${resourceName}-video-input`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const audioOutput = new s3.Bucket(this, 'audioOutput', {
      bucketName: `${resourceName}-audio-output`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const transcribeOutput = new s3.Bucket(this, 'transcribeOutput', {
      bucketName: `${resourceName}-transcribe-output`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // vpc, ecs, fagate
    const vpc = new ec2.Vpc(this, 'Vpc', {
      vpcName: `${resourceName}-vpc`,
      maxAzs: 2,
    });

    const cluster = new ecs.Cluster(this, "ecs-cluster", {
      clusterName: `${resourceName}-cluster`,
      vpc: vpc
    })

    const logGroup = new logs.LogGroup(this, "LogGroup", {
      logGroupName: `/aws/ecs/${resourceName}`,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const service = new ecs_patterns.ApplicationLoadBalancedFargateService(
      this,
      "fargate-service",{
        loadBalancerName: `${resourceName}-lb`,
        publicLoadBalancer: true,
        cluster: cluster,
        serviceName: `${resourceName}-service`,
        cpu: 256,
        desiredCount: 2,
        memoryLimitMiB: 512,
        assignPublicIp: true,
        taskSubnets: { subnetType: ec2.SubnetType.PUBLIC },
        taskImageOptions: {
          family: `${resourceName}-taskdef`,
          containerName: `${resourceName}-container`,
          image: ecs.ContainerImage.fromEcrRepository(props.ecr, "latest"),
          logDriver: new ecs.AwsLogDriver({
            streamPrefix: `container`,
            logGroup: logGroup,
          }),
        }
      }
    )

    // lambdas

    const lambdaRole = new iam.Role(this, 'LambdaExecutionRole', {
      roleName: `${resourceName}-lambda-role`,
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      description: 'Lambda Execution Role',
    })
    // とりあえず全部 Allow して後で絞る
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ['*'],
      resources: ['*'],
    }));

    const convertToAudio = new lambda.DockerImageFunction(this, 'convertToAudio', {
      functionName: `${resourceName}-convertToAudio`,
      code: lambda.DockerImageCode.fromImageAsset('../functions/convertToAudio',{ platform: Platform.LINUX_AMD64 }),
      timeout: cdk.Duration.seconds(300),
      memorySize: 256,
      architecture: lambda.Architecture.X86_64,
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
    });

    const stepFunctionsTrigger = new lambda.Function(this, 'stepFunctionsTrigger', {
      functionName: `${resourceName}-stepFunctionsTrigger`,
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('../functions/stepFunctionsTrigger'),
      timeout: cdk.Duration.seconds(300),
      memorySize: 256,
      architecture: lambda.Architecture.X86_64,
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
      handler: 'main.lambda_handler', 
    });
    
    const transcribeJob = new lambda.Function(this, 'transcribeJob', {
      functionName: `${resourceName}-transcribeJob`,
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('../functions/transcribeJob'),
      timeout: cdk.Duration.seconds(300),
      memorySize: 256,
      architecture: lambda.Architecture.X86_64,
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
      handler: 'main.lambda_handler', 
    });

    const checkJobStatusFormatting = new lambda.Function(this, 'checkJobStatusFormatting', {
      functionName: `${resourceName}-checkJobStatusFormatting`,
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('../functions/checkJobStatusFormatting'),
      timeout: cdk.Duration.seconds(300),
      memorySize: 256,
      architecture: lambda.Architecture.X86_64,
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
      handler: 'main.lambda_handler', 
    });

    const mainSummaryEnglish = new lambda.Function(this, 'mainSummaryEnglish', {
      functionName: `${resourceName}-mainSummaryEnglish`,
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('../functions/mainSummaryEnglish'),
      timeout: cdk.Duration.seconds(300),
      memorySize: 512,
      architecture: lambda.Architecture.X86_64,
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
      handler: 'main.lambda_handler', 
    });

    const mainSummaryTranslation = new lambda.Function(this, 'mainSummaryTranslation', {
      functionName: `${resourceName}-mainSummaryTranslation`,
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('../functions/mainSummaryTranslation'),
      timeout: cdk.Duration.seconds(300),
      memorySize: 256,
      architecture: lambda.Architecture.X86_64,
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
      handler: 'main.lambda_handler', 
    });

    const splitPartsSummary = new lambda.Function(this, 'splitPartsSummary', {
      functionName: `${resourceName}-splitPartsSummary`,
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('../functions/splitPartsSummary'),
      timeout: cdk.Duration.seconds(300),
      memorySize: 256,
      architecture: lambda.Architecture.X86_64,
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
      handler: 'main.lambda_handler', 
    });

    // step functions
    const stepFunctions = new sfn.StateMachine(this, 'StateMachineFromFile', {
      definitionBody: sfn.DefinitionBody.fromFile('../functions/sfn_placeholder.json', {}),
      stateMachineName: `${resourceName}-sfn`,
    });

    // triggers
    videoInput.addEventNotification(
      s3.EventType.OBJECT_CREATED_PUT, new s3n.LambdaDestination(convertToAudio)
    );

    audioOutput.addEventNotification(
      s3.EventType.OBJECT_CREATED_PUT, new s3n.LambdaDestination(stepFunctionsTrigger)
    );
  }
}
