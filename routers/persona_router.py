from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pathlib import Path
import json
import shutil

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent / 'personas'

@router.get('/personas/{scope}/{name}')
def read_persona(scope: str, name: str):
    if scope not in ['local', 'shared']:
        raise HTTPException(status_code=400, detail='Invalid scope')
    persona_path = BASE_DIR / scope / name / 'persona.json'
    if not persona_path.exists():
        raise HTTPException(status_code=404, detail='Persona not found')
    with open(persona_path, 'r') as f:
        persona = json.load(f)
    if 'moderated' not in persona:
        persona['moderated'] = False
    return persona

@router.get('/personas/{scope}')
def list_personas(scope: str):
    if scope not in ['local', 'shared']:
        raise HTTPException(status_code=400, detail='Invalid scope')
    scope_dir = BASE_DIR / scope
    personas = [p.name for p in scope_dir.iterdir() if p.is_dir()]
    return [{'name': name} for name in personas]

@router.post('/personas/{scope}')
def create_persona(scope: str, persona: str = Form(...), faceref: UploadFile = File(None), avatar: UploadFile = File(None)):
    try:
        print("In create_persona")
        print("scope is ", scope)
        persona = json.loads(persona)

        print("persona is ", persona)

        if scope not in ['local', 'shared']:
            raise HTTPException(status_code=400, detail='Invalid scope')
        persona_name = persona.get('name')
        if not persona_name:
            raise HTTPException(status_code=400, detail='Persona name is required')
        persona_path = BASE_DIR / scope / persona_name / 'persona.json'
        if persona_path.exists():
            raise HTTPException(status_code=400, detail='Persona already exists')
        persona_path.parent.mkdir(parents=True, exist_ok=True)

        # Create target directory
        target_dir = Path(f'/files/ah/static/personas/{persona_name}')
        target_dir.mkdir(parents=True, exist_ok=True)

        if faceref:
            print("Trying to save faceref")
            faceref_path = persona_path.parent / 'faceref.png'
            print("faceref path is ", faceref_path)
            with open(faceref_path, 'wb') as f:
                print("opened file for writing")
                f.write(faceref.file.read())
            # Copy faceref to new location
            new_faceref_path = target_dir / 'faceref.png'
            shutil.copy2(faceref_path, new_faceref_path)
            persona['faceref'] = str(new_faceref_path)

        if avatar:
            print("Trying to save avatar")
            avatar_path = persona_path.parent / 'avatar.png'
            with open(avatar_path, 'wb') as f:
                print("opened file for writing")
                f.write(avatar.file.read())
            # Copy avatar to new location
            new_avatar_path = target_dir / 'avatar.png'
            shutil.copy2(avatar_path, new_avatar_path)
            persona['avatar'] = str(new_avatar_path)

        with open(persona_path, 'w') as f:
            json.dump(persona, f, indent=2)
        return {'status': 'success'}

    except Exception as e:
        print("Error in create_persona")
        raise HTTPException(status_code=500, detail='Internal server error ' + str(e))

                
@router.put('/personas/{scope}/{name}')
def update_persona(scope: str, name:str, persona: str = Form(...), faceref: UploadFile = File(None), avatar: UploadFile = File(None)):
     
    try:
        print("In update_persona")
        print("scope is ", scope)
        print("name is ", name)
        persona = json.loads(persona)
        print("persona is ", persona)
        
        if scope not in ['local', 'shared']:
            raise HTTPException(status_code=400, detail='Invalid scope')
        persona_path = BASE_DIR / scope / name / 'persona.json'
        if not persona_path.exists():
            raise HTTPException(status_code=404, detail='Persona not found')
        if 'moderated' not in persona:
            persona['moderated'] = False
        
        # Create target directory
        # Based on BASE_DIR plus static/personas/name
        # This is where the faceref and avatar
        # will be stored
        # This is the directory that the webserver will serve
        target_dir = Path(f'{BASE_DIR}/static/personas/{name}')
        #target_dir = Path(f'/files/ah/static/personas/{name}')
        target_dir.mkdir(parents=True, exist_ok=True)
        
        if faceref:
            print("Trying to save faceref")
            faceref_path = persona_path.parent / 'faceref.png'
            print("faceref path is ", faceref_path)
            with open(faceref_path, 'wb') as f:
                print("opened file for writing")
                f.write(faceref.file.read())
            # Copy faceref to new location
            new_faceref_path = target_dir / 'faceref.png'
            shutil.copy2(faceref_path, new_faceref_path)
            persona['faceref'] = str(new_faceref_path)
        
        if avatar:
            print("Trying to save avatar")
            avatar_path = persona_path.parent / 'avatar.png'
            with open(avatar_path, 'wb') as f:
                print("opened file for writing")
                f.write(avatar.file.read())
            # Copy avatar to new location
            new_avatar_path = target_dir / 'avatar.png'
            shutil.copy2(avatar_path, new_avatar_path)
            persona['avatar'] = str(new_avatar_path)
 
        with open(persona_path, 'w') as f:
            json.dump(persona, f, indent=2)
        return {'status': 'success'}
    except Exception as e:
        print("Error in update_persona")
        raise HTTPException(status_code=500, detail='Internal server error '+ str(e))

