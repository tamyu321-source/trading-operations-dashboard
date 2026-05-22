from __future__ import annotations

from flask import Flask, jsonify, request

from .services import TradingOperationsService


def create_app() -> Flask:
    app = Flask(__name__)
    service = TradingOperationsService()

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "trading-operations-dashboard"})

    @app.get("/api/dashboard")
    def dashboard():
        return jsonify({"data": service.dashboard()})

    @app.get("/api/accounts")
    def accounts():
        return jsonify({"data": service.accounts(request.args.get("status"))})

    @app.get("/api/holdings")
    def holdings():
        return jsonify({"data": service.holdings(request.args.get("accountId"))})

    @app.post("/api/strategies/<strategy_id>")
    def update_strategy(strategy_id: str):
        payload = request.get_json(silent=True) or {}
        try:
            return jsonify({"data": service.update_strategy(strategy_id, payload)})
        except KeyError:
            return jsonify({"error": f"Strategy '{strategy_id}' was not found"}), 404

    @app.get("/api/logs")
    def logs():
        return jsonify({"data": service.logs()})

    @app.get("/api/servers")
    def servers():
        return jsonify({"data": service.servers()})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
