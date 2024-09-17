import json

def corrigir_comentarios(filename="comentariosReclameAqui.json"):
    """Corrige a codificação dos comentários e salva o JSON reformatado."""

    try:
        # Primeiro, tentar abrir o arquivo com a codificação incorreta
        with open(filename, "r", encoding='latin1') as f:
            dados = json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"Erro ao abrir o arquivo: {e}")
        return

    print("Codificação inicial usada: latin1")

    # Corrigir o texto dos comentários
    for item in dados:
        if 'comentario' in item:
            try:
                # Tenta converter o texto para utf-8
                item['comentario'] = item['comentario'].encode('latin1').decode('utf-8')
            except UnicodeDecodeError as e:
                print(f"Erro ao converter comentário: {e}")
                item['comentario'] = item['comentario']  # Deixa o texto como está em caso de erro

    # Salvar os dados corrigidos em um novo arquivo JSON
    with open("comentariosCorrigidos.json", "w", encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    print("Comentários corrigidos e salvos com sucesso!")

# Executa a função para corrigir o JSON
corrigir_comentarios()
