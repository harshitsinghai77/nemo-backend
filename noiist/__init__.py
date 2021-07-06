__version__ = "0.1.0"
import os
import environ

environ.Env.read_env(env_file=os.getenv("ENVFILEPATH", ".env"))
