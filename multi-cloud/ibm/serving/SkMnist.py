from sklearn.externals import joblib
import ibm_boto3
from ibm_botocore.client import Config

BUCKET_NAME=""
ITEM_NAME="sk.pkl"
COS_ENDPOINT = 'https://s3.us-east.cloud-object-storage.appdomain.cloud'  ## This has to match s COS_BUCKET_LOCATION
COS_API_KEY_ID = "DISJY3dwqhCYi8ZiKxQMdo28lbRBqsYG9F0ASAR0IgjB"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/1e27724d6a7feea015054bfe32fb52f5:39a172fc-d755-48b8-a24c-604c7c353df4::"
COS_BUCKET_LOCATION = "us-east"  ## This has to match w COS_ENDPOINT


class SkMnist(object):
    def __init__(self):
        self.class_names = ["class:{}".format(str(i)) for i in range(10)]
        cos = ibm_boto3.resource("s3",
                                 ibm_api_key_id=COS_API_KEY_ID,
                                 ibm_service_instance_id=COS_RESOURCE_CRN,
                                 ibm_auth_endpoint=COS_AUTH_ENDPOINT,
                                 config=Config(signature_version="oauth"),
                                 endpoint_url=COS_ENDPOINT
                                 )

        file = cos.Object(BUCKET_NAME, ITEM_NAME).get()
        f = open('/sk.pkl', 'wb')
        f.write(file['Body'].read())
        self.clf = joblib.load('./sk.pkl')


    def predict(self,X,feature_names):
        predictions = self.clf.predict_proba(X)
        return predictions