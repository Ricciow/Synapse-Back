from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from AI.aiManager import gerar_resposta_stream

from AI.Modelos import Modelos
from AI.Personas import Personas
from database.chats import get_chat_history, add_message, get_chat, delete_chat, update_chat_title, create_chat, get_all_chats_titles, add_model_history

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

class MessageRequest(BaseModel):
    user_input: str
    model: Modelos = Modelos.GEMINI_25_FLASH
    persona: Personas = Personas.Agente

CONVERSA_NAO_ENCONTRADA = HTTPException(status_code=404, detail="Conversa não encontrada.")

def gerar_resposta(id: str, prompt : str, modelo : Modelos = Modelos.GEMINI_25_FLASH, persona : Personas = Personas.Agente):
    USER_PROMPT = {"role": "user", "content": prompt}
    MODEL_NAME = modelo.valor["name"]

    mensagens = get_chat_history(id)["messages"]

    historico =  next((d for d in mensagens if d['model'] == MODEL_NAME), {}).get("messages", [])

    if(historico == []):
        add_model_history(id, MODEL_NAME)

    historico.append(USER_PROMPT)

    add_message(id, USER_PROMPT, MODEL_NAME)

    resposta = {
        "role": "assistant",
        "content": "",
        "reasoning": "",
    }
    
    for response in gerar_resposta_stream(historico, modelo, persona):
        resposta["content"] = resposta["content"] + response["content"]
        resposta["reasoning"] = resposta["reasoning"] + response["reasoning"]

        yield json.dumps(response) + "\n"

    add_message(id, resposta, MODEL_NAME)

    return []

@router.get("/history/{conversation_id}",)
async def get_conversation_history(conversation_id: str):
    try:
        resultado = get_chat_history(conversation_id)

        if(resultado == None):
                raise CONVERSA_NAO_ENCONTRADA

        return resultado["messages"]
    except Exception:
        raise CONVERSA_NAO_ENCONTRADA


@router.get("/models")
async def list_models():
    modelos = []
    for modelo in Modelos:
        modelos.append(modelo.valor)
    return modelos

@router.get("/{conversation_id}",)
async def get_chat_data(conversation_id: str):
    try:
        resultado = get_chat(conversation_id)
    except Exception:
        raise CONVERSA_NAO_ENCONTRADA

    if(resultado == None):
        raise CONVERSA_NAO_ENCONTRADA

    return resultado

@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str):
    resultado = delete_chat(conversation_id)

    if(not resultado):
        raise CONVERSA_NAO_ENCONTRADA

@router.patch("/{conversation_id}")
async def update_conversation_title(conversation_id: str, payload: ConversationUpdate):
    return update_chat_title(conversation_id, payload.title)

@router.post("/{conversation_id}/message")
async def send_message(conversation_id: str, payload: MessageRequest):
    if(get_chat(conversation_id) == None):
        raise CONVERSA_NAO_ENCONTRADA

    return StreamingResponse(gerar_resposta(conversation_id, payload.user_input, modelo=payload.model, persona=payload.persona), media_type="text/event-stream")


@router.post("/", status_code=201)
async def create_conversation(payload: ConversationCreate):
    return create_chat(payload.title)
    
@router.get("/")
async def list_conversations():
    return get_all_chats_titles()