---
name: dify-import-export
description: "Dify app import/export mechanics. Use when deploying generated DSL YAML to a running Dify instance, exporting existing apps, or handling import errors."
---

# Dify Import/Export

How to get DSL YAML into and out of a running Dify instance.

## Import App from YAML

### Endpoint
```
POST /console/api/apps/imports
Content-Type: application/json
Authorization: Bearer <console_token>
```

### Request Body
```json
{
  "mode": "yaml-content",
  "yaml_content": "<full YAML string>"
}
```

### Modes
| Mode | Description |
|------|-------------|
| `yaml-content` | Direct YAML string in request body |
| `yaml-url` | URL to fetch YAML from (supports GitHub blob URLs) |

### Response States
| Status | Meaning | Action |
|--------|---------|--------|
| `COMPLETED` | Import successful | App is ready |
| `COMPLETED_WITH_WARNINGS` | Imported with minor version mismatch | Check warnings |
| `PENDING` | Version compatibility issue | Call confirm endpoint |
| `FAILED` | Import error | Check error message |

### Confirm Pending Import
```
POST /console/api/apps/imports/<import_id>/confirm
Authorization: Bearer <console_token>
```

## Export App to YAML

### Endpoint
```
GET /console/api/apps/<app_id>/export
Authorization: Bearer <console_token>
```

### Query Parameters
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `include_secret` | bool | false | Include credentials/secrets |

### Response
Returns the DSL YAML as a string.

## Check Dependencies

After import, verify all plugins are available:
```
GET /console/api/apps/imports/<app_id>/check-dependencies
Authorization: Bearer <console_token>
```

## Important Notes

1. **Max size**: 10MB per DSL file
2. **Dataset IDs**: Encrypted with AES-CBC on export, decrypted on import (same tenant)
3. **Credentials**: Stripped by default on export — tools need re-authorization after import
4. **Triggers**: Schedule configs reset, webhook URLs cleared on export (security)
5. **GitHub URLs**: Blob URLs auto-converted to raw URLs for fetching

## Workflow for Deploying Generated Apps

```
1. Generate DSL YAML (using dify-workflow-patterns + dify-dsl-expert)
2. Validate locally (check structure, selectors, mode consistency)
3. Replace placeholders:
   - DATASET_ID_PLACEHOLDER → real dataset UUIDs
   - Model provider/name → available models in target instance
4. Import via API or paste in Dify console UI
5. If PENDING: confirm import
6. Check dependencies: install missing plugins
7. Test the app in Dify
```

## Getting a Console Token

The import API requires a console (admin) token, not an app API token.

Options:
- Use the token from your browser session (inspect network requests in Dify console)
- Use the Dify API with proper authentication
- For local dev: check the Dify console login flow

## File-Based Import (Alternative)

If you have direct access to the Dify instance:
1. Save DSL as `.yml` file
2. In Dify console: Studio → Import DSL File
3. Select the file and confirm
