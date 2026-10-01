"""Business validation shared by manual entry and spreadsheet ingestion."""
from decimal import Decimal, InvalidOperation

CATEGORIES = {'polpas', 'frutas', 'acai-cremes', 'gelo', 'sobremesas', 'salgados', 'peixes'}
UNITS = {'un', 'pacote', 'kg', 'caixa', 'bandeja'}
FIELDS = ['id','nome','categoria','subcategoria','marca','embalagem','unidadeVenda','preco','caixaQuantidade','caixaPreco','foto','disponivel','destaque','descricao','publicar','codigoSistema','ean','status','observacao','estoqueSistema','precoRevenda']

def number(value, field, money=False):
    if value is None or str(value).strip() == '': return None
    try:
        n = Decimal(str(value).strip().replace(',', '.'))
        if not n.is_finite() or n < 0: raise ValueError()
        if money and n != n.quantize(Decimal('.01')): raise ValueError()
        return int(n * 100) if money else float(n)
    except (InvalidOperation, ValueError, OverflowError):
        raise ValueError(f'{field}: informe um número não negativo' + (' com até duas casas decimais' if money else ''))

def boolean(value, field):
    if isinstance(value, bool): return value
    if value is None or value == '': return False
    normalized = str(value).strip().lower()
    if normalized in {'true','1','sim','yes'}: return True
    if normalized in {'false','0','não','nao','no'}: return False
    raise ValueError(f'{field}: informe verdadeiro ou falso')

def validate(raw):
    p = {field: raw.get(field) for field in FIELDS}
    for key in ['id','nome','categoria','unidadeVenda']:
        p[key] = str(p[key] or '').strip()
        if not p[key]: raise ValueError(f'{key}: campo obrigatório')
    if p['categoria'] not in CATEGORIES: raise ValueError('categoria: valor desconhecido')
    if p['unidadeVenda'] not in UNITS: raise ValueError('unidadeVenda: valor desconhecido')
    for key in ['preco','caixaPreco','precoRevenda']: p[key] = number(p[key], key, money=True)
    for key in ['estoqueSistema','caixaQuantidade']: p[key] = number(p[key], key)
    for key in ['disponivel','destaque','publicar']: p[key] = boolean(p[key], key)
    for key in ['codigoSistema','ean']:
        p[key] = str(p[key]).strip() if p[key] is not None else None
        if p[key] == '': p[key] = None
    return p

def external(p):
    p = dict(p)
    for key in ['preco','caixaPreco','precoRevenda']:
        if p.get(key) is not None: p[key] = p[key] / 100
    return p
