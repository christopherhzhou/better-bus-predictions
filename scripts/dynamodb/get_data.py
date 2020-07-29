import boto3


def get_data(trip_id, route_id, direction_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('rte-{}-d{}'.format(route_id, direction_id))

    response = table.get_item(
            Key={
                'tripId': trip_id
            }
        )

    print(response["Item"])