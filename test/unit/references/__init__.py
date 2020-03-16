import mongomock


mock_mongo_client = mongomock.MongoClient()

database = mock_mongo_client.get_database("fhirstore")
database.create_collection("Patient")
database.create_collection("HealthcareService")

database["Patient"].insert_many(
    [
        {
            "_id": "987654321",
            "id": "123456",
            "resourceType": "Patient",
            "identifier": [{"system": "system", "value": "0001"}],
            "generalPractitioner": [
                {"identifier": {"value": "12345"}, "type": "HealthcareService"}
            ],
        },
        {
            "_id": "123456789",
            "id": "654321",
            "resourceType": "Patient",
            "identifier": [{"system": "system", "value": "0002"}],
            "generalPractitioner": [
                {"type": "Practitioner", "identifier": {"system": "sys", "value": "9467"}}
            ],
        },
    ]
)


database["HealthcareService"].insert_one(
    {
        "_id": "123456789",
        "id": "654321",
        "resourceType": "HealthcareService",
        "identifier": [{"value": "12345"}],
    }
)
