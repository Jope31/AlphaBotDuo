import pulumi
import pulumi_digitalocean as do

config = pulumi.Config()
libsql_url = config.require_secret("LIBSQL_URL")
libsql_auth_token = config.require_secret("LIBSQL_AUTH_TOKEN")
alpaca_key = config.require_secret("ALPACA_KEY")
composer_key = config.require_secret("COMPOSER_KEY")

app = do.App("alpha-bot-app",
    spec=do.AppSpecArgs(
        name="alpha-bot-app",
        region="nyc",
        services=[
            do.AppSpecServiceArgs(
                name="alpha-bot-service",
                git=do.AppSpecServiceGitArgs(
                    repo_clone_url="https://github.com/Jope31/AlphaBotDuo.git",
                    branch="main",
                ),
                run_command="python alpha_bot_execution.py",
                http_port=5002,
                envs=[
                    do.AppSpecServiceEnvArgs(key="LIBSQL_URL", value=libsql_url, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="LIBSQL_AUTH_TOKEN", value=libsql_auth_token, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="ALPACA_KEY", value=alpaca_key, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="COMPOSER_KEY", value=composer_key, type="SECRET"),
                ]
            )
        ]
    )
)

pulumi.export("live_url", app.live_url)
