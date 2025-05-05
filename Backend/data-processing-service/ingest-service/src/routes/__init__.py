from .import_routes import import_bp

def register_routes(app):
  """Register all blueprint routes with the app."""
  app.register_blueprint(import_bp)