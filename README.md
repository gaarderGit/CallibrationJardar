# Calibration App

This repository contains a Dash application defined in **`app_calibrate.py`**.

The project is managed with **[uv](http://docs.astral.sh/uv)**.

## Prerequisites

* **[uv](https://docs.astral.sh/uv/getting-started/installation/)** installed on your system
* **[git](https://git-scm.com)** installed on your system

## Project Installation

Clone the repository and move into the project directory:

```bash
git clone git@github.com:gaarderGit/CallibrationJardar.git
cd CallibrationJardar
```

Install all dependencies defined in `pyproject.toml` using **uv**:

```bash
uv sync
```

Create a file named `.env` in the project root containing app secrets with the following lines (replace `***`):

```
DB_HOST=***
DB_USER=***
DB_PASSWORD=***
DB_PORT=***
ENTSOE_SECURITY_TOKEN=***
```

## Running the Dash App

Before running the app, we need to download ENTSO-E data:

```bash
uv run entsoe.py
```

The Dash application entry point is **`app_calibrate.py`**.

Run the app:

```bash
uv run app_calibrate.py
```

Once started, open app at http://127.0.0.1:8080.
