def dangerously_drop_noistli_table():
    """Drop table from the database."""
    from noiist.config.database import engine
    from noiist.models.noisli import noisli_user

    noisli_user.drop(engine)
