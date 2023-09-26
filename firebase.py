from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

def get_bot_config():
    cred = credentials.Certificate("C:\\Users\\gabri\\OneDrive\\Documentos\\Projetos\\Python\\bot-freela\\paware-clientes-firebase-adminsdk-21s47-5b5b36d979.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    bot_ref = db.collection('bots').document('kZaZNxr9ZMAovv4EA8I4')
    bot_data = bot_ref.get().to_dict()
    config = bot_data['config']
    return config

def add_proposal_to_firestore(title, description, success, proposal, log):
    try:
        db = firestore.client()

        formatted_date = datetime.now().strftime('%d/%m/%Y %H:%M')

        proposal_data = {
            'title': title,
            'description': description,
            'success': success,
            'replied': False,
            'proposal': proposal,
            'log': log,
            'from': 'Workana',
            'botId': 'kZaZNxr9ZMAovv4EA8I4',
            'createdAt': formatted_date
        }

        db.collection('proposals').add(proposal_data)
    except Exception as e:
        print(e)
