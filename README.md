Thalia Bot
----------

This repository contains the source code for a Discord bot that connects the users of a guild to a [https://github.com/svthalia/concrexit](Concrexit) backend and allows us to sync the guild with settings from such a backend.

The code exists of three parts:
1. authentication
This part contains lambdas that allow a user to authenticate with the backend and attach their Discord user to their Thalia account.
2. bot
This is the actual code for the bot, it is written using [discord.py](https://discordpy.readthedocs.io) and automatically loads cogs from the cogs module. 
3. common
These are shared code modules that can both be used in the bot and in the authentication code.


### Deploying

To be able to deploy this service you need access to the Thalia AWS account with permissions to change EC2, DynamoDB, Route53, Lambda and API Gateway services. Moreover, you need an installation of [Terraform](https://terraform.io).

#### First time

To deploy the develop environment make sure your working directory is set to `terraform/stages/develop`.

1. Run `terraform init`
2. Run `terraform apply` to deploy everything.

#### Specific modules

The Terraform config is split into three parts:
1. The server that runs the bot
2. The lambdas that allow you to do the OAuth2 connection with the backend
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


