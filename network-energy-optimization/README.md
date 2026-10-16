# Network Energy Optimization — Exploratory Prototype

An experimental Python/Flask project exploring how occupancy and motion events could inform Cisco Meraki switch-port schedules and potentially reduce unnecessary network-connected device energy use. Developed as a technical proof of concept; **no measured energy savings or production readiness is claimed**.

## What is included

- `app_run.py`: Flask UI, network provisioning and motion event handlers.
- `update_scheduler.py`: prototype Meraki switch scheduling operations.
- `templates/`, `static/`: web interface and assets.
- `motion_modeling/`: exploratory model training, testing and evaluation scripts.
- `databases/`: simulated-data generators and visualization scripts.
- `scripts_setup/`: experimental database setup helper.

## Setup (development only)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Environment variables are read by `config.py`; a `.env` file is **not automatically loaded**. Export variables into your shell or use an environment loader. For example:

```bash
export FLASK_SECRET_KEY=local-development-only
python app_run.py
```

The UI can load without an API key; live Meraki operations require authorized credentials. **All non-GET routes are blocked by default**. Never enable live operations against a production network without independently reviewing and testing the implementation. This prototype includes device claiming, schedule changes and network deletion.

## Project status and limitations

This is a **preserved experimental prototype**, not a tested deployable product. Original local databases, generated model weights, hard-coded organization/device identifiers, and private notes have been excluded from the public package. Some scripts depend on databases and schemas not included in this release, and certain scripts still need portability and integration work. ML experiments are not proven to drive the live scheduling logic. No automated test suite or validated energy-impact study is included.

## Security

A credential was present in the original private source archive. **Revoke/rotate it before publishing or using this project.** The credential is not included in this repository package. Do not commit local `.env`, database files, or real device identifiers.

## Why I built it

To explore whether an existing enterprise networking platform could support a new energy-management use case by combining network APIs, motion events, historical patterns and automation. The commercial potential remains a hypothesis requiring measurement, operational-risk analysis and validation.
