# Contributing

Thanks for considering a contribution.

Quick start:

- Create and activate the virtualenv:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

- Run tests:

```powershell
pytest -q
```

- Run format and checks (if pre-commit installed):

```powershell
.venv\Scripts\python.exe -m pre_commit run --all-files
```
