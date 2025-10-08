from flask import jsonify, current_app


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log full stack trace to server logs
        try:
            current_app.logger.exception("Unhandled exception")
        except Exception:
            pass
        # Return concise JSON error for client
        return jsonify({"error": str(e)}), 500
