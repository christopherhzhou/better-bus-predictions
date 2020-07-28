import boto3

__TableName__ = 'rte-34-d1'
Primary_Column_Name = 'tripId'
Primary_Key = '1'
columns = ['arriveDest', 'departOrigin']

dynamodb = boto3.resource('dynamodb')

DB = boto3.resource('dynamodb')
table = DB.Table(__TableName__)

response = table.get_item(
        Key={
            Primary_Column_Name: Primary_Key
        }
    )
    
print(response["Item"])