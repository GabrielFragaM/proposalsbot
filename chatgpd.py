import requests
import json

def generate_proposal_response(proposal_info, context):
    baseUrl = 'https://api.openai.com/v1/chat/completions'
    print('Iniciando integração com o chatgpt-3.5-turbo-16k')
    
    sorted_context = sorted(context, key=lambda x: x['index'])
    
    chatMessages = [{"role": item["role"], "content": item["content"]} for item in sorted_context]
    
    chatMessages.append({"role": "user", "content": f'Devolva o objeto js do mesmo formato com suas resposta da proposta da Paware Softwares: {proposal_info}'}) #esse objeto precisa ser o ultimo objeto
    
    headers = {
        'Content-type': 'application/json',
        'Authorization': 'Bearer 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'
    }

    body = {
        "messages": chatMessages,
        "max_tokens": 8000,
        "model": "gpt-3.5-turbo-16k"
    }

    response = requests.post(baseUrl, headers=headers, json=body)

    responseJson = response.json()
  
    messageChatResult = responseJson['choices'][-1]['message']['content']
  
   
    messageChatResult = messageChatResult.replace("'", '"')
    messageChatResult = messageChatResult.replace("'", "")

    return json.loads(messageChatResult)