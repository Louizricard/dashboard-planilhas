import csv
import io
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from app import main


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_path = main.DB_PATH
        main.DB_PATH = Path(self.temp.name) / 'test.sqlite3'
        main.previews.clear()
        self.client = TestClient(main.app)

    def tearDown(self):
        main.DB_PATH = self.original_path
        main.previews.clear()
        self.temp.cleanup()

    def preview(self, rows):
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=['id','nome','categoria','unidadeVenda','preco','codigoSistema'])
        writer.writeheader()
        writer.writerows(rows)
        return self.client.post('/api/imports/preview', files={'file':('produtos.csv',stream.getvalue(),'text/csv')})

    def row(self, identifier='polpa-1', **kwargs):
        return {'id':identifier,'nome':'Polpa','categoria':'polpas','unidadeVenda':'pacote','preco':'30,50','codigoSistema':'001', **kwargs}

    def test_real_workbook_roundtrip_and_idempotency(self):
        data = (Path(__file__).resolve().parents[1] / 'data/produtos-original.xlsx').read_bytes()
        result = self.client.post('/api/imports/preview', files={'file':('produtos.xlsx',data)}).json()
        self.assertEqual(result['validos'],154)
        self.assertEqual(result['erros'],[])
        self.assertEqual(self.client.get('/api/products').json(),[])
        confirmation = self.client.post('/api/imports/'+result['token']+'/confirm',json={})
        self.assertEqual(confirmation.status_code,200)
        products = self.client.get('/api/products').json()
        self.assertEqual(len(products),154)
        self.assertEqual(sum(p['status']=='Conferir' for p in products),29)
        self.assertEqual(sum(p['estoqueSistema']==0 for p in products),100)
        self.assertEqual(self.client.post('/api/imports/preview',files={'file':('again.xlsx',data)}).status_code,409)
        export = self.client.get('/api/export')
        self.assertEqual(export.status_code,200)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(export.content.decode('utf-8-sig')),delimiter=';'))),154)
        self.assertEqual(len(self.client.get('/api/imports').json()),1)

    def test_partial_requires_explicit_confirmation(self):
        preview = self.preview([self.row(),self.row('bad',preco='-1',codigoSistema='002')]).json()
        self.assertEqual(preview['validos'],1)
        self.assertEqual(preview['erros'][0]['linha'],3)
        url = '/api/imports/'+preview['token']+'/confirm'
        self.assertEqual(self.client.post(url,json={}).status_code,422)
        self.assertEqual(self.client.get('/api/products').json(),[])
        self.assertEqual(self.client.post(url,json={'permitirParcial':True}).status_code,200)
        self.assertEqual(len(self.client.get('/api/imports').json()[0]['errors']),1)

    def test_stale_preview_rolls_back_entire_import(self):
        preview = self.preview([self.row('first',codigoSistema='002'),self.row()]).json()
        self.assertEqual(self.client.post('/api/products',json=self.row()).status_code,201)
        result = self.client.post('/api/imports/'+preview['token']+'/confirm',json={})
        self.assertEqual(result.status_code,409)
        self.assertEqual(len(self.client.get('/api/products').json()),1)
        self.assertEqual(self.client.get('/api/imports').json(),[])

    def test_edit_audited_and_identity_preserved(self):
        product = self.row()
        self.client.post('/api/products',json=product)
        product['preco'] = '35.00'
        self.assertEqual(self.client.put('/api/products/polpa-1',json=product).status_code,200)
        self.assertEqual(self.client.get('/api/products').json()[0]['preco'],35)
        events = self.client.get('/api/products/polpa-1/history').json()
        self.assertEqual([e['action'] for e in events],['update','create'])
        product['id']='changed'
        self.assertEqual(self.client.put('/api/products/polpa-1',json=product).status_code,422)

    def test_validation_and_duplicate_code(self):
        for invalid in ['NaN','Infinity','-2','0.001']:
            self.assertEqual(self.client.post('/api/products',json=self.row(preco=invalid)).status_code,422)
        self.assertEqual(self.client.post('/api/products',json=self.row()).status_code,201)
        self.assertEqual(self.client.post('/api/products',json=self.row('other')).status_code,409)
        result = self.preview([self.row('new',codigoSistema='003'),self.row('new',codigoSistema='004')]).json()
        self.assertEqual(result['validos'],1)
        self.assertEqual(len(result['erros']),1)

    def test_formula_injection_export_and_unsupported_file(self):
        self.client.post('/api/products',json=self.row(nome='=HYPERLINK("evil")'))
        self.assertIn("'=HYPERLINK",self.client.get('/api/export').text)
        self.assertEqual(self.client.post('/api/imports/preview',files={'file':('file.xls',b'bad')}).status_code,422)
        self.assertEqual(self.client.post('/api/imports/preview',files={'file':('file.xlsx',b'bad')}).status_code,422)

    def test_ui_assets_served(self):
        for url in ['/','/static/app.js','/static/app.css','/static/brand/frutmar-logo-horizontal.svg']:
            self.assertEqual(self.client.get(url).status_code,200)

if __name__ == '__main__': unittest.main()
