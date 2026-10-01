"""Load the supplied workbook using the same preview/confirmation API as the UI."""
from pathlib import Path
from fastapi.testclient import TestClient
from .main import app

if __name__ == '__main__':
    client = TestClient(app)
    path = Path(__file__).resolve().parents[1] / 'data/produtos-original.xlsx'
    response = client.post('/api/imports/preview', files={'file':(path.name,path.read_bytes())})
    if response.status_code == 409 and response.json()['detail'] == 'Este arquivo já foi importado':
        print('Arquivo original já importado; nenhum dado alterado.')
    else:
        response.raise_for_status()
        result = response.json()
        if result['erros']:
            raise SystemExit(f"Importação interrompida: {result['erros']}")
        confirmation = client.post('/api/imports/'+result['token']+'/confirm',json={})
        confirmation.raise_for_status()
        print(f"{confirmation.json()['importados']} produtos importados com histórico.")
