Thalia Bot 
----------

[![Linting](https://img.shields.io/github/workflow/status/svthalia/discord-bot/Linting?style=flat-square)](https://github.com/svthalia/concrexit/actions)
[![Issues](https://img.shields.io/github/issues/svthalia/discord-bot?style=flat-square)](https://github.com/svthalia/concrexit/issues)
[![License](https://img.shields.io/github/license/svthalia/discord-bot?style=flat-square)](https://github.com/svthalia/discord-bot/blob/master/LICENSE.md)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

This repository contains the source code for a Discord bot that connects the users of a guild to a [https://github.com/svthalia/concrexit](Concrexit) backend and allows us to sync the guild with settings from such a backend.

The code exists of three parts:
1. authentication
    
   This part contains code for AWS Lambdas that allow a user to authenticate with the backend and attach their Discord user to their Thalia account. It will create a record in a DynamoDB connecting a Discord user id to a Thalia user id allowing us to identify our members.

1. bot
    
   This is the actual code for the bot, it is written using [discord.py](https://discordpy.readthedocs.io) and automatically loads cogs from the cogs module. These cogs can be used for functionalities like member syncing or other commands. The bot can use the DynamoDB instance from the authentication to identify members.

2. common

   These are shared code modules that can both be used in the bot and in the authentication code.

The essentials of this code assume that you have basic knowledge of how to access services provided by Amazon Web Services.
To be able to deploy you should only need credentials and an installation of Terraform though.

## Development environment

To be able to run this service you need a couple of prerequisites:
1. An installation of [Python 3.8](https://www.python.org/)
2. The dependency manager [Poetry](https://python-poetry.org/)
3. Some instance of [concrexit](https://github.com/svthalia/concrexit)
4. A Discord bot token from their [developer portal](https://discord.com/developers/applications)
5. Have a DynamoDB instance available to you
   - You could deploy the Terraform common module to create one
   - Or run [the local version](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)

Once you are ready you can proceed to setting up the environment itself.

### Setup

1. Run `poetry install` to install all the dependencies for the tool. These are the same for the lambda and bot code.
2. Create an `.env` file for local execution of the bot, see the example below
3. Run `poetry run bot/main.py` to start the Discord bot

If you want to test the AWS Lambda code for the authentication we recommend that you deploy these to AWS since they use API Gateway.
It is technically possible to run [API Gateway](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html) locally but it is not included in this repository.
_Note_: The environment variables in the `.env` file only work for the bot, the lambdas require different OAuth credentials.

#### Example .env

```
DISCORD_BOT_TOKEN = "<generated-for-your-bot>"
DISCORD_GUILD_ID = "430967226567809111"

USERS_TABLE = "discord-bot-develop-users"
DOMAIN_NAME = "https://discord-bot-develop.technicie.nl/"

THALIA_SERVER_URL     = "http://localhost:8000"
THALIA_CLIENT_ID      = "<generated-for-your-client>"
THALIA_CLIENT_SECRET  = "<generated-for-your-client>"

AWS_DEFAULT_REGION = "eu-west-1"
AWS_ACCESS_KEY_ID = "fakeMyKeyId"
AWS_SECRET_ACCESS_KEY = "fakeSecretAccessKey"
```

If you have the AWS CLI setup on your local machine for the environment you want to use you can leave out the AWS information.

## Deploying

To be able to deploy this service you need access to the Thalia AWS account with permissions to change EC2, DynamoDB, Route53, Lambda and API Gateway services. Moreover, you need an installation of [Terraform](https://terraform.io).

### First time

To deploy the develop environment make sure your working directory is set to `terraform/stages/develop`.

1. Setup the missing variables (see below)
2. Run `terraform init`
3. Run `terraform apply` to deploy everything

#### Variables

The Terraform configuration is missing some configuration when you first clone this repository.
There are [multiple ways to insert variables into the Terraform root module](https://www.terraform.io/docs/configuration/variables.html#assigning-values-to-root-module-variables).
One example is using a `.tfvars` file inside the stage folder. The code below is an example for a `local.auto.tfvars` file that will be automatically ignored by version control since it is in `.gitignore`.

```
discord_bot_token = "<generated-for-your-bot>"
discord_guild_id  = "430967226567809111"

thalia_server_url         = "http://localhost:8000"
thalia_auth_client_id     = "<generated-for-your-client>"
thalia_auth_client_secret = "<generated-for-your-client>"
thalia_bot_client_id      = "<generated-for-your-client>"
thalia_bot_client_secret  = "<generated-for-your-client>"
```

### Specific modules

The Terraform config is split into three parts:
1. The server that runs the bot
2. The AWS Lambdas and API Gateway that allow you to do the OAuth2 connection with the backend
3. Common resources

It is possible to target these resources and deploy only parts of the configuration:

```
terraform apply -target="module.discord_bot_server"
terraform destroy -target="module.discord_bot_server"
terraform apply -target="module.discord_bot_authentication"
terraform destroy -target="module.discord_bot_authentication"
terraform apply -target="module.discord_bot_common"
terraform destroy -target="module.discord_bot_common"
```


