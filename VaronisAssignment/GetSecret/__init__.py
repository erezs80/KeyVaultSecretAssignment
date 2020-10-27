import os
import logging
from datetime import datetime
from http import HTTPStatus
from azure.keyvault.secrets import SecretClient
from azure.common.credentials import (
    ServicePrincipalCredentials,
    get_azure_cli_credentials,
)
from azure.identity import DefaultAzureCredential

import azure.functions as func

logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)

keyVaultNames = os.environ["KEY_VAULT_NAME"].split(" ")


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    credentials = DefaultAzureCredential()
    
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        retrieved_secrets = []
        for vault in keyVaultNames:
            retrieved_secret = {}
            KVUri = f"https://{vault}.vault.azure.net"
            client = SecretClient(vault_url=KVUri, credential=credentials)
            try:
                logging.info(f"Try to retrive secret: {name} from key vault: {vault}")
                secret = client.get_secret(name)
                secret_creation_time = secret.properties.created_on
                secret_creation_time_parse = secret_creation_time.strftime("%m/%d/%Y")
                retrieved_secret["Key Vault Name"] = vault
                retrieved_secret["Key Vault Secret Name"] = secret.name
                retrieved_secret["Secret creation date"] = secret_creation_time_parse
                retrieved_secret["Key Vault Secret Value"] = secret.value
                retrieved_secrets.append(retrieved_secret)
            except:
                logging.info(f"Could not find secret: {name} in key vault: {vault}")
                continue
        if retrieved_secrets:
            return func.HttpResponse(f"secret details: {retrieved_secrets}")
        else:
            return func.HttpResponse(f"Could not find secret {name} in any vault")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a secret name in the query string or in the request body for a response with the secret details.",
             status_code=200
        )
