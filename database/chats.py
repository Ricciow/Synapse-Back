from database.database import chats
from bson.objectid import ObjectId

# Estrutura de um chat:
# {
#   "_id": "chat_id_A",
#   "titulo": "Chat nome",
#   "messages": [
#     {
#         "model": "DeepSeek",
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "Olá"
#             },
#             {
#                 "role": "assistant",
#                 "content": "Olá"
#             }
#         ]
#     }  
#   ]
# }

def create_chat(title):
    chat_document = {
        "title": title, 
        "messages": []
    }
    chats.insert_one(chat_document)
    chat_document["id"] = str(chat_document.pop("_id"))
    
    return chat_document

def delete_chat(id):
    resultado = chats.delete_one({"_id": ObjectId(id)})
    return resultado.deleted_count > 0

def get_chat_history(id):
    QUERY_RESULT = chats.find_one(
        {"_id": ObjectId(id)}, 
        {"_id": 0, "messages": 1}
    )
    return QUERY_RESULT

def get_chat(id):
    QUERY_RESULT = chats.find_one(
        {"_id": ObjectId(id)}, 
        {"_id": 0, "title": 1, "messages": 1}
    )
    return QUERY_RESULT

def get_all_chats_titles():
    QUERY_RESULT = chats.find({}, {"title": 1})
    
    chat_list = []
    for doc in QUERY_RESULT:
        doc["id"] = str(doc.pop("_id"))
        chat_list.append(doc)
        
    return chat_list

def add_model_history(id, model):
    chats.update_one(
        {"_id": ObjectId(id)}, 
        {"$push": {"messages": {"model": model, "messages": []}}}
    )

def add_message(id, message, model):
    chats.update_one(
        {"_id": ObjectId(id), "messages.model": model}, 
        {"$push": {"messages.$.messages": message}}
    )

def update_chat_title(id, title):
    chats.update_one(
        {"_id": ObjectId(id)}, 
        {"$set": {"title": title}}
    )

    return {
        "id": id,
        "title": title
    }