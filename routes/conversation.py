from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from AI.aiManager import gerar_resposta_stream

from AI.Modelos import Modelos
from AI.Personas import Personas
from database.chats import get_chat_history, add_message, get_chat, delete_chat, update_chat_title, create_chat, get_all_chats_descriptions

import json

from pydantic import BaseModel

router = APIRouter(
    prefix="/conversation",
    tags=["conversation"],
)

class ConversationUpdate(BaseModel):
    title: str

class ConversationCreate(BaseModel):
    title: str
    description: str

class MessageRequest(BaseModel):
    user_input: str
    model: Modelos = Modelos.GEMINI_25_FLASH
    persona: Personas = Personas.Roteirista

CONVERSA_NAO_ENCONTRADA = HTTPException(status_code=404, detail="Conversa não encontrada.")

def gerar_resposta(id: str, prompt : str, modelo : Modelos = Modelos.GEMINI_25_FLASH, persona : Personas = Personas.Roteirista):
    USER_PROMPT = {"role": "user", "content": prompt}

    historico = get_chat_history(id)["messages"]

    historico.append(USER_PROMPT)

    add_message(id, USER_PROMPT)

    resposta = {
        "role": "assistant",
        "content": "",
        "reasoning": "",
    }
    
    for response in gerar_resposta_stream(historico, modelo, persona):
        resposta["content"] = resposta["content"] + response["content"]
        resposta["reasoning"] = resposta["reasoning"] + response["reasoning"]

        yield json.dumps(response) + "\n"

    add_message(id, resposta)

    return []

@router.get("/history/{conversation_id}",)
async def get_conversation_history(conversation_id: str):
   resultado = get_chat_history(conversation_id)

   if(resultado == None):
        raise CONVERSA_NAO_ENCONTRADA

   return resultado["messages"]

@router.get("/models")
async def list_models():
    modelos = []
    for modelo in Modelos:
        modelos.append({
            "name": modelo.valor["name"],
            "model": modelo.valor["model"],
            "provider": modelo.valor["provider"]
        })
    return modelos

@router.get("/{conversation_id}",)
async def get_conversation_history(conversation_id: str):
   resultado = get_chat(conversation_id)

   if(resultado == None):
        raise CONVERSA_NAO_ENCONTRADA

   return resultado

@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str):
    resultado = delete_chat(conversation_id)

    if(not resultado):
        raise CONVERSA_NAO_ENCONTRADA

    return {"message": "Chat deleted successfully."}

@router.patch("/{conversation_id}")
async def update_conversation_title(conversation_id: str, payload: ConversationUpdate):
    return update_chat_title(conversation_id, payload.title)

@router.post("/{conversation_id}/message")
async def send_message(conversation_id: str, payload: MessageRequest):
    return StreamingResponse(gerar_resposta(conversation_id, payload.user_input, modelo=payload.model, persona=payload.persona), media_type="text/event-stream")


@router.post("/", status_code=201)
async def create_conversation(payload: ConversationCreate):
    return create_chat(payload.title, payload.description)
    
@router.get("/")
async def list_conversations(user_id):
    return get_all_chats_descriptions()