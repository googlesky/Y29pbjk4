from flask import Flask, request, jsonify
import hashlib
import os

app = Flask(__name__)
file_storage = {}


def calculate_file_hash(file_path):
    """
    Calculates the SHA1 hash of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The SHA1 hash of the file.
    """
    sha1_hash = hashlib.sha1()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha1_hash.update(chunk)
    return sha1_hash.hexdigest()


def save_file(file):
    """
    Saves a file to the server and returns its SHA1 hash.

    Args:
        file (FileStorage): The file to be saved.

    Returns:
        str: The SHA1 hash of the saved file.
    """
    file_hash = calculate_file_hash(file.filename)
    if file_hash not in file_storage:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        file_storage[file_hash] = file_path
    return file_hash


def delete_file(file_hash):
    """
    Deletes a file from the server.

    Args:
        file_hash (str): The SHA1 hash of the file to be deleted.

    Returns:
        bool: True if the file was deleted successfully, False otherwise.
    """
    if file_hash in file_storage:
        file_path = file_storage[file_hash]
        os.remove(file_path)
        del file_storage[file_hash]
        return True
    return False


@app.route('/files', methods=['POST'])
def upload_file():
    """
    Endpoint for uploading a file to the server.

    Returns:
        JSON: A JSON object containing the SHA1 hash of the uploaded file.
    """
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected for uploading'}), 400

    file_hash = save_file(file)
    return jsonify({'file_hash': file_hash})


@app.route('/files/<file_hash>', methods=['GET'])
def retrieve_file(file_hash):
    """
    Endpoint for retrieving a file from the server.

    Args:
        file_hash (str): The SHA1 hash of the file to be retrieved.

    Returns:
        File: The requested file.
    """
    if file_hash not in file_storage:
        return jsonify({'message': 'File not found'}), 404

    file_path = file_storage[file_hash]
    return app.send_static_file(file_path)


@app.route('/files/<file_hash>', methods=['DELETE'])
def delete_uploaded_file(file_hash):
    """
    Endpoint for deleting a file from the server.

    Args:
        file_hash (str): The SHA1 hash of the file to be deleted.

    Returns:
        JSON: A JSON object containing a message indicating whether the file was deleted successfully or not.
    """
    if delete_file(file_hash):
        return jsonify({'message': 'File deleted successfully'})
    else:
        return jsonify({'message': 'File not found'}), 404


if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)  # Create the uploads directory if it doesn't exist
    app.run()