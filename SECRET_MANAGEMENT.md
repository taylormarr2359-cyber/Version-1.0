Secret management recommendations
===============================

Goal: keep API keys out of source control and use a proper secret store in production.

1) Azure Key Vault (recommended for Azure-hosted apps)

- Create a vault (Azure CLI):

  az group create -n my-rg -l eastus
  az keyvault create -n my-vault -g my-rg -l eastus

- Add a secret:

  az keyvault secret set --vault-name my-vault -n BLACKBOX_API_KEY --value "<your-key>"

- In production, grant your app a managed identity or service principal access to the vault and use the `azure-identity` + `azure-keyvault-secrets` client to fetch secrets at runtime:

  ```py
  from azure.identity import DefaultAzureCredential
  from azure.keyvault.secrets import SecretClient

  credential = DefaultAzureCredential()
  client = SecretClient(vault_url="https://my-vault.vault.azure.net/", credential=credential)
  api_key = client.get_secret("BLACKBOX_API_KEY").value
  ```

2) CI/CD (GitHub Actions)

- Store secrets in the repository or organization secrets in GitHub settings.
- Reference them in workflows and pass them to jobs as env vars:

  ```yaml
  env:
    BLACKBOX_API_KEY: ${{ secrets.BLACKBOX_API_KEY }}
  ```

3) Local development

- Use `az keyvault` commands after `az login`, or keep a local `.env` that is listed in `.gitignore` and not committed. Use `.env.example` in the repo as a template.

4) Best practices

- Rotate keys regularly.
- Use least-privilege credentials and separate keys per environment.
- Do not commit real secrets. Audit repo history if a secret is accidentally committed.

References
- Azure Key Vault docs: https://learn.microsoft.com/azure/key-vault/
- GitHub Actions secrets: https://docs.github.com/actions/security-guides/encrypted-secrets
