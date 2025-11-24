# PorttuSmart - Sistema de Gestão de Condomínios

![PorttuSmart Logo](static/logo.png)

## 📋 Sobre o Projeto

PorttuSmart é um sistema completo de gestão de condomínios desenvolvido com Django REST Framework. O sistema facilita a comunicação entre moradores e administração, oferecendo funcionalidades abrangentes para gestão de visitantes, finanças, reservas de áreas comuns, ocorrências, encomendas e muito mais.

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.11+**
- **Django 5.2.7** - Framework web principal
- **Django REST Framework 3.16.1** - API REST
- **PostgreSQL** - Banco de dados principal
- **Gunicorn 23.0.0** - Servidor WSGI para produção

### Autenticação e Segurança
- **Django Allauth 65.13.0** - Autenticação social (Google)
- **dj-rest-auth 7.0.1** - Autenticação via API
- **djangorestframework-simplejwt 5.5.1** - Autenticação JWT
- **Google reCAPTCHA** - Proteção contra bots

### Documentação API
- **drf-yasg 1.21.11** - Documentação Swagger/OpenAPI
- **drf-spectacular 0.29.0** - Geração de schema OpenAPI

### Outras Bibliotecas
- **django-cors-headers 4.9.0** - CORS para APIs
- **django-filter 25.2** - Filtragem avançada
- **django-stdimage 6.0.2** - Processamento de imagens
- **django-unfold 1.0.0** - Interface administrativa moderna
- **Pillow 12.0.0** - Manipulação de imagens
- **psycopg2-binary 2.9.11** - Adaptador PostgreSQL
- **pdfplumber 0.11.7** - Processamento de PDFs
- **huggingface-hub 1.0.1** - Integração com modelos de IA

## 📁 Estrutura do Projeto

```
github/
├── condomineo/              # Configurações principais do projeto
│   ├── settings.py          # Configurações do Django
│   ├── urls.py              # URLs principais
│   ├── api_urls.py          # URLs da API
│   ├── wsgi.py              # Configuração WSGI
│   └── asgi.py              # Configuração ASGI
│
├── core/                    # App principal com modelos de negócio
│   ├── models.py            # Modelos: Condomínio, Apartamento, Visitante, etc.
│   ├── views.py             # Views da aplicação
│   ├── serializers.py       # Serializers para API
│   ├── permissions.py       # Permissões customizadas
│   ├── filters.py           # Filtros para queryset
│   ├── forms.py             # Formulários
│   ├── services_ia.py       # Serviços de IA
│   ├── admin.py             # Configuração do admin
│   └── urls.py              # URLs do app
│
├── users/                   # App de gerenciamento de usuários
│   ├── models.py            # Modelo Person (usuário customizado)
│   ├── views.py             # Views de autenticação e usuários
│   ├── serializers.py       # Serializers de usuários
│   ├── permissions.py       # Permissões de usuários
│   ├── authentication.py    # Autenticação customizada
│   ├── adapters.py          # Adaptadores do allauth
│   ├── services.py          # Serviços de usuários
│   ├── signals.py           # Signals do Django
│   └── forms.py             # Formulários de usuários
│
├── utils/                   # Utilitários compartilhados
│   ├── utils.py             # Funções auxiliares
│   └── validators.py        # Validadores customizados
│
├── templates/               # Templates HTML
│   ├── account/             # Templates de autenticação
│   ├── emails/              # Templates de e-mail
│   └── pages/               # Páginas do site
│
├── static/                  # Arquivos estáticos
│   └── logo.png             # Logo do projeto
│
├── staticfiles/             # Arquivos estáticos coletados
│
├── media/                   # Arquivos de mídia (uploads)
│   └── notice_files/        # Arquivos de avisos
│
├── database_schema.dbml     # Esquema do banco de dados
├── Dockerfile               # Configuração Docker
├── requirements.txt         # Dependências Python
├── manage.py                # Script de gerenciamento Django
└── README.md                # Este arquivo
```

## 🗄️ Modelos de Dados

### App: Users
- **Person** - Modelo de usuário customizado com tipos: Morador, Funcionário e Administrador

### App: Core
- **Condominium** - Condomínios gerenciados pelo sistema
- **Address** - Endereços dos condomínios
- **Apartment** - Apartamentos com informações de ocupação
- **Visitor** - Cadastro de visitantes
- **Visit** - Registro de visitas aos apartamentos
- **Occurrence** - Ocorrências e problemas reportados
- **Reservation** - Reservas de áreas comuns (salão, churrasqueira, etc.)
- **Finance** - Controle financeiro (receitas e despesas)
- **Vehicle** - Cadastro de veículos dos moradores
- **Order** - Controle de encomendas
- **Notice** - Avisos e comunicados
- **Communication** - Sistema de mensagens internas
- **Resident** - Dependentes/moradores secundários

## 🔐 Tipos de Usuários e Permissões

