from ..commands import command
import os

@service(context=None)
async def get_persona_data(persona_name):
    import os
    import json
    import sys

    print("persona name is", persona_name, file=sys.stderr)

    persona_path = os.path.join('personas', 'local', persona_name)
    if not os.path.exists(persona_path):
        persona_path = os.path.join('personas', 'shared', persona_name)
        if not os.path.exists(persona_path):
            return {}
    # read the persona data
    persona_file = os.path.join(persona_path, 'persona.json')
    if not os.path.exists(persona_file):
        return {}
    with open(persona_file, 'r') as f:
        persona_data = json.load(f)

    persona_data['avatar_image_path'] = os.path.join(persona_path, 'avatar.png')
    persona_data['face_ref_image_path'] = os.path.join(persona_path, 'faceref.png')

    # if faceref image does not exist, use the avatar image
    if not os.path.exists(persona_data['face_ref_image_path']):
        persona_data['face_ref_image_path'] = persona_data['avatar_image_path']

    return persona_data


@command()
async def pic_of_me(prompt, context=None):
    """pic_of_me(prompt)

    Generate a picture of the persona given a detailed description of what they 
    they look like and what are doing. You will (usually) want to include
    the full text from the Appearance section of the Persona.
    Always use this instead of 'image' when creating an image of the persona!

    Example:

    { "pic_of_me": "[details from Appearance section of Persona definition] wearing a blue hat and a red shirt, playing guitar." }

    """
    persona = context.persona
    print("persona:", persona)
    img = await context.text_to_image(prompt + ', solo, ', 'split-view, diptych, side-by-side, 2girl, 2boy')
    print("img = ", img)
    img_dir = os.path.dirname(persona['face_ref_image_path'])
    swapped = await context.swap_face(img_dir, img)
    await context.insert_image(swapped)


