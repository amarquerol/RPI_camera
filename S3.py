import boto3
import uuid
import sys
from datetime import timedelta
from datetime import datetime
from PIL import Image
from boto.s3.connection import S3Connection

#AWS_KEY = 
#AWS_SECRET = 

# Per pujar fitxers des del disc dur
#def uploadFileToBucket(bucketName,fileToUpload):
#    s3 = boto3.resource('s3')
#    region = s3.meta.client.get_bucket_location(Bucket=bucketName)['LocationConstraint']
#    s3 = boto3.resource('s3',region_name=region)
#    s3.Object(bucketName, fileToUpload).put(Body=open(fileToUpload, 'rb'))

# Per pujar fitxers des de memoria
def uploadStreamToBucket(bucketName,filename,file_as_stream):
    client = boto3.client('s3')
    resp = client.put_object(Bucket= bucketName, Key= filename, Body= file_as_stream.getvalue())
    #print(resp)
    print "\nFoto pujada al S3.\n"

#def getFileNamesInBucket(AWS_KEY,AWS_SECRET):
#    aws_connection = S3Connection(AWS_KEY, AWS_SECRET)
#    bucket = aws_connection.get_bucket(bucketName)
#    for file_key in bucket.list():
#        print file_key.name

#def saveToFileLocal(bucketName,stringNom,item):
#        image_stream = io.BytesIO()
#        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some processing on it
#        image_stream.seek(0)
#        image = Image.open(item)
#        i = datetime.now()
#        nomADefinir = i.strftime('%Y_%m_%d__%H_%M_%S_%f')
#        customPath = "/home/pi/testN/"
#        comanda = customPath + nomADefinir + '.jpeg'
#        image.save(comanda)

############   NO HI HA MAIN   ############
