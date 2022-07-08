def create_output_path(*args):
    image_id, output_path = args
    with open(output_path, 'w') as f:
        f.write("")
