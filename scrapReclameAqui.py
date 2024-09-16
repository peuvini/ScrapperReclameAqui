from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json
import time
import undetected_chromedriver as uc

def carregar_comentarios(filename="comentariosReclameAqui.json"):
    """Carrega comentários existentes do arquivo JSON, se houver."""
    try:
        with open(filename, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_comentarios(comentarios, filename="comentariosReclameAqui.json"):
    """Salva a lista de comentários em um arquivo JSON, adicionando aos existentes."""
    # Carrega comentários existentes
    comentarios_existentes = carregar_comentarios(filename)
    comentarios_existentes.extend(comentarios)
    
    # Salva todos os comentários (existentes e novos) no arquivo
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(comentarios_existentes, f, ensure_ascii=False, indent=4)

def reclameAqui(chrome_options=None):
    # Configurações do navegador
    options = chrome_options or Options()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    
    # Abre a página
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.reclameaqui.com.br/empresa/banese-banco-do-estado-de-sergipe-s-a/lista-reclamacoes/?pagina=29")

    comentarios = []
    pagina = 1

    while True:
        print(f"Coletando comentários da página {pagina}...")

        for i in range(1, 11):  # Coleta até 10 comentários por página
            try:
                # Espera pelo link do comentário
                div = wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//*[@id='__next']/div[1]/div[1]/div[2]/main/section[2]/div[2]/div[2]/div[{i}]/a"))
                )
                link = div.get_attribute('href')
                # Abrir o link diretamente na mesma guia
                driver.get(link)
                
                try:
                    comentario_element = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//p[@data-testid='complaint-description']"))
                    )
                    
                    # Coletar o HTML completo e converter para texto
                    comentario_html = comentario_element.get_attribute('innerHTML')
                    comentario_texto = comentario_html.replace('<br>', '\n').replace('<br/>', '\n')  # Substitui <br> por quebras de linha
                    
                    comentarios.append({"comentario": comentario_texto})
                except TimeoutException:
                    print(f"Timeout ao tentar coletar o comentário da página {pagina}, item {i}.")
                    comentarios.append({"comentario": "Erro ao coletar comentário."})
                
                # Voltar para a página anterior com os comentários
                driver.back()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[@id='__next']/div[1]/div[1]/div[2]/main/section[2]/div[2]/div[2]/div[{i}]/a"))
                )
            
            except TimeoutException:
                print(f"Timeout ao tentar coletar o link da página {pagina}, item {i}.")
                continue

        # Salva os dados após coletar todos os comentários da página atual
        salvar_comentarios(comentarios)

        # Tenta ir para a próxima página
        try:
            passarPagina = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='__next']/div[1]/div[1]/div[2]/main/section[2]/div[2]/div[2]/div[11]/div/button[3]/div"))
            )
            passarPagina.click()
            pagina += 1
            driver.refresh()
            # Adiciona um refresh e espera após a mudança de página
            time.sleep(2)  # Aguarda 2 segundos para garantir que a página tenha tempo de carregar
            
        except TimeoutException:
            print("Não foi possível encontrar o botão de próxima página ou chegou ao final das páginas.")
            break

    # Salvar dados finais em um arquivo JSON
    salvar_comentarios(comentarios)

    # Fecha o navegador
    driver.quit()

reclameAqui()
