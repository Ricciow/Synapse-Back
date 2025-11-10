from database.database import chats
from bson.objectid import ObjectId

# Estrutura de um chat:
# {
#   "_id": "chat_id_A",
#   "projectId": "project_id_123", 
#   "titulo": "Chat sobre Roteiro",
#   "descrição": "Brainstorm para o filme...",
#   "mensagens": [
#     { "role": "user", "content": "Me dê ideias...", "reasoning": null },
#     { "role": "assistant", "content": "...", "reasoning": "..." }
#   ]
# }

def create_chat(title, description):
    chat_document = {
        "title": title, 
        "description": description, 
        "messages": []
    }
    chats.insert_one(chat_document)
    chat_document["_id"] = str(chat_document["_id"])
    
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
        {"_id": 0, "title": 1, "description": 1, "messages": 1}
    )
    return QUERY_RESULT

def get_all_chats_descriptions():
    QUERY_RESULT = chats.find({}, {"title": 1, "description": 1})
    
    chat_list = []
    for doc in QUERY_RESULT:
        doc["id"] = str(doc.pop("_id"))
        chat_list.append(doc)
        
    return chat_list

def add_message(id, message):
    chats.update_one(
        {"_id": ObjectId(id)}, 
        {"$push": {"messages": message}}
    )

def remove_last_message(id):
    chats.update_one(
        {"_id": ObjectId(id)}, 
        {"$pop": {"messages": 1}}
    )

def update_chat_title(id, title):
    chats.update_one(
        {"_id": ObjectId(id)}, 
        {"$set": {"title": title}}
    )