# source: https://github.com/aws/amazon-sagemaker-examples/blob/c7320a15c510c79ae0550ed8702e3fd88e0732ca/sagemaker-python-sdk/scikit_learn_randomforest/Sklearn_on_SageMaker_end2end.ipynb

# launching a training with boto3
# boto3 is more verbose yet gives more visibility in the low-level details of Amazon SageMaker

# first compress the code and send to S3

import boto3

source = "source.tar.gz"
project = "scikitlearn-train-from-boto3"

tar = tarfile.open(source, "w:gz")
tar.add("script.py")
tar.close()

s3 = boto3.client("s3")
s3.upload_file(source, bucket, project + "/" + source)

# %%

# When using boto3 to launch a training job we must explicitly point to a docker image.

from sagemaker import image_uris

training_image = image_uris.retrieve(
    framework="sklearn",
    region=region,
    version=FRAMEWORK_VERSION,
    py_version="py3",
    instance_type="ml.c5.xlarge",
)
print(training_image)

# %%

# launch training job

import boto3
import datetime

sm_boto3 = boto3.client('sagemaker')

response = sm_boto3.create_training_job(
    TrainingJobName="sklearn-boto3-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
    HyperParameters={
        "n_estimators": "300",
        "min_samples_leaf": "3",
        "sagemaker_program": "script.py",
        "features": "MedInc HouseAge AveRooms AveBedrms Population AveOccup Latitude Longitude",
        "target": "target",
        "sagemaker_submit_directory": "s3://" + bucket + "/" + project + "/" + source,
    },
    AlgorithmSpecification={
        "TrainingImage": training_image,
        "TrainingInputMode": "File",
        "MetricDefinitions": [
            {"Name": "median-AE", "Regex": "AE-at-50th-percentile: ([0-9.]+).*$"},
        ],
    },
    RoleArn=get_execution_role(),
    InputDataConfig=[
        {
            "ChannelName": "train",
            "DataSource": {
                "S3DataSource": {
                    "S3DataType": "S3Prefix",
                    "S3Uri": trainpath,
                    "S3DataDistributionType": "FullyReplicated",
                }
            },
        },
        {
            "ChannelName": "test",
            "DataSource": {
                "S3DataSource": {
                    "S3DataType": "S3Prefix",
                    "S3Uri": testpath,
                    "S3DataDistributionType": "FullyReplicated",
                }
            },
        },
    ],
    OutputDataConfig={"S3OutputPath": "s3://" + bucket + "/sagemaker-sklearn-artifact/"},
    ResourceConfig={"InstanceType": "ml.c5.xlarge", "InstanceCount": 1, "VolumeSizeInGB": 10},
    StoppingCondition={"MaxRuntimeInSeconds": 86400},
    EnableNetworkIsolation=False,
)

print(response)


# TODO: adjust logic for training
# TODO: Factor this into several script. Step Function orchestrator.
# TODO: register model with [registry](https://github.com/aws/amazon-sagemaker-examples/blob/c7320a15c510c79ae0550ed8702e3fd88e0732ca/sagemaker-python-sdk/scikit_learn_model_registry_batch_transform/scikit_learn_model_registry_batch_transform.ipynb)
