def init_app(app):
    from .health import bp as health_bp
    from .accounts import bp as accounts_bp
    from .transactions import bp as tx_bp
    from .budgets import bp as budgets_bp
    from .reports import bp as reports_bp

    app.register_blueprint(health_bp,     url_prefix="/api")
    app.register_blueprint(accounts_bp,   url_prefix="/api/accounts")
    app.register_blueprint(tx_bp,         url_prefix="/api/transactions")
    app.register_blueprint(budgets_bp,    url_prefix="/api/budgets")
    app.register_blueprint(reports_bp,    url_prefix="/api/reports")
