def get_engine():
    neon_url = os.getenv("NEON_DATABASE_URL")
    if neon_url:
        # Force psycopg2 dialect
        if "postgresql://" in neon_url and "psycopg2" not in neon_url:
            neon_url = neon_url.replace("postgresql://", "postgresql+psycopg2://")
        return create_engine(neon_url)
    else:
        return create_engine(
            f"postgresql+psycopg2://"
            f"{os.getenv('DB_USER', 'airquality')}:"
            f"{os.getenv('DB_PASSWORD', 'airquality123')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5433')}/"
            f"{os.getenv('DB_NAME', 'airqualitydb')}"
        )