import os
from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    app.config["APP_ENV"] = os.getenv("APP_ENV", "local")
    app.config["APP_VERSION"] = os.getenv("APP_VERSION", "dev")
    app.config["BUILD_NUMBER"] = os.getenv("BUILD_NUMBER", "0")
    app.config["GIT_COMMIT"] = os.getenv("GIT_COMMIT", "unknown")

    @app.get("/")
    def index():
        return jsonify(
            message="Flask CI/CD application",
            environment=app.config["APP_ENV"],
            version=app.config["APP_VERSION"],
            build=app.config["BUILD_NUMBER"],
            commit=app.config["GIT_COMMIT"]
        )

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            environment=app.config["APP_ENV"]
        )

    @app.get("/env")
    def env():
        return jsonify(
            environment=app.config["APP_ENV"],
            version=app.config["APP_VERSION"],
            build=app.config["BUILD_NUMBER"]
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
