
# Saúde Connect

## Como rodar o backend

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure a variável `DATABASE_URL` no `.env`.

3. Inicie o servidor:
   ```
   flask run
   ```

## Como rodar o frontend

Abra `static/activities.html` no navegador.

## Como rodar os testes

1. Instale pytest:
   ```
   pip install pytest pytest-flask
   ```

2. Execute os testes:
   ```
   pytest tests/
   ```
