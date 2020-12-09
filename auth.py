import base64
import boto3
import string
import random
import re
from botocore.signers import RequestSigner

class EKSAuth(object):

    METHOD = 'GET'
    EXPIRES = 60
    EKS_HEADER = 'x-k8s-aws-id'
    EKS_PREFIX = 'k8s-aws-v1.'
    STS_URL = 'sts.amazonaws.com'
    STS_ACTION = 'Action=GetCallerIdentity&Version=2011-06-15'

    def __init__(self, cluster_id, region='us-east-1'):
        self.cluster_id = cluster_id
        self.region = region
    
    def get_token(self):
     
        session = boto3.session.Session()
        
        
        #Get ServiceID required by class RequestSigner
        client = session.client("sts",region_name=self.region)
        service_id = client.meta.service_model.service_id


        #An object to sign requests before they go out over the wire using one of the authentication mechanisms defined in auth.py
        signer = RequestSigner(
            service_id,
            session.region_name,
            'sts',
            'v4',
            session.get_credentials(),
            session.events
        )


        #creating the get request template 
        params = {
            'method': self.METHOD,
            'url': 'https://' + self.STS_URL + '/?' + self.STS_ACTION,
            'body': {},
            'headers': {
                self.EKS_HEADER: self.cluster_id
            },
            'context': {}
        }


        #Generates a presigned url
        signed_url = signer.generate_presigned_url(
            params,
            region_name=session.region_name,
            expires_in=self.EXPIRES,
            operation_name=''
        )
        
        
        #bearere token hash
        base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')
        
        
        #removed padding from beare token
        #return bearere token hash
        return self.EKS_PREFIX + re.sub(r'=*', '', base64_url)
       