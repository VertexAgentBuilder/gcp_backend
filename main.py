import functions_framework
import json
import time,os
import dotenv
from datetime import datetime, timedelta
from datetime import date
from pymongo import MongoClient
from werkzeug.wrappers import Response
from collections import defaultdict
import cohere
import qdrant_client
from qdrant_client import models, QdrantClient

dotenv.load_dotenv()

mongoUrl = os.getenv("MONGO_URL")
dbName = os.getenv("MONGO_DB")
sessionCollection = os.getenv("SESSION_COLLECTION")

client = MongoClient(mongoUrl)
collection = client[dbName][sessionCollection]

class ClientLogManager:
    def __init__(self, path):
        self.client_logs = {}
        self.path = path
        self.load_client_logs()

    def load_client_logs(self):
        # Json Read
        with open(self.path, 'r') as f:
            self.client_logs = json.load(f)

    def get_customer_activities(self, customer_id):
        for log in self.client_logs:
            if log["Customer"] == customer_id:
                return{"Logs": "\n".join([logi["Date and Time"] + " - " + logi["Log"] for logi in log["Logs"]])}
        return {"Logs":"No logs found for this customer"}
    
    def add_customer_activity(self, customer_id, activity):
        for log in self.client_logs:
            if log["Customer"] == customer_id:
                log["Logs"].append({"Date and Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Log": activity})
                self.save_client_logs()
                return {"Status": "Success"}
            
        # If customer not found create new log for customer
        self.client_logs.append({"Customer": customer_id, "Logs": [{"Date and Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Log": activity}]})
        self.save_client_logs()
        return {"Status": "Success"}
    
    def save_client_logs(self):
        with open(self.path, 'w') as f:
            json.dump(self.client_logs, f, indent=4)


client_log_manager = ClientLogManager("./data/logs.json")
CO = cohere.Client(os.environ['COHERE_API_KEY'])

class QCLIENT_Wrapper:
    def __init__(self,path):
        print("Creating QCLIENT ...")
        try:
            self.QCLIENT = qdrant_client.QdrantClient(path=path)
        except:
            print("Reattempting to create QCLIENT ...")
            self.QCLIENT.close()
            self.QCLIENT = qdrant_client.QdrantClient(path=path)
QCLIENT = QCLIENT_Wrapper(path='./qdrant_client').QCLIENT


class SimilarResultManager:
    def __init__(self, path):
        self.similar_results = {}
        self.path = path
        self.load_similar_results()
        self.emb_lamdda = lambda x: CO.embed(texts=[x],model='embed-english-v3.0',input_type='search_query').embeddings[0]
    
    def load_similar_results(self):
        # Json Read
        with open(self.path, 'r') as f:
            self.similar_results = json.load(f)
        
    def upsert(self):
        QCLIENT.recreate_collection(
            collection_name="past_conv",
            vectors_config=models.VectorParams(
                size=1024,  # Vector size is defined by used model
                distance=models.Distance.COSINE,
            )
        )
        documents = []
        for key, value in self.similar_results.items():
            for c in value['summary']:
                documents.append({
                    "id": key,
                    "text": c
                })
        QCLIENT.upload_points(collection_name="past_conv", points = [models.PointStruct(id=idx, vector=self.emb_lamdda(doc['text']),payload=doc) for idx, doc in enumerate(documents)])

    def get_similar_results(self, query):
        hits = QCLIENT.search(collection_name="past_conv",query_vector=self.emb_lamdda(query),limit=5)
        hits = [h for h in hits if h.score > 0.6]
        hit_ids = [h.payload['id'] for h in hits]
        # Only keep the hit ids whose freq is max
        max_freq = 0
        max_freq_id = None
        freqs = defaultdict(int)

        for hit_id in hit_ids:
            freqs[hit_id] += 1
            if freqs[hit_id] > max_freq:
                max_freq = freqs[hit_id]
                max_freq_id = hit_id

        print(f"Max freq id: {max_freq_id} | Max freq: {max_freq}")
        
        if max_freq_id is None:
            return {"Similar Solution": "No similar solution found"}

        return {"Similar Solution": "\n".join(self.similar_results[max_freq_id]['Conversation'])}

similar_result_manager = SimilarResultManager("./data/chats copy.json")

def similar_solution(body):
    if "query" not in body:
        return {"Similar Solution": "No similar solution found"}, 200
    sim_json = similar_result_manager.get_similar_results(body["query"])
    return sim_json, 200

def logs(body):
    if "customer" not in body:
        return {"Logs":""}, 200
    logs_json = client_log_manager.get_customer_activities(body["customer"])
    return logs_json, 200

def echo(body):
    return json.dumps(body), 200

def echo_sid(body):
    return json.dumps(body), 200

def validate(body):
    # sessionid = "{body.customer}" + "{currenttime(unix)}" 
    if "customer" not in body:
        return "Customer not found", 400
    if body["customer"] !='9p0q1r2s3t4u5v6w':
        return {"sessionid":"Invalid Customer"}, 400
    sessionid = body["customer"]+"_"+str(int(time.time()))
    return {"sessionid":sessionid}, 200

def endsession(body):    
    # Load from existing file
    # try:
    #     with open('./data/feedbacks.json', 'r') as f:
    #         sessions = json.load(f)
    # except:
    #     sessions = []

    # Append new session
    sessions = []
    try:
        for b in body:
            b["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sessions.append(b)

        # Write to file
        # with open('./data/feedbacks.json', 'w') as f:
        #     json.dump(sessions, f, indent=4)
        collection.insertMany(sessions)
        return {"Status":"Session ended successfully"}, 200
    except:
        return {"Status":"Failed to end session"}, 400


def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


def analytics(body):
    data = list(collection.find({}))
    for doc in data:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for JSON serialization

    response = Response(response=json.dumps({"data": data}), status=200, mimetype='application/json')
    return add_cors_headers(response)


request_handlers = {
    "/echo":echo,
    "/simsolution":similar_solution,
    "/logs":logs,
    "/validate":validate,
    "/echo_sid":echo_sid,
    "/endsession":endsession,
    "/analytics":analytics
}

@functions_framework.http
def hello_http(request):
    request_json = request.get_json(silent=True)
    path = request.path

    if path not in request_handlers:
      return "Unsupported path", 500
    
    return request_handlers[path](request_json)