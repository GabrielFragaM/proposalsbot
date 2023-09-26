from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from firebase import add_proposal_to_firestore, get_bot_config
from functions import answer_items, clean_string, click_in_proposal, go_to_page_jobs, read_json_file, save_json_file, scroll_to_element, select_filter_option, select_skills, collect_proposal_info, await_time
from chatgpd import generate_proposal_response

config = get_bot_config()
timeAwaitRenderPage = config['timeAwaitRenderPage']
timeAwaitRenderElement = config['timeAwaitRenderElement']
timeAwaitActionsIntoElement = config['timeAwaitActionsIntoElement']

print(f'Tempo de espera para renderização das paginas: {str(timeAwaitRenderPage)} segundos.')
print(f'Tempo de espera para renderização dos elementos: {str(timeAwaitRenderElement)} segundos.')
print(f'Tempo de espera apos interações com os elementos: {str(timeAwaitActionsIntoElement)} segundos.')

start_time = datetime.datetime.now()
print(f'Bot iniciado em: {str(start_time)}')

# Definindo o caminho do ChromeDriver
CHROMEDRIVER_PATH = "C:\\Users\\gabri\\OneDrive\\Documentos\\Projetos\\Python\\bot-freela\\chromedriver\\chromedriver.exe"
CHROME_PATH = "C:\\Users\\gabri\\OneDrive\\Documentos\\Projetos\\Python\\bot-freela\\chrome\\chrome.exe"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-running-insecure-content")
options.binary_location = CHROME_PATH

service = Service(CHROMEDRIVER_PATH)
browser = webdriver.Chrome(service=service, options=options)

browser.get("https://www.workana.com/jobs")
await_time(timeAwaitRenderPage)

try:
    accept_cookies_button = browser.find_element(By.ID, 'onetrust-accept-btn-handler')
    accept_cookies_button.click()
except Exception as e:
    print(f"Erro ao tentar clicar no botão: {e}")

await_time(timeAwaitActionsIntoElement)
login_button = browser.find_element(By.LINK_TEXT, 'Entrar')
login_button.click()
await_time(timeAwaitActionsIntoElement)

email_input = browser.find_element(By.NAME, 'email')
email_input.send_keys("xxxx@email.com")

password_input = browser.find_element(By.NAME, 'password')
password_input.send_keys("xxxx")

login_button = browser.find_element(By.NAME, 'submit')
login_button.click()
await_time(timeAwaitRenderPage)

select_filter_option(browser, timeAwaitActionsIntoElement)

data = read_json_file()
clicked_projects = data["clicked_projects"]
project_index = 0
success_count = 0
failed_count = 0

while True:

    projects = browser.find_elements(By.CSS_SELECTOR, '.project-item.js-project')
    
    if project_index >= len(projects):
        break  # Sai do loop se todos os projetos foram processados

    try:
        project = projects[project_index]
        title_element = project.find_element(By.CSS_SELECTOR, '.h3.project-title span')
        title = title_element.get_attribute('title')
        originalTitle = title
        title = clean_string(title)

        if title not in clicked_projects:
            try:
                show_mode_btn = project.find_element(By.CSS_SELECTOR, '.more-link')
                browser.execute_script("arguments[0].click();", show_mode_btn)
            except Exception as e:
                continue

            description_element = project.find_element(By.CSS_SELECTOR, '.more-link')
            description = description_element.text
            
            description = 'Descrição não encontrada.'
            try:
                description_element = project.find_element(By.CSS_SELECTOR, '.expander.js-expander-passed')
                description = description_element.text
            except Exception as e:
                description_element = project.find_element(By.CSS_SELECTOR, '.more-link')
                description = description_element.text



            amount_element = project.find_element(By.CSS_SELECTOR, '.budget .values')
            amount = amount_element.text

            wait = WebDriverWait(browser, 10)
            originalDescription = description
            description = clean_string(description)

            make_proposal_btn = project.find_element(By.CSS_SELECTOR, '.btn.btn-inverse')

            click_in_proposal(browser, make_proposal_btn, title, clicked_projects, timeAwaitActionsIntoElement, timeAwaitRenderPage)
            save_json_file({"clicked_projects": clicked_projects})

            proposal_info = collect_proposal_info(browser, title, description, amount, timeAwaitActionsIntoElement)

            response = generate_proposal_response(proposal_info, config['context'])
            if response is None:
                print("Não foi possível obter uma resposta do ChatGPT.")
                failed_count += 1
                pass

            answer_items(browser, response, timeAwaitActionsIntoElement)
            await_time(timeAwaitActionsIntoElement)

            try:
                submit_button = browser.find_element(By.CSS_SELECTOR, '.wk-submit-block input[type="submit"]')
                scroll_to_element(browser, submit_button)
                await_time(timeAwaitActionsIntoElement)
                browser.execute_script("arguments[0].click();", submit_button)
                success_count += 1
                print(f"Proposta para '{title}' enviada com sucesso!")
                add_proposal_to_firestore(originalTitle, originalDescription, True, response, '')
                await_time(timeAwaitActionsIntoElement)
                go_to_page_jobs(browser, timeAwaitRenderPage)
            except Exception as e:
                print(f"Erro ao tentar enviar a proposta para '{title}': {e}")
                add_proposal_to_firestore(originalTitle, originalDescription, False, response, str(e))
                failed_count += 1
                pass

            try:
                wait = WebDriverWait(browser, 10)
                select_filter_option(browser, timeAwaitActionsIntoElement)
            except Exception as e:
                print(f'Erro ao tentar filtrar projetos: {e}')
    except Exception as e:
        print(f'Proposta falhou: {e}')
        failed_count += 1
        add_proposal_to_firestore(originalTitle, originalDescription, False, {}, str(e))
        pass  

    project_index += 1  # Incrementa o índice para o próximo projeto

end_time = datetime.datetime.now()
time_difference = end_time - start_time
minutes_elapsed = time_difference.total_seconds() / 60.0

# Calcule as propostas por minuto
proposals_per_minute = success_count / minutes_elapsed

print(f"O bot fez {success_count} propostas por minuto.")