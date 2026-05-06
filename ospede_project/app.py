"""
ÔSPEDE — Backend Flask
Rotas: API REST + servir HTML estático
"""

from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
import json, os, uuid, datetime

app = Flask(__name__, static_folder="static")
CORS(app)

# ─────────────────────────────────────────
# DADOS EM MEMÓRIA  (substitui DB por ora)
# ─────────────────────────────────────────
USERS = {}      # email -> {name, email, password_hash, cpf}
RESERVATIONS = {}  # code -> reservation dict

HOTELS = [
    {
        "id": 1,
        "name": "Grand Paulista",
        "location": "Av. Paulista, Bela Vista",
        "region": "Paulista",
        "stars": 5,
        "badge": "Destaque",
        "price": 689,
        "description": (
            "Majestoso hotel de 5 estrelas no coração da Avenida Paulista. "
            "Piscina aquecida panorâmica, spa completo e restaurante assinado "
            "pelo chef Hugo Conti. Vista privilegiada para o skyline da cidade."
        ),
        "amenities": ["Spa", "Piscina", "Academia", "Restaurante", "Bar"],
        "image": "hotel16.jpg",
        "hero_image": "hotel15.jpg",
    },
    {
        "id": 2,
        "name": "Jardins Boutique",
        "location": "R. Haddock Lobo, Jardins",
        "region": "Jardins",
        "stars": 5,
        "badge": "Melhor Avaliado",
        "price": 571,
        "description": (
            "Propriedade boutique de luxo com apenas 42 suítes exclusivas. "
            "Decoração contemporânea brasileira, jardim privativo e serviço "
            "de mordomo 24 horas. Refúgio preferido de executivos e celebridades."
        ),
        "amenities": ["Concierge", "Wi-Fi 1Gb", "Bar Exclusivo"],
        "image": "hotel18.jpg",
        "hero_image": "hotel13.jpg",
    },
    {
        "id": 3,
        "name": "Ibirapuera Palace",
        "location": "Av. Brasil, Ibirapuera",
        "region": "Ibirapuera",
        "stars": 4,
        "badge": None,
        "price": 449,
        "description": (
            "Localizado a 300 metros do Parque Ibirapuera, oferece ambiente "
            "tranquilo com infraestrutura completa para viagens corporativas "
            "e de lazer. Transfer para aeroporto incluso."
        ),
        "amenities": ["Academia", "Wi-Fi", "Transfer", "Café"],
        "image": "hotel17.jpg",
        "hero_image": "hotel19.jpg",
    },
    {
        "id": 4,
        "name": "Vila Madalena Arts Hotel",
        "location": "R. Aspicuelta, Vila Madalena",
        "region": "Pinheiros",
        "stars": 4,
        "badge": "Novo",
        "price": 395,
        "description": (
            "Hotel temático no bairro mais criativo de São Paulo. Quartos "
            "decorados por artistas locais, galeria de arte no lobby e "
            "localização privilegiada próxima a bares e restaurantes badalados."
        ),
        "amenities": ["Arte", "Wi-Fi", "Bar", "Galeria"],
        "image": "hotel8.webp",
        "hero_image": "hotel6.webp",
    },
    {
        "id": 5,
        "name": "Consolação Executive",
        "location": "R. da Consolação, Centro",
        "region": "Paulista",
        "stars": 4,
        "badge": None,
        "price": 371,
        "description": (
            "Hotel business de excelência com salas de reunião modernas, "
            "auditório para 200 pessoas e serviço de secretaria executiva. "
            "Solução completa para viagens corporativas a São Paulo."
        ),
        "amenities": ["Business", "Wi-Fi", "Auditório", "Café"],
        "image": "hotel9.webp",
        "hero_image": "hotel9.webp",
    },
    {
        "id": 6,
        "name": "Higienópolis Grand",
        "location": "Av. Higienópolis, Higienópolis",
        "region": "Jardins",
        "stars": 5,
        "badge": None,
        "price": 749,
        "description": (
            "O hotel mais luxuoso de São Paulo. Suítes de até 320 m², "
            "coleção particular de arte, dois restaurantes premiados e "
            "o spa mais exclusivo da cidade. Uma experiência incomparável."
        ),
        "amenities": ["Spa Ultra", "Piscina Aquecida", "Restaurante", "Lounge VIP"],
        "image": "hotel13.jpg",
        "hero_image": "hotel16.jpg",
    },
    {
        "id": 7,
        "name": "Morumbi Heights",
        "location": "Av. Giovanni Gronchi, Morumbi",
        "region": "Ibirapuera",
        "stars": 4,
        "badge": None,
        "price": 488,
        "description": (
            "Moderno hotel com vista para o Rio Pinheiros e o skyline sul da "
            "cidade. Rooftop bar com coquetéis artesanais e piscina infinity. "
            "Próximo ao Shopping Morumbi e centro empresarial."
        ),
        "amenities": ["Rooftop", "Piscina Infinity", "Wi-Fi", "Academia"],
        "image": "hotel19.jpg",
        "hero_image": "hotel17.jpg",
    },
    {
        "id": 8,
        "name": "Liberdade Orient",
        "location": "Praça da Liberdade, Liberdade",
        "region": "Paulista",
        "stars": 4,
        "badge": "Exclusivo",
        "price": 425,
        "description": (
            "Hotel temático no bairro japonês de SP. Arquitetura inspirada no "
            "Japão, onsen (banho termal) privativo, restaurante de culinária "
            "nipo-brasileira e jardim zen para meditação."
        ),
        "amenities": ["Onsen", "Jardim Zen", "Restaurante", "Wi-Fi"],
        "image": "hotel15.jpg",
        "hero_image": "hotel18.jpg",
    },
]

ROOM_TYPES = [
    {"id": "standard",  "name": "Standard",  "desc": "Cama queen, TV, Wi-Fi, ar-cond.", "extra": 0},
    {"id": "superior",  "name": "Superior",  "desc": "Vista parcial, cama king, cofre.", "extra": 80},
    {"id": "deluxe",    "name": "Deluxe",    "desc": "Vista panorâmica, hidromassagem.", "extra": 160},
    {"id": "suite",     "name": "Suíte",     "desc": "Sala de estar, varanda privativa.", "extra": 260},
]

# ─────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────
def _hash_pass(pw: str) -> str:
    import hashlib
    return hashlib.sha256(pw.encode()).hexdigest()

def _gen_code() -> str:
    return "OSP-" + uuid.uuid4().hex[:8].upper()

# ─────────────────────────────────────────
# ROTAS — HOTÉIS
# ─────────────────────────────────────────
@app.route("/api/hotels", methods=["GET"])
def list_hotels():
    region   = request.args.get("region", "").strip()
    max_price = request.args.get("max_price", type=int)
    stars    = request.args.get("stars", type=int)

    results = HOTELS[:]
    if region:
        results = [h for h in results if h["region"].lower() == region.lower()]
    if max_price:
        results = [h for h in results if h["price"] <= max_price]
    if stars:
        results = [h for h in results if h["stars"] == stars]

    return jsonify({"hotels": results, "total": len(results)})


@app.route("/api/hotels/<int:hotel_id>", methods=["GET"])
def get_hotel(hotel_id):
    hotel = next((h for h in HOTELS if h["id"] == hotel_id), None)
    if not hotel:
        return jsonify({"error": "Hotel não encontrado"}), 404
    return jsonify(hotel)


@app.route("/api/rooms", methods=["GET"])
def list_rooms():
    return jsonify({"rooms": ROOM_TYPES})


# ─────────────────────────────────────────
# ROTAS — AUTH
# ─────────────────────────────────────────
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip().lower()
    cpf      = data.get("cpf", "").strip()
    password = data.get("password", "")

    if not all([name, email, cpf, password]):
        return jsonify({"error": "Preencha todos os campos"}), 400
    if email in USERS:
        return jsonify({"error": "E-mail já cadastrado"}), 409
    if len(password) < 6:
        return jsonify({"error": "Senha muito curta (mínimo 6 caracteres)"}), 400

    cpf_digits = "".join(c for c in cpf if c.isdigit())
    if len(cpf_digits) != 11:
        return jsonify({"error": "CPF inválido"}), 400

    USERS[email] = {
        "name": name,
        "email": email,
        "cpf": cpf_digits,
        "password": _hash_pass(password),
    }
    return jsonify({"message": "Conta criada com sucesso!", "name": name, "email": email}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = USERS.get(email)
    if not user or user["password"] != _hash_pass(password):
        return jsonify({"error": "E-mail ou senha incorretos"}), 401

    return jsonify({"message": "Login realizado!", "name": user["name"], "email": user["email"]}), 200


# ─────────────────────────────────────────
# ROTAS — RESERVAS
# ─────────────────────────────────────────
@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    data = request.get_json(force=True)

    hotel_id  = data.get("hotel_id")
    room_id   = data.get("room_id")
    guests    = data.get("guests", 1)
    checkin   = data.get("checkin")
    checkout  = data.get("checkout")
    payment   = data.get("payment", "Cartão de Crédito")
    email     = data.get("email", "").strip().lower()

    # validações básicas
    if not all([hotel_id, room_id, checkin, checkout]):
        return jsonify({"error": "Dados incompletos"}), 400

    hotel = next((h for h in HOTELS if h["id"] == int(hotel_id)), None)
    if not hotel:
        return jsonify({"error": "Hotel inválido"}), 400

    room = next((r for r in ROOM_TYPES if r["id"] == room_id), None)
    if not room:
        return jsonify({"error": "Tipo de quarto inválido"}), 400

    try:
        ci = datetime.date.fromisoformat(checkin)
        co = datetime.date.fromisoformat(checkout)
        nights = (co - ci).days
        if nights <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Datas inválidas"}), 400

    price_per_night = hotel["price"] + room["extra"]
    total = price_per_night * nights
    code  = _gen_code()

    reservation = {
        "code": code,
        "hotel_id": hotel["id"],
        "hotel_name": hotel["name"],
        "room": room["name"],
        "guests": guests,
        "checkin": checkin,
        "checkout": checkout,
        "nights": nights,
        "price_per_night": price_per_night,
        "total": total,
        "payment": payment,
        "email": email,
        "created_at": datetime.datetime.now().isoformat(),
    }
    RESERVATIONS[code] = reservation
    return jsonify(reservation), 201


@app.route("/api/reservations/<string:code>", methods=["GET"])
def get_reservation(code):
    res = RESERVATIONS.get(code.upper())
    if not res:
        return jsonify({"error": "Reserva não encontrada"}), 404
    return jsonify(res)


@app.route("/api/reservations/by-email/<string:email>", methods=["GET"])
def reservations_by_email(email):
    email = email.strip().lower()
    user_res = [r for r in RESERVATIONS.values() if r.get("email") == email]
    return jsonify({"reservations": user_res})


# ─────────────────────────────────────────
# ROTA — SERVE O FRONT-END
# ─────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    print("=" * 50)
    print("  ÔSPEDE Backend rodando em http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
