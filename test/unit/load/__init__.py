import mongomock


mock_mongo_client = mongomock.MongoClient()

database = mock_mongo_client.get_database("fhirstore")
database.create_collection("Patient")

database["Patient"].insert_one(
    {
        "_id": "987654321",
        "id": "123456",
        "resourceType": "Patient",
        "gender": "female",
        "address": [{"city": "Paris", "country": "France"}],
        "identifier": [{"system": "system", "value": "0001"}],
    }
)

