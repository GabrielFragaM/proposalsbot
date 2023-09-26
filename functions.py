from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import re
import json
import os
import time

def await_time(seconds):
    print(f'Aguardando {seconds} segundos...')
    time.sleep(seconds)

def clean_string(s):
    return re.sub(r"[^a-zA-Z0-9\s]", "", s)

def scroll_to_element(browser, element):
    """Função auxiliar para rolar até um elemento."""
    browser.execute_script("arguments[0].scrollIntoView();", element)

def collect_proposal_info(browser, title, description, amount, timeAwaitActionsIntoElement):
    proposal_data = {
        'Selecionar no mínimo 5 Habilidades => JavaScript, .Net Core, React.js, Flutter, Microsoft Azure, Dart, C#?': {'id': 'dropdown', 'resposta': ''},
        'Titulo da Proposta': title,
        'Informações da Proposta': description,
        'Valor ofecido pelo cliente': amount
    }

    # Coletando as perguntas iniciais
    questions = browser.find_elements(By.CSS_SELECTOR, 'div.form-group.form-group-simple input.form-control')
    for idx, question in enumerate(questions):
        label_for = question.get_attribute("id")
        
        # Verifique se o elemento label existe
        try:
            label_element = browser.find_element(By.CSS_SELECTOR, f'label[for="{label_for}"]')
            label_text = label_element.text
            print('Pegando a questão: ' + str(label_text))
            proposal_data[str(label_text)] = {'id': label_for, 'resposta': ''}
            scroll_to_element(browser, question)
            await_time(timeAwaitActionsIntoElement)
        except NoSuchElementException:
            print(f"Não foi possível encontrar o label para o ID {label_for}. Pulando esta questão.")
            continue
    
    # Coletando os outros campos
    fields = {
        'Amount': 'Valor total Em numero.',
        'BidContent': 'De o detalhes da proposta(descrição)? minimo 250 caracteres',
        'BidDeliveryTime': 'O tempo necessário para finalizar o trabalho? ex: 10 dias, 1 mês...'
    }

    print('Coletando os outros campos')

    for key, value in fields.items():
        try:
            print('Pegando a questão: ' + str(value))
            field_element = browser.find_element(By.ID, key)
            scroll_to_element(browser, field_element)
            await_time(timeAwaitActionsIntoElement)
            proposal_data[str(value)] = {'id': key, 'resposta': ''}
        except Exception as e:
            print(f"Erro ao tentar rolar até o campo {key}: {e}")
    
    return proposal_data

def select_skills(browser, skills_list, timeAwaitActionsIntoElement):
    """Função para selecionar habilidades no dropdown."""

    if isinstance(skills_list, str):
        skills_list = [skill.strip() for skill in skills_list.split(',')]
    
    try:
        print("Tentando localizar o campo de pesquisa do dropdown...")
        search_field = browser.find_element(By.CSS_SELECTOR, '.multi-select-search-field')
        
        await_time(timeAwaitActionsIntoElement)
        scroll_to_element(browser, search_field)
    except Exception as e:
        print(f"Erro ao tentar localizar o campo de pesquisa do dropdown: {e}")
        return
    
    for skill in skills_list:
        try:
            print(f"Tentando inserir a habilidade '{skill}' no campo de pesquisa...")
            search_field.clear()
            search_field.send_keys(skill)
        
            await_time(timeAwaitActionsIntoElement)
            
            skill_element = browser.find_element(By.XPATH, f'//li[contains(@class, "multi-select-results-item")]/span[text()="{skill}"]')
            scroll_to_element(browser, skill_element)
            await_time(timeAwaitActionsIntoElement)

            browser.execute_script("arguments[0].click();", skill_element)
            print(f"Habilidade '{skill}' selecionada com sucesso!")
        except Exception as e:
            print(f"Não foi possível encontrar a habilidade {skill}. Pulando. Erro: {e}")
            continue

def answer_items(browser, response, timeAwaitActionsIntoElement):
    for key, value in response.items():
        try:
            if(value['id'] == 'dropdown'):
                try:
                    print('Preenchendo as habilidades do Dropdown: ' + str(value['resposta']))
                    select_skills(browser, value['resposta'], timeAwaitActionsIntoElement)
                except Exception as e:
                    print(f"Erro ao tentar preencher o campo {value['id']}: {e}")
            else:
                try:
                    input_element = browser.find_element(By.ID, value['id'])
                    scroll_to_element(browser, input_element)
                    await_time(timeAwaitActionsIntoElement)
                    print('Preechendo a questão: ' + str(key) + ' = ' + str(value['resposta']))
                    if key == 'Valor total Em numero':
                        only_numbers = re.sub(r'\D', '', value['resposta'])  # Remove tudo que não for dígito
                        input_element.send_keys(only_numbers)
                    else:
                        input_element.send_keys(value['resposta'])
                except Exception as e:
                    print(f"Erro ao tentar preencher o campo {value['id']}: {e}")
        except Exception as e:
            print(f"Erro ao tentar preencher a chave {key}: {e}")


def accept_alert(browser):
    try:
        WebDriverWait(browser, 10).until(EC.alert_is_present())

        alert = browser.switch_to.alert

        alert.accept()

        print("Alerta aceito!")
    except:
        print("Nenhum alerta presente.")


def go_to_page_jobs(browser, timeAwaitRenderPage):
    browser.get("https://www.workana.com/jobs")
    accept_alert(browser)
    await_time(timeAwaitRenderPage)

def click_in_proposal(browser, make_proposal_btn, title, clicked_projects, timeAwaitActionsIntoElement, timeAwaitRenderPage):
    try:
        await_time(timeAwaitActionsIntoElement)
        browser.execute_script("arguments[0].click();", make_proposal_btn)
    except Exception as e:
        print('Erro ao clicar na proposta Aguardando 3 segundos')
        return
    
    clicked_projects.append(title)

    await_time(timeAwaitActionsIntoElement)
    
    # Clicar no botão "Fazer uma proposta"
    try:
        bid_button = browser.find_element(By.ID, 'bid_button')
        browser.execute_script("arguments[0].click();", bid_button)
    except Exception as e:
        print(f"Erro ao tentar clicar no botão 'Fazer uma proposta': {e}")
    
    print('Proposta: "' + title + '" Clicada!')
    await_time(timeAwaitRenderPage)

def select_filter_option(browser, timeAwaitActionsIntoElement):
    dropdown = browser.find_element(By.CSS_SELECTOR, '.multi-select-selection.form-control')
    browser.execute_script("arguments[0].click();", dropdown)
    await_time(timeAwaitActionsIntoElement)

    option = browser.find_element(By.XPATH, '//li[@data-dropdown-item-index="0"]/span[text()="Principal Programação"]')
    browser.execute_script("arguments[0].click();", option)
    await_time(timeAwaitActionsIntoElement)


# Caminho do arquivo JSON
file_path = " analytics.json"

def read_json_file():
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {"clicked_projects": []}

# Salvar no arquivo JSON
def save_json_file(data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)