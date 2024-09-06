from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time

def reclameAqui(chrome_options=None):
    # Configurações do navegador
    options = chrome_options or Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    
    # Abre a página
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.reclameaqui.com.br/empresa/banese-banco-do-estado-de-sergipe-s-a/lista-reclamacoes/?pagina=1&categoria=0000000000000001")

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
                    
                    comentarios.append(comentario_texto)
                except TimeoutException:
                    print(f"Timeout ao tentar coletar o comentário da página {pagina}, item {i}.")
                    comentarios.append("Erro ao coletar comentário.")
                
                # Voltar para a página anterior com os comentários
                driver.back()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[@id='__next']/div[1]/div[1]/div[2]/main/section[2]/div[2]/div[2]/div[{i}]/a"))
                )
            
            except TimeoutException:
                print(f"Timeout ao tentar coletar o link da página {pagina}, item {i}.")
                continue

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

    # Salvar dados em um DataFrame e exportar para CSV
    df = pd.DataFrame(comentarios, columns=["Comentario"])
    df.to_csv("comentarios.csv", index=False, encoding='utf-8')
    
    # Fecha o navegador
    driver.quit()

reclameAqui()
