from fastapi import FastAPI, HTTPException
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import base64
from io import BytesIO
from PIL import Image
import json
import os
from pathlib import Path

app = FastAPI(
    title="Minecraft API",
    description="API for getting player skins and images of Minecraft items",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOJANG_API_URL = "https://api.mojang.com/users/profiles/minecraft/"
TEXTURE_API_URL = "https://sessionserver.mojang.com/session/minecraft/profile/"

ICONS_DIR = Path("icons")
ITEMS_DIR = ICONS_DIR / "item"
BLOCKS_DIR = ICONS_DIR / "block"

def get_available_items():
    """Get a list of all available items"""
    items = []
    
    for file in ITEMS_DIR.glob("*.png"):
        if any(x in file.name for x in ['overlay', 'pulling', 'standby', 'cast', '_empty']):
            continue
        items.append(file.stem)
    
    return sorted(items)

def get_item_path(item_name: str) -> Path:
    """Get the path to the item texture"""
    item_path = ITEMS_DIR / f"{item_name}.png"
    if item_path.exists():
        return item_path

        
    return None

def get_available_blocks():
    """Get a list of all available blocks"""
    blocks = []
    
    for file in BLOCKS_DIR.glob("*.png"):
        blocks.append(file.stem)
    
    return sorted(blocks)

def get_skin_url(nickname: str) -> str:
    response = requests.get(f"{MOJANG_API_URL}{nickname}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="The player was not found")
    elif response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error accessing the Mojang API")
    
    player_data = response.json()
    uuid = player_data["id"]
    
    profile_response = requests.get(f"{TEXTURE_API_URL}{uuid}")
    if profile_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error when receiving skin data")
    
    profile_data = profile_response.json()
    
    try:
        textures = json.loads(base64.b64decode(profile_data["properties"][0]["value"]))
        return textures["textures"]["SKIN"]["url"]
    except (KeyError, json.JSONDecodeError, base64.binascii.Error):
        raise HTTPException(status_code=500, detail="Error when getting the skin URL")

def get_skin_image(skin_url: str) -> Image.Image:
    response = requests.get(skin_url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error loading the skin")
    return Image.open(BytesIO(response.content))

@app.get("/")
async def read_root():
    return {"message": "API working!"}

@app.get("/skin/{nickname}/front")
async def get_skin_front(nickname: str):
    try:
        skin_url = get_skin_url(nickname)
        skin = get_skin_image(skin_url)
        
        front = Image.new('RGBA', (16, 32))
        front.paste(skin.crop((8, 8, 16, 16)), (4, 0))
        front.paste(skin.crop((20, 20, 28, 32)), (4, 8))
        front.paste(skin.crop((44, 20, 48, 32)), (0, 8))
        front.paste(skin.crop((36, 52, 40, 64)), (12, 8))
        front.paste(skin.crop((4, 20, 8, 32)), (4, 20))
        front.paste(skin.crop((20, 52, 24, 64)), (8, 20))
        
        img_byte_arr = BytesIO()
        front = front.resize((160, 320), Image.Resampling.NEAREST)  
        front.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skin/{nickname}/back")
async def get_skin_back(nickname: str):
    try:
        skin_url = get_skin_url(nickname)
        skin = get_skin_image(skin_url)
        
        back = Image.new('RGBA', (16, 32))
        back.paste(skin.crop((24, 8, 32, 16)), (4, 0))
        back.paste(skin.crop((32, 20, 40, 32)), (4, 8))
        back.paste(skin.crop((52, 20, 56, 32)), (0, 8))
        back.paste(skin.crop((44, 52, 48, 64)), (12, 8))
        back.paste(skin.crop((12, 20, 16, 32)), (4, 20))
        back.paste(skin.crop((28, 52, 32, 64)), (8, 20))
        
        img_byte_arr = BytesIO()
        back = back.resize((160, 320), Image.Resampling.NEAREST)  
        back.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skin/{nickname}/head")
async def get_skin_head(nickname: str):
    try:
        skin_url = get_skin_url(nickname)
        skin = get_skin_image(skin_url)
        
        head = Image.new('RGBA', (8, 8))
        head.paste(skin.crop((8, 8, 16, 16)), (0, 0))
        
        img_byte_arr = BytesIO()
        head = head.resize((160, 160), Image.Resampling.NEAREST)  
        head.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skin/{nickname}")
async def get_skin_info(nickname: str):
    try:
        response = requests.get(f"{MOJANG_API_URL}{nickname}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="The player was not found")
        elif response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error accessing the Mojang API")
        
        player_data = response.json()
        uuid = player_data["id"]
        
        profile_response = requests.get(f"{TEXTURE_API_URL}{uuid}")
        if profile_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error when receiving skin data")
        
        profile_data = profile_response.json()
        
        return {
            "nickname": nickname,
            "uuid": uuid,
            "profile_data": profile_data
        }
        
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Error accessing the server")

@app.get("/items")
async def list_items():
    """Get a list of all available items"""
    return {"items": get_available_items()}

@app.get("/blocks")
async def list_blocks():
    """Get a list of all available blocks"""
    return {"blocks": get_available_blocks()}

@app.get("/item/{item_name}")
async def get_item_image(item_name: str):
    """
    Get the image of an item by its name.
    Item names should be in snake_case, for example: diamond_sword
    """
    try:
        item_name = item_name.lower().replace(" ", "_")
        
        item_path = get_item_path(item_name)
        if not item_path:
            raise HTTPException(
                status_code=404,
                detail=f"The item '{item_name}' was not found. Use /items to get a list of available items."
            )
        
        image = Image.open(item_path)
        
        image = image.resize((image.width * 8, image.height * 8), Image.Resampling.NEAREST)
        
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/block/{block_name}")
async def get_block_image(block_name: str):
    """
    Get an image of a block by its name.
    Block names should be in snake_case format, for example: hanging_roots
    """
    try:
        block_name = block_name.lower().replace(" ", "_")
        
        block_path = BLOCKS_DIR / f"{block_name}.png"
        if not block_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"The block '{block_name}' was not found. Use /blocks to get a list of available blocks."
            )
        
        image = Image.open(block_path)
        
        image = image.resize((image.width * 8, image.height * 8), Image.Resampling.NEAREST)
        
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
