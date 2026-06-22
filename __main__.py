import pulumi
import pulumi_digitalocean as do

config = pulumi.Config()
libsql_url = config.require_secret("LIBSQL_URL")
libsql_auth_token = config.require_secret("LIBSQL_AUTH_TOKEN")
alpaca_key = config.require_secret("ALPACA_KEY")
alpaca_secret = config.require_secret("ALPACA_SECRET")
composer_key = config.require_secret("COMPOSER_KEY")
composer_secret = config.require_secret("COMPOSER_SECRET")
discord_url = config.require_secret("DISCORD_WEBHOOK_URL")

app = do.App("alpha-bot-app",
    spec=do.AppSpecArgs(
        name="alpha-bot-app",
        region="nyc3",
        services=[
            do.AppSpecServiceArgs(
                name="alpha-bot-service",
                git=do.AppSpecServiceGitArgs(
                    repo_clone_url="https://github.com/Jope31/AlphaBotDuo.git",
                    branch="main",
                ),
                run_command="python alpha_bot_execution.py",
                http_port=5002,
                instance_count=1,
                instance_size_slug="apps-s-1vcpu-1gb",
                envs=[
                    do.AppSpecServiceEnvArgs(key="LIBSQL_URL", value=libsql_url, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="LIBSQL_AUTH_TOKEN", value=libsql_auth_token, type="SECRET"),
                    
                    do.AppSpecServiceEnvArgs(key="ALPACA_KEY", value=alpaca_key, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="ALPACA_KEY_ID", value=alpaca_key, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="APCA_API_KEY_ID", value=alpaca_key, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="ALPACA_SECRET", value=alpaca_secret, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="ALPACA_SECRET_KEY", value=alpaca_secret, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="APCA_API_SECRET_KEY", value=alpaca_secret, type="SECRET"),
                    
                    do.AppSpecServiceEnvArgs(key="COMPOSER_KEY", value=composer_key, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="COMPOSER_KEY_ID", value=composer_key, type="SECRET"),
                    do.AppSpecServiceEnvArgs(key="COMPOSER_SECRET", value=composer_secret, type="SECRET"),
                    
                    do.AppSpecServiceEnvArgs(key="DISCORD_WEBHOOK_URL", value=discord_url, type="SECRET"),
                ]
            )
        ]
    )
)

pulumi.export("live_url", app.live_url)