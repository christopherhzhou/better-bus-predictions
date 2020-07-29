import boto3


def post_data(data, route, direction):
    table_name = 'rte-{rte}-d{d}'.format(rte=route, d=direction)
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    response = table.put_item(Item=data)
        
    print('POST status:', response["ResponseMetadata"]["HTTPStatusCode"])
