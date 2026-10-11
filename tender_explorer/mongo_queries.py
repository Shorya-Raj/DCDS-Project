"""MongoDB CRUD and aggregation examples for the DCDS demonstration."""


def read_detail(collection, tender_key: str):
    return collection.find_one({"_id": tender_key})


def create_or_update_detail(collection, document: dict):
    """Create or update a document for a verified tender listing."""
    if "_id" not in document:
        raise ValueError("A document needs a stable _id")
    return collection.replace_one({"_id": document["_id"]}, document, upsert=True)


def update_eligibility(collection, tender_key: str, eligibility: dict):
    """Update only when eligibility was verified from an approved source."""
    return collection.update_one({"_id": tender_key}, {"$set": {"eligibility": eligibility}})


def delete_detail(collection, tender_key: str):
    """Delete a document by its stable tender key."""
    return collection.delete_one({"_id": tender_key})


def category_aggregation(collection):
    """Count documents for each listing category."""
    return list(collection.aggregate([
        {"$unwind": "$categories"},
        {"$group": {"_id": "$categories", "document_count": {"$sum": 1}}},
        {"$sort": {"document_count": -1, "_id": 1}},
    ]))
