#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { VideoSummaryStack } from '../lib/videoSummaryStack';
import { EcrStack } from '../lib/ecrStack'

const app = new cdk.App();
const ecrStack = new EcrStack(app, 'EcrStack');

new VideoSummaryStack(app, 'VideoSummaryStack', {
    ecr: ecrStack.ecr,
});