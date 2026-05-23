from __future__ import annotations

from flask import Flask, jsonify, request, send_file

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

    @app.get("/api/rpa/jobs")
    def rpa_jobs():
        return jsonify({"data": service.rpa_jobs()})

    @app.post("/api/rpa/jobs")
    def submit_rpa_job():
        payload = request.get_json(silent=True) or {}
        try:
            job = service.submit_rpa_job(
                account_id=str(payload.get("accountId", "")),
                action=str(payload.get("action", "")),
                operator=str(payload.get("operator") or "Portfolio Reviewer"),
            )
            return jsonify({"data": job}), 201
        except KeyError:
            return jsonify({"error": "Account was not found"}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.get("/api/rpa/artifacts/<filename>")
    def rpa_artifact(filename: str):
        try:
            return send_file(service.artifact_path(filename), as_attachment=True)
        except FileNotFoundError:
            return jsonify({"error": "Artifact was not found"}), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
