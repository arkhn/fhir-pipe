import mongomock


mock_mongo_client = mongomock.MongoClient()

database = mock_mongo_client.get_database("fhirstore")
database.create_collection("Patient")
database.create_collection("HealthcareService")
