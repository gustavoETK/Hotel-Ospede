# ÔSPEDE — Sistema de Reservas de Hotéis

## 📁 Estrutura

```
ospede_project/
├── app.py              ← Backend Flask (API REST)
├── index.html          ← Frontend (SPA completo)
├── requirements.txt    ← Dependências Python
├── static/
│   ├── images/         ← Fotos dos hotéis
│   └── fonts/          ← ZonaPro (Zona Pro Bold/Light)
└── README.md
```

## 🚀 Rodando o projeto

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor

```bash
python app.py
```

### 3. Abrir no navegador

```
http://localhost:5000
```

---

## 🌐 API — Endpoints disponíveis

### Hotéis
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/hotels` | Lista todos os hotéis |
| GET | `/api/hotels?region=Jardins` | Filtra por região |
| GET | `/api/hotels?max_price=500` | Filtra por preço máximo |
| GET | `/api/hotels/<id>` | Detalhes de um hotel |
| GET | `/api/rooms` | Tipos de quarto disponíveis |

### Autenticação
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/register` | Criar conta |
| POST | `/api/auth/login` | Login |

### Reservas
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/reservations` | Criar reserva |
| GET | `/api/reservations/<code>` | Buscar por código |
| GET | `/api/reservations/by-email/<email>` | Reservas do usuário |

---

## 📋 Exemplos de uso da API (curl)

**Listar hotéis:**
```bash
curl http://localhost:5000/api/hotels
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","password":"minha_senha"}'
```

**Criar reserva:**
```bash
curl -X POST http://localhost:5000/api/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": 1,
    "room_id": "deluxe",
    "guests": 2,
    "checkin": "2025-06-10",
    "checkout": "2025-06-13",
    "payment": "PIX",
    "email": "teste@email.com"
  }'
```

---

## 💡 Funcionamento sem Backend

O frontend possui dados embutidos como fallback. Se o servidor Flask não estiver rodando, a página funciona normalmente com dados estáticos — basta abrir o `index.html` diretamente no navegador.

---

## 🎨 Design

Inspirado no layout **hotel_hero-main**:
- Hero slider full-screen com transição suave
- Fontes **Zona Pro** (Bold/Light) + **Cormorant Garamond**
- Paleta: preto profundo + dourado elegante (#c9a84c)
- Navbar transparente → sólida ao rolar
- Cards com imagens reais e hover animado
- Modais com fluxo multi-step para reservas

---

## 🔧 Notas Técnicas

- **Dados em memória**: os usuários e reservas são armazenados em dicionários Python. Para persistência, substitua por SQLite ou PostgreSQL.
- **Sem autenticação JWT**: o login retorna os dados do usuário diretamente. Para produção, implemente tokens JWT.
- **CORS habilitado**: o frontend pode rodar em qualquer porta durante desenvolvimento.
