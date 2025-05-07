import uuid

def get_bidding_id(date: str) -> str:
    return "BID-" + date + "_" + str(uuid.uuid4())
