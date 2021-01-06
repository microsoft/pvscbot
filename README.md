[![CI](https://github.com/microsoft/pvscbot/workflows/CI/badge.svg?branch=master&event=push "CI status badge")](https://github.com/microsoft/pvscbot/actions?query=branch%3Amaster+event%3Apush+workflow%3ACI)

# Purpose

This bot exists to automate the development process/workflow for
https://github.com/microsoft/vscode-python. It also acts as a simple demo of
a GitHub bot running on Azure.

This bot is what is known as an OAuth app and is not a GitHub app. The
[differences](https://developer.github.com/apps/differences-between-apps/) come
down to simplicity in authentication and how widely can the bot be deployed. Since
this bot is only deployed for a single repository and the original author was
intimately familiar with OAuth apps that was the route taken.

This bot also predates [GitHub Actions](https://developer.github.com/actions/)
being released. As such some things this bot does may be easier to do as an action.

Currently the bot will do the following things for you:

1. Add/remove the `classify` label based on whether any other status label is set.
1. When an issue is closed, remove any status-related labels, e.g. `needs PR`
   (with the idea that if an issue is re-opened then it needs to be re-evaluated
   as to why the issue is still open).

# Deployment

## Generically

### On the deployment/hosting side

You must set two environment variables for the bot to function:

1. `GH_SECRET`: [secret between GitHub and your bot](https://developer.github.com/webhooks/securing/#setting-your-secret-token).
1. `GH_AUTH`: [Auth token](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line) for the bot to make changes in your repo.

The [shared secret](https://developer.github.com/webhooks/securing/#setting-your-secret-token)
between GitHub and your bot is used to verify that the webhook payload actually
originated from GitHub for your repository and isn't malicious. This is important
as a malicious user could send fake webhook payloads to your bot and cause it to
make changes on the malicious user's behalf.

The [personal access token](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line)
is to empower your bot to make changes to your repo on your behalf. You can use
a token from your personal GitHub account or create a fake bot account. Make sure
the token has the following scopes/permissions:

1.`repo:public_repo` (if your repo is public; adjust accordingly for your needs)

### On the GitHub side

When [creating the webhook](https://developer.github.com/webhooks/creating/) you
need to specify what events to send to your endpoint. This bot supports the
following events:

1. `Issues`

## Azure

The bot is currently written to support
[Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/)
running on Python 3.7.

# Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
