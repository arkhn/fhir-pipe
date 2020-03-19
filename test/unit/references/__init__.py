import mongomock


mock_mongo_client = mongomock.MongoClient()

database = mock_mongo_client.get_database("fhirstore")
database.create_collection("Patient")
database.create_collection("HealthcareService")

id_example_pat_1 = "123456"
id_example_pat_2 = "654321"

database["Patient"].insert_many(
    [
        {
            "_id": "987654321",
            "id": id_example_pat_1,
            "resourceType": "Patient",
            "identifier": [{"system": "system", "value": "0001"}],
            "generalPractitioner": [
                {"identifier": {"value": "12345"}, "type": "HealthcareService"}
            ],
        },
        {
            "_id": "123456789",
            "id": id_example_pat_2,
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
