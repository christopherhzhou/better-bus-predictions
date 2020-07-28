import boto3


def post_data(data):
    table_name = 'rte-{rte}-d{d}'.format(rte=data['route'],d=data['direction'])
    
    dynamodb = boto3.resource('dynamodb')
    
    DB = boto3.resource('dynamodb')
    table = DB.Table(table_name)
    
    data.pop('route')
    data.pop('direction')
    
    response = table.put_item(Item=data)
        
    print(response["ResponseMetadata"]["HTTPStatusCode"])