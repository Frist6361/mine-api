
# Minecraft API
![5fe56758-0c7e-4223-afd3-140bc0173b17](https://github.com/user-attachments/assets/33dbb4d5-3f57-47ab-9d40-4eb3d5fe46ed) ![9b14c44e-94a6-4c24-9640-a66f7bb34b06](https://github.com/user-attachments/assets/afbb6a6f-bc6c-405b-84ea-398c4387a801)


An API for retrieving Minecraft player skins and item images.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Frist6361/mine-api.git
cd mine-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Usage

### Retrieving Player Skin

1. Get the front of the skin:
```
GET /skin/{nickname}/front
```

2. Get the back of the skin:
```
GET /skin/{nickname}/back
```

3. Get the head of the skin:
```
GET /skin/{nickname}/head
```

Example:
```bash
curl http://localhost:8000/skin/Fristikon/front
```

### Retrieving Item Images

1. Get a list of all available items:
```
GET /items
```

2. Get an image of a specific item:
```
GET /item/{item_name}
```

3. Get an image of a block:
```
GET /block/{block_name}
```

The item or block name should be in snake_case format, for example: `diamond_sword` or `hanging_roots`.

Examples:
```bash
# Get a list of all items
curl http://localhost:8000/items

# Get an image of a diamond sword
curl http://localhost:8000/item/diamond_sword

# Get an image of a grass block
curl http://localhost:8000/block/hanging_roots
```

## API Documentation

After starting the server, the API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Data Sources

- Player skins: Official Mojang API
- Item textures: Local textures from downloaded files

## License

MIT
