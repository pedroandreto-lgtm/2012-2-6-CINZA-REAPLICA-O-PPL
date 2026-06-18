"""
Propósito: Dividir as questões por padrão. Observa-se que ao início de cada questão tem uma faixa de alguma cor, que é o padrão de início de cada questão
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026
"""

from PIL import Image
import os

def encontrar_padrao_e_remover_pixel(imagem):
    """
    Encontra o padrão no meio da imagem e remove APENAS o 1 pixel ACIMA dele
    Padrão: 7 pixels RGB(35,31,32), 4 pixels RGB(255,255,255), 2 pixels RGB(35,31,32)
    Retorna a imagem modificada
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Padrão a ser procurado: 7 pixels cor1, 4 pixels cor2, 2 pixels cor1
    cor1 = (35, 31, 32)  # RGB 0-255
    cor2 = (255, 255, 255)  # RGB 0-255
    padrao = [cor1] * 7 + [cor2] * 4 + [cor1] * 2
    tamanho_padrao = len(padrao)  # 13 pixels no total
    
    print(f"Procurando padrão de {tamanho_padrao} pixels no meio da imagem...")
    
    # Lista para armazenar as posições Y onde o padrão foi encontrado
    posicoes_padrao = []
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura - tamanho_padrao:
        # Verifica se há o padrão no meio da imagem
        padrao_encontrado = True
        pixel_meio = largura // 2  # Pixel do meio da imagem
        
        for i in range(tamanho_padrao):
            pixel = pixels[pixel_meio, y + i]
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor atual corresponde ao padrão esperado
            cor_esperada = padrao[i]
            if (r != cor_esperada[0] or g != cor_esperada[1] or b != cor_esperada[2]):
                padrao_encontrado = False
                break
        
        if padrao_encontrado:
            posicoes_padrao.append(y)
            print(f"Padrão encontrado começando em y={y}")
            # Pula o padrão inteiro para evitar detecções múltiplas
            y += tamanho_padrao
        else:
            y += 1
    
    if not posicoes_padrao:
        print("Nenhum padrão encontrado na imagem!")
        return imagem
    
    print(f"Encontrados {len(posicoes_padrao)} padrões")
    
    # Cria uma nova imagem para modificar
    imagem_modificada = imagem.copy()
    pixels_mod = imagem_modificada.load()
    
    # Para cada padrão encontrado, remove APENAS o 1 pixel ACIMA
    for pos_y in posicoes_padrao:
        # Remove o pixel acima do padrão (pos_y - 1)
        if pos_y > 0:  # Garante que não está no topo da imagem
            y_remover = pos_y - 1
            
            # Remove o pixel em toda a largura da imagem
            for x in range(largura):
                # Pega a cor do pixel abaixo para substituir (ou cor branca)
                if y_remover + 1 < altura:
                    # Pega a cor do pixel abaixo (que é o início do padrão)
                    pixel_abaixo = pixels[x, y_remover + 1]
                    pixels_mod[x, y_remover] = pixel_abaixo
                else:
                    # Se não houver pixel abaixo, usa branco
                    pixels_mod[x, y_remover] = (255, 255, 255)
            
            print(f"Removido pixel na linha y={y_remover} (acima do padrão que começa em y={pos_y})")
    
    return imagem_modificada

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES das faixas
    """
    # CRIA A PASTA DE SAÍDA PRIMEIRO
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Remove os pixels acima dos padrões
    imagem_modificada = encontrar_padrao_e_remover_pixel(imagem)
    
    # Salva a imagem modificada (opcional)
    nome_base = os.path.splitext(os.path.basename(caminho_imagem))[0]
    caminho_modificado = os.path.join(pasta_saida, f"{nome_base}_modificada.png")
    imagem_modificada.save(caminho_modificado)
    print(f"Imagem modificada salva em: {caminho_modificado}")
    
    # Agora vamos dividir a imagem modificada em partes
    # Vamos usar o mesmo padrão para encontrar onde cortar
    pixels = imagem_modificada.load()
    
    # Encontra todas as posições onde começa o padrão
    posicoes_corte = []
    padrao = [(35,31,32)] * 7 + [(255,255,255)] * 4 + [(35,31,32)] * 2
    tamanho_padrao = len(padrao)
    
    y = 0
    while y < altura - tamanho_padrao:
        padrao_encontrado = True
        pixel_meio = largura // 2
        
        for i in range(tamanho_padrao):
            pixel = pixels[pixel_meio, y + i]
            
            if len(pixel) == 4:
                r, g, b, a = pixel
            else:
                r, g, b = pixel[:3]
            
            cor_esperada = padrao[i]
            if (r != cor_esperada[0] or g != cor_esperada[1] or b != cor_esperada[2]):
                padrao_encontrado = False
                break
        
        if padrao_encontrado:
            # Corta 1 pixel ANTES do padrão (que agora foi removido)
            posicao_corte = y - 1
            if posicao_corte < 0:
                posicao_corte = 0
            posicoes_corte.append(posicao_corte)
            print(f"Cortando em y={posicao_corte} (antes do padrão em y={y})")
            y += tamanho_padrao
        else:
            y += 1
    
    # Adiciona a posição final
    posicoes_corte.append(altura)
    
    # Corta as seções da imagem
    for i in range(len(posicoes_corte) - 1):
        inicio = posicoes_corte[i]
        fim = posicoes_corte[i + 1]
        
        # Corta a seção
        area_corte = (0, inicio, largura, fim)
        secao = imagem_modificada.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"

    #caminho_imagem = "./inteiras/pagina_enem_15.png"
    #pasta_saida = "pagina_15"
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")