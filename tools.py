"""
Ferramentas do agente CRM HITL.
Cada função é registrada como tool no LangGraph via @tool decorator.
"""

import requests
from datetime import datetime, timedelta, timezone
from langchain_core.tools import tool

from config import (
    HUBSPOT_API_TOKEN,
    SLACK_BOT_TOKEN,
    SLACK_CHANNEL_ID,
    HUBSPOT_BASE_URL,
    SLACK_BASE_URL,
)

_HUBSPOT_HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
    "Content-Type": "application/json",
}

_SLACK_HEADERS = {
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    "Content-Type": "application/json",
}


def _hubspot_post(path: str, payload: dict) -> dict:
    url = f"{HUBSPOT_BASE_URL}{path}"
    resp = requests.post(url, json=payload, headers=_HUBSPOT_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _hubspot_get(path: str, params: dict | None = None) -> dict:
    url = f"{HUBSPOT_BASE_URL}{path}"
    resp = requests.get(url, params=params, headers=_HUBSPOT_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# 1. buscar_deals_abertos
# ---------------------------------------------------------------------------

@tool
def buscar_deals_abertos(pipeline_id: str = "") -> dict:
    """
    Busca todos os deals com closedWon=false (pipeline aberto) no HubSpot.
    Retorna lista de deals com campos: id, dealname, hubspot_owner_id,
    pipeline, dealstage, createdate, hs_lastmodifieddate, amount,
    hs_all_owner_ids.

    Args:
        pipeline_id: Filtra por pipeline específico (opcional).
                     Se vazio, retorna deals de todos os pipelines.
    """
    properties = [
        "dealname",
        "hubspot_owner_id",
        "pipeline",
        "dealstage",
        "createdate",
        "hs_lastmodifieddate",
        "closedate",
        "amount",
        "hs_all_owner_ids",
        "hs_deal_stage_probability",
    ]

    filters = [
        {
            "propertyName": "hs_is_closed_won",
            "operator": "EQ",
            "value": "false",
        },
        {
            "propertyName": "hs_is_closed",
            "operator": "EQ",
            "value": "false",
        },
    ]

    if pipeline_id:
        filters.append(
            {
                "propertyName": "pipeline",
                "operator": "EQ",
                "value": pipeline_id,
            }
        )

    deals: list[dict] = []
    after: str | None = None

    while True:
        payload: dict = {
            "filterGroups": [{"filters": filters}],
            "properties": properties,
            "limit": 100,
            "sorts": [
                {
                    "propertyName": "hs_lastmodifieddate",
                    "direction": "DESCENDING",
                }
            ],
        }
        if after:
            payload["after"] = after

        data = _hubspot_post("/crm/v3/objects/deals/search", payload)

        results = data.get("results", [])
        deals.extend(
            {
                "id": d["id"],
                **d.get("properties", {}),
            }
            for d in results
        )

        paging = data.get("paging", {})
        next_page = paging.get("next", {})
        after = next_page.get("after")
        if not after:
            break

    return {
        "total": len(deals),
        "deals": deals,
    }


# ---------------------------------------------------------------------------
# 2. buscar_contatos_batch  (skeleton — implementar a seguir)
# ---------------------------------------------------------------------------

@tool
def buscar_contatos_batch(deal_ids: list[str]) -> dict:
    """
    Busca os contatos associados a uma lista de deal IDs via batch associations API.

    Args:
        deal_ids: Lista de IDs de deals (strings).
    """
    raise NotImplementedError("Implementar na próxima etapa")


# ---------------------------------------------------------------------------
# 3. buscar_detalhes_contatos  (skeleton)
# ---------------------------------------------------------------------------

@tool
def buscar_detalhes_contatos(contact_ids: list[str]) -> dict:
    """
    Busca propriedades dos contatos em batch.

    Args:
        contact_ids: Lista de IDs de contatos (strings).
    """
    raise NotImplementedError("Implementar na próxima etapa")


# ---------------------------------------------------------------------------
# 4. postar_canal_slack  (skeleton)
# ---------------------------------------------------------------------------

@tool
def postar_canal_slack(texto: str) -> dict:
    """
    Posta uma mensagem no canal #marketing-comercial do Slack.

    Args:
        texto: Texto da mensagem (suporta Slack mrkdwn).
    """
    raise NotImplementedError("Implementar na próxima etapa")


# ---------------------------------------------------------------------------
# 5. buscar_historico_slack  (skeleton)
# ---------------------------------------------------------------------------

@tool
def buscar_historico_slack(dias: int = 30) -> dict:
    """
    Busca o histórico de mensagens do canal Slack dos últimos N dias.

    Args:
        dias: Janela de busca em dias (padrão 30).
    """
    raise NotImplementedError("Implementar na próxima etapa")


# ---------------------------------------------------------------------------
# 6. solicitar_analise_workflow  (skeleton)
# ---------------------------------------------------------------------------

@tool
def solicitar_analise_workflow(contexto: str) -> dict:
    """
    Aciona o subagente de análise profunda de inconsistências.

    Args:
        contexto: Resumo JSON dos deals problemáticos encontrados.
    """
    raise NotImplementedError("Implementar na próxima etapa")


# Exporta lista de tools para o agente
ALL_TOOLS = [
    buscar_deals_abertos,
    buscar_contatos_batch,
    buscar_detalhes_contatos,
    postar_canal_slack,
    buscar_historico_slack,
    solicitar_analise_workflow,
]