### 1. **Administrador (Admin)**
- Gerencia múltiplos condomínios
- Acesso total ao sistema
- Pode criar outros usuários
- Ativo por padrão

### 2. **Funcionário (Employee)**
- Vinculado a um condomínio específico
- Gerencia visitantes, encomendas, ocorrências
- Precisa de aprovação para ativar conta

### 3. **Morador (Resident)**
- Vinculado a um apartamento específico
- Pode fazer reservas, reportar ocorrências
- Visualiza avisos e comunicados
- Precisa de aprovação para ativar conta

## 🌟 Principais Funcionalidades

### Gestão de Visitantes
- Cadastro de visitantes por CPF
- Registro de entrada e saída
- Histórico de visitas por apartamento
- Observações e notas

### Controle de Acesso
- Cadastro de veículos
- Controle de encomendas
- Sistema de assinaturas digitais
- Notificações de recebimento

### Áreas Comuns
- Reserva de espaços (salão de festas, churrasqueira, piscina, quadra, playground, academia)
- Controle de conflitos de horários
- Histórico de reservas

### Financeiro
- Registro de receitas e despesas
- Upload de comprovantes
- Relatórios financeiros
- Auditoria de transações

### Comunicação
- Avisos gerais
- Mensagens direcionadas
- Broadcast para todos os moradores
- Anexos em comunicados

### Ocorrências
- Abertura de chamados
- Acompanhamento de status
- Histórico completo
- Priorização

## 🔧 Configuração e Instalação

### Pré-requisitos
- Python 3.11 ou superior
- PostgreSQL
- pip (gerenciador de pacotes Python)
- Docker (opcional)

### Instalação Local

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd github
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
Crie um arquivo `.env` na raiz do projeto:
```env
SECRET=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOST=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
DATABASE_URL=postgres://usuario:senha@localhost:5432/portusmart
GOOGLE_RECAPTCHA_SECRET_KEY=sua-chave-recaptcha
```

5. **Execute as migrações**
```bash
python manage.py migrate
```

6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

7. **Colete os arquivos estáticos**
```bash
python manage.py collectstatic
```

8. **Inicie o servidor**
```bash
python manage.py runserver
```

O sistema estará disponível em `http://localhost:8000`

### Instalação com Docker

```bash
docker build -t portusmart .
docker run -p 8000:8000 portusmart
```

## 📡 Endpoints da API

A documentação completa da API está disponível em:
- **Swagger UI**: `/api/v1/swagger/`
- **ReDoc**: `/api/v1/redoc/`
- **Schema OpenAPI**: `/api/v1/schema/`

### Principais Endpoints

#### Autenticação
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/google/` - Login com Google
- `POST /api/v1/auth/password/change/` - Alterar senha
- `POST /api/v1/auth/password/reset/` - Resetar senha

#### Usuários
- `GET /api/v1/users/` - Listar usuários
- `POST /api/v1/users/` - Criar usuário
- `GET /api/v1/users/{id}/` - Detalhes do usuário
- `PUT /api/v1/users/{id}/` - Atualizar usuário
- `DELETE /api/v1/users/{id}/` - Deletar usuário

#### Core (Condomínios, Apartamentos, etc.)
- `/api/v1/core/condominiums/` - Condomínios
- `/api/v1/core/apartments/` - Apartamentos
- `/api/v1/core/visitors/` - Visitantes
- `/api/v1/core/visits/` - Visitas
- `/api/v1/core/occurrences/` - Ocorrências
- `/api/v1/core/reservations/` - Reservas
- `/api/v1/core/finances/` - Finanças
- `/api/v1/core/vehicles/` - Veículos
- `/api/v1/core/orders/` - Encomendas
- `/api/v1/core/notices/` - Avisos
- `/api/v1/core/communications/` - Comunicações

## 🎨 Interface Administrativa

O projeto utiliza o tema **Django Unfold** para uma interface administrativa moderna e intuitiva.

Acesse em: `/painel/`

## 🔒 Segurança

- Autenticação JWT com refresh tokens
- Proteção CSRF
- CORS configurável
- Validação com Google reCAPTCHA
- Senhas hasheadas
- Permissões granulares por tipo de usuário

## 🧪 Testes

```bash
python manage.py test
```

## 📊 Banco de Dados

O projeto utiliza PostgreSQL como banco de dados principal. O esquema completo está documentado no arquivo `database_schema.dbml` e pode ser visualizado em [dbdiagram.io](https://dbdiagram.io/).

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob licença proprietária. Todos os direitos reservados.

## 👥 Equipe

**PorttuSmart Team**

## 📞 Contato

Para dúvidas ou suporte, entre em contato através do e-mail: [seu-email@example.com]


## 📸 Screenshots

*Adicione screenshots da aplicação aqui*

---

**Versão**: 1.0.0  
**Última atualização**: Novembro de 2025

