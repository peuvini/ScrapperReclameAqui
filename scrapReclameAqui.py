import json
import signal
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc  # Corrigido
from selenium.webdriver.chrome.options import Options

# Variável global para armazenar os comentários
comentarios_coletados = []

def salvar_comentarios(comentarios, arquivo='comentarios.json'):
    # Abre o arquivo em modo de escrita ('w') e salva a lista completa de comentários como um array JSON
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(comentarios, f, ensure_ascii=False, indent=4)  # Salva todos os comentários como uma lista de objetos JSON

def reclameAqui(chrome_options=None):
    global comentarios_coletados

    # Configurações do navegador
    options = chrome_options or Options()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    
    # Inicializa a página e o número da página
    base_url = "https://www.reclameaqui.com.br/empresa/banese-banco-do-estado-de-sergipe-s-a/lista-reclamacoes/?pagina="
    pagina = 1

    try:
        while True:
            print(f"Coletando comentários da página {pagina}...")

            comentarios = []

            driver.get(base_url + str(pagina))

            try:
                # Captura todas as divs que contêm os links dos comentários
                divs = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'sc-1sm4sxr-0')]/div[@class='sc-1pe7b5t-0 eJgBOc']/a"))
                )

                # Extrai os links de cada div e armazena em uma lista
                links = [div.get_attribute('href') for div in divs]

                # Agora que temos os links, vamos abrir cada um
                for i, link in enumerate(links[:10]):  # Pega no máximo os 10 primeiros links
                    driver.get(link)

                    try:
                        # Coletar o texto do comentário
                        comentario_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//p[@data-testid='complaint-description']"))
                        )

                        # Coletar o HTML completo e converter para texto
                        comentario_html = comentario_element.get_attribute('innerHTML')
                        comentario_texto = comentario_html.replace('<br>', '\n').replace('<br/>', '\n')  # Substitui <br> por quebras de linha

                        comentarios.append({"comentario": comentario_texto})
                    except TimeoutException:
                        print(f"Timeout ao tentar coletar o comentário da página {pagina}, item {i + 1}.")
                        comentarios.append({"comentario": "Erro ao coletar comentário."})

                    # Voltar para a página anterior com os comentários
                    driver.back()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'sc-1sm4sxr-0')]/div[@class='sc-1pe7b5t-0 eJgBOc']/a"))
                    )

            except TimeoutException:
                print(f"Timeout ao tentar coletar os links da página {pagina}.")
                break

            # Adiciona os comentários da página atual à lista global
            comentarios_coletados.extend(comentarios)

            # Salva os dados após coletar todos os comentários da página atual
            salvar_comentarios(comentarios_coletados)

            # Tenta ir para a próxima página
            pagina += 1
            next_page_url = base_url + str(pagina)
            driver.get(next_page_url)

            try:
                # Aguarda a nova página carregar
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'sc-1sm4sxr-0')]/div[@class='sc-1pe7b5t-0 eJgBOc']/a"))
                )
                # Adiciona um refresh e espera após a mudança de página
                time.sleep(2)  # Aguarda 2 segundos para garantir que a página tenha tempo de carregar
                
            except TimeoutException:
                print("Não foi possível encontrar os links da nova página ou chegou ao final das páginas.")
                break

    except KeyboardInterrupt:
        print("\nInterrupção detectada! Salvando os comentários coletados...")

    finally:
        # Sempre salva os comentários coletados até o momento, mesmo com Ctrl+C
        salvar_comentarios(comentarios_coletados)
        # Fecha o navegador
        driver.quit()

reclameAqui()
