"""
Entrypoint do agente CRM HITL.
Pode ser chamado diretamente (local) ou via HTTP POST (Cloud Run).
"""

import json
import logging
from datetime import date

from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def run_agent() -> None:
    from agent import agent  # import tardio para evitar ciclos

    hoje = date.today().strftime("%d/%m/%Y")
    prompt = (
        f"Hoje é {hoje}. Execute a verificação completa de inconsistências de CRM "
        "e poste o relatório no Slack conforme as instruções do sistema."
    )

    log.info("Iniciando agente CRM HITL — %s", hoje)

    final_state = agent.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config={"recursion_limit": 50},
    )

    last = final_state["messages"][-1]
    log.info("Agente finalizado. Última mensagem:\n%s", last.content)


# Suporte a Cloud Run (HTTP handler simples com Flask — adicionado na Fase 2)
def create_app():
    try:
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route("/", methods=["POST"])
        def handle():
            run_agent()
            return jsonify({"status": "ok"}), 200

        return app
    except ImportError:
        return None


if __name__ == "__main__":
    run_agent()
