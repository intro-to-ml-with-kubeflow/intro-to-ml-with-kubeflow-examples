import ibm_boto3
from ibm_botocore.client import Config


BUCKET_NAME='demo-bucket123'
# Constants for IBM COS values
COS_ENDPOINT = 'https://s3.us-east.cloud-object-storage.appdomain.cloud'  ## This has to match s COS_BUCKET_LOCATION
COS_API_KEY_ID = "DISJY3dwqhCYi8ZiKxQMdo28lbRBqsYG9F0ASAR0IgjB"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/1e27724d6a7feea015054bfe32fb52f5:39a172fc-d755-48b8-a24c-604c7c353df4::"
COS_BUCKET_LOCATION = "us-east"  ## This has to match w COS_ENDPOINT

# Create resource
cos = ibm_boto3.resource("s3",
                         ibm_api_key_id=COS_API_KEY_ID,
                         ibm_service_instance_id=COS_RESOURCE_CRN,
                         ibm_auth_endpoint=COS_AUTH_ENDPOINT,
                         config=Config(signature_version="oauth"),
                         endpoint_url=COS_ENDPOINT
                         )

part_size = 1024 * 1024 * 5

# set threadhold to 15 MB
file_threshold = 1024 * 1024 * 15

# set the transfer threshold and chunk size
transfer_config = ibm_boto3.s3.transfer.TransferConfig(
    multipart_threshold=file_threshold,
    multipart_chunksize=part_size
)

# the upload_fileobj method will automatically execute a multi-part upload
# in 5 MB chunks for all files over 15 MB
with open("/data/sk.pkl", "rb") as file_data:
    cos.Object(BUCKET_NAME, "foo.txt").upload_fileobj(
        Fileobj=file_data,
        Config=transfer_config
    )