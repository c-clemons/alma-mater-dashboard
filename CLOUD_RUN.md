# Deploying the Alma Mater portal to Cloud Run

Target: a **private** Cloud Run service, SSO via **Cloudflare Access**, at
`https://almamater.empirica-analytics.com`.

> Alma runs the **live** app (entry `app_client.py`) with its Shopify/QBO
> integrations. The kit is now vendored and `check_password()` trusts an identity
> proxy first (single email login via Cloudflare Access / IAP), falling back to
> the `dashboard_password` gate when there's no proxy (local dev).

## Prerequisites (one-time per GCP project)

```bash
export PROJECT=<your-gcp-project>  REGION=us-central1
gcloud config set project $PROJECT
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create portals \
  --repository-format=docker --location=$REGION --description="Empirica client portals"
```

## 1. Secrets

Create a local `.streamlit/secrets.toml` (gitignored) with everything the live
app reads today — copy the values from the current Streamlit Cloud app's
Settings → Secrets:

```toml
dashboard_password = "..."
# Shopify + any QBO keys the live app uses, e.g.:
# shopify_store = "..."; shopify_token = "..."
```

```bash
gcloud secrets create alma-secrets --data-file=.streamlit/secrets.toml
gcloud secrets versions add alma-secrets --data-file=.streamlit/secrets.toml   # updates
PROJNUM=$(gcloud projects describe $PROJECT --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding alma-secrets \
  --member="serviceAccount:${PROJNUM}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 2. Build + deploy

```bash
PROJECT=$PROJECT ./deploy.sh
```

Deploys **private**, mounting `alma-secrets` at `~/.streamlit/secrets.toml`.

## 3. Test the private service

```bash
gcloud run services proxy alma-portal --region $REGION   # http://localhost:8080
```

## 4. SSO front door — Cloudflare Access (email logins)

Cloudflare Tunnel to the private service, then a Zero Trust → Access app on
`almamater.empirica-analytics.com` allowing the client's email(s). Cloudflare
handles the email login.

### Single sign-on
Single email login is wired: `check_password()` returns immediately when the
identity proxy sets `Cf-Access-Authenticated-User-Email` (or IAP's
`X-Goog-Authenticated-User-Email`), so clients see **only** Cloudflare's email
login — no second prompt. Keep `dashboard_password` in `alma-secrets` as the
fallback for local/no-proxy access. Refresh the vendored kit after any kit change
with `~/empirica-core/scripts/vendor_into.sh ~/alma-mater-dashboard`.

## 5. Custom domain

Point `almamater.empirica-analytics.com` at the tunnel hostname / domain
mapping. Verify first, then attach DNS, then retire the old SCC app.
