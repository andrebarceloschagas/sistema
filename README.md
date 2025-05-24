# Sistema de Anúncios de Veículos

Este sistema permite o cadastro e gerenciamento de veículos e anúncios de venda. Os usuários podem publicar, pesquisar e gerenciar seus anúncios, enquanto administradores têm acesso a funcionalidades especiais.

## Tecnologias utilizadas

- Django 4.x
- Python 3.x
- Django Rest Framework (API REST)
- Bootstrap 5 (frontend)
- SQLite (desenvolvimento) / PostgreSQL (produção)

## Estrutura do projeto

O projeto contém duas principais aplicações (apps) Django:

- **veiculo**: Gerenciamento de veículos, incluindo cadastro, edição e listagem
- **anuncio**: Gerenciamento de anúncios de venda de veículos

## Funcionalidades

### Veículos

- Cadastro de veículos com informações detalhadas (marca, modelo, ano, etc.)
- Upload de fotos
- Validação de dados (placa, chassi, quilometragem)
- Categorização automática (novo, seminovo, usado, antigo)
- API REST para consultas

### Anúncios

- Criação de anúncios relacionados a veículos
- Sistema de status (ativo, vendido, pausado, expirado)
- Controle de visualizações
- Anúncios destacados
- Filtros por marca, preço, ano, etc.
- API REST para consultas

## Instalação

### Requisitos

- Python 3.x
- pip
- virtualenv (opcional, mas recomendado)

### Passos para instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/sistema.git
cd sistema
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```
cd web
pip install -r requirements.txt
```

4. Configure o banco de dados:
```
python manage.py migrate
```

5. Crie um superusuário:
```
python manage.py createsuperuser
```

6. Execute o servidor de desenvolvimento:
```
python manage.py runserver
```

7. Acesse o sistema em http://localhost:8000

## API REST

### Endpoints disponíveis

#### Veículos
- `GET /veiculo/api/` - Lista todos os veículos
- Parâmetros de filtro: marca, ano, combustivel

#### Anúncios
- `GET /anuncio/api/` - Lista todos os anúncios
- `GET /anuncio/api/<id>/` - Detalhes de um anúncio específico
- Parâmetros de filtro: status, preco_min, preco_max, marca, ano

### Autenticação

Todas as APIs requerem autenticação por token. Para obter um token:

```
curl -X POST http://localhost:8000/api-token-auth/ -d "username=seu_usuario&password=sua_senha"
```

Para usar o token nas requisições:

```
curl -H "Authorization: Token seu-token-aqui" http://localhost:8000/anuncio/api/
```

## Testes

Para executar os testes:

```
pytest
```

## Permissões

O sistema inclui as seguintes permissões personalizadas:

### Veículos:
- `can_view_detailed_info` - Visualizar informações detalhadas
- `can_export_veiculos` - Exportar lista de veículos

### Anúncios:
- `can_feature_anuncio` - Destacar anúncios
- `can_view_all_anuncios` - Visualizar todos os anúncios
- `can_export_anuncios` - Exportar anúncios

## Contribuição

Contribuições são bem-vindas! Por favor, siga estas etapas:

1. Crie um fork do repositório
2. Crie sua branch de funcionalidade (`git checkout -b minha-nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adicionando nova funcionalidade'`)
4. Push para a branch (`git push origin minha-nova-funcionalidade`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT.
