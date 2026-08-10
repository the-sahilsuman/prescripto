from bson import ObjectId


def serialize(doc):
    """Recursively convert ObjectId and other non-JSON-serializable BSON types
    to strings so FastAPI can return them as JSON."""
    if isinstance(doc, list):
        return [serialize(item) for item in doc]
    if isinstance(doc, dict):
        return {key: serialize(value) for key, value in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc
