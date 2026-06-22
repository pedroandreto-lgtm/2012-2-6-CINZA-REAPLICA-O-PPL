"""
Propósito: Dividir as questões por padrão. Observa-se que ao início de cada questão tem uma faixa de alguma cor, que é o padrão de início de cada questão
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a imagem "colunas_concatenadas_verticalmente.png" do passo 6 para essa pasta do passo 7, e as imagens de páginas inteiras da pasta "inteiras" do passo 5 para essa pasta do passo 7
OBS2: esse código vai percorrer a imagem de cima pra baixo, sempre analisando o pixel central da imagem, para encontrar a faixa que divide as questões. Quando encontrar a faixa, ele vai cortar a imagem ANTES da faixa, e depois pular a faixa para continuar procurando a próxima questão
OBS3: primeiro você vai rodar esse código para cortar a imagem de colunas concatenadas, depois você vai rodar para cada página inteira
OBS4: atualize as linhas 127 e 128 para recortar a imagem de colunas concatenadas, depois atualize para recortar cada página inteira. Atualize o nome da pasta de saída também
OBS5: o padrão atual é: 7px rgb(35,31,32), 4px rgb(255,255,255), 2px rgb(35,31,32) com margem de erro de 2px
"""

from PIL import Image
import os

def encontrar_padrao_faixa(imagem, tolerancia=5):
    """
    Encontra posições onde há uma faixa horizontal com o padrão específico:
    7px rgb(35,31,32), 4px rgb(255,255,255), 2px rgb(35,31,32)
    Com margem de erro de 2px em cada faixa
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Padrão esperado
    cor_escura = (35, 31, 32)
    cor_branca = (255, 255, 255)
    
    # Tamanhos esperados com margem de erro de 2px
    # Faixa escura 1: 7px ± 2px = 5-9px
    # Faixa branca: 4px ± 2px = 2-6px  
    # Faixa escura 2: 2px ± 2px = 0-4px
    # Total: 7-19px
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura - 20:  # Deixar espaço mínimo para o padrão completo
        # Pega o pixel central (metade da largura)
        x_central = largura // 2
        pixel = pixels[x_central, y]
        
        # Converte para RGB se necessário
        if len(pixel) == 4:  # RGBA
            r, g, b, a = pixel
        else:  # RGB
            r, g, b = pixel[:3]
        
        # Verifica se o pixel atual é da cor escura (início do padrão)
        if (abs(r - cor_escura[0]) <= tolerancia and 
            abs(g - cor_escura[1]) <= tolerancia and 
            abs(b - cor_escura[2]) <= tolerancia):
            
            # Verifica se o padrão completo está presente
            padrao_valido = True
            posicao_atual = y
            
            # 1ª faixa escura: 7px ± 2px (5-9px)
            qtd_escura1 = 0
            while posicao_atual < altura and qtd_escura1 < 10:  # máximo 10px
                pixel_check = pixels[x_central, posicao_atual]
                if len(pixel_check) == 4:
                    r, g, b, a = pixel_check
                else:
                    r, g, b = pixel_check[:3]
                
                if (abs(r - cor_escura[0]) <= tolerancia and 
                    abs(g - cor_escura[1]) <= tolerancia and 
                    abs(b - cor_escura[2]) <= tolerancia):
                    qtd_escura1 += 1
                    posicao_atual += 1
                else:
                    break
            
            # Verifica se a quantidade está dentro da margem de erro (5-9px)
            if qtd_escura1 < 5 or qtd_escura1 > 9:
                padrao_valido = False
            
            # Faixa branca: 4px ± 2px (2-6px)
            if padrao_valido:
                qtd_branca = 0
                while posicao_atual < altura and qtd_branca < 7:  # máximo 7px
                    pixel_check = pixels[x_central, posicao_atual]
                    if len(pixel_check) == 4:
                        r, g, b, a = pixel_check
                    else:
                        r, g, b = pixel_check[:3]
                    
                    if (abs(r - cor_branca[0]) <= tolerancia and 
                        abs(g - cor_branca[1]) <= tolerancia and 
                        abs(b - cor_branca[2]) <= tolerancia):
                        qtd_branca += 1
                        posicao_atual += 1
                    else:
                        break
                
                # Verifica se a quantidade está dentro da margem de erro (2-6px)
                if qtd_branca < 2 or qtd_branca > 6:
                    padrao_valido = False
            
            # 2ª faixa escura: 2px ± 2px (0-4px)
            if padrao_valido:
                qtd_escura2 = 0
                while posicao_atual < altura and qtd_escura2 < 5:  # máximo 5px
                    pixel_check = pixels[x_central, posicao_atual]
                    if len(pixel_check) == 4:
                        r, g, b, a = pixel_check
                    else:
                        r, g, b = pixel_check[:3]
                    
                    if (abs(r - cor_escura[0]) <= tolerancia and 
                        abs(g - cor_escura[1]) <= tolerancia and 
                        abs(b - cor_escura[2]) <= tolerancia):
                        qtd_escura2 += 1
                        posicao_atual += 1
                    else:
                        break
                
                # Verifica se a quantidade está dentro da margem de erro (0-4px)
                if qtd_escura2 < 0 or qtd_escura2 > 4:
                    padrao_valido = False
            
            # Se o padrão foi validado, registra a posição de corte
            if padrao_valido:
                # Pula alguns pixels antes do padrão para garantir que vamos antes da faixa
                # A faixa começa em y, então cortamos em y-5 para garantir que não pegamos
                posicao_corte = max(0, y - 35)
                posicoes_corte.append(posicao_corte)
                print(f"Padrão encontrado começando em y={y}, cortando em y={posicao_corte}")
                print(f"  -> 1ª escura: {qtd_escura1}px, branca: {qtd_branca}px, 2ª escura: {qtd_escura2}px")
                
                # Pula a faixa inteira + alguns pixels extras para evitar detecções múltiplas
                y = posicao_atual + 10
                continue
        
        y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES das faixas
    """
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    print(f"Analisando pixel central em x={largura//2}")
    
    # Encontra as posições das faixas
    posicoes_corte = encontrar_padrao_faixa(imagem)
    
    if not posicoes_corte:
        print("Nenhuma faixa com o padrão encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção ANTES da faixa (do início anterior até o início da faixa)
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa após o final desta faixa
        posicao_anterior = posicao_corte + 20  # Pula a faixa com margem extra
    
    # Corta a seção final (após a última faixa)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    # Para colunas concatenadas
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"
    
    # Para páginas inteiras (descomente as linhas abaixo e comente as de cima)
    # caminho_imagem = "./inteiras/pagina_enem_15.png"
    # pasta_saida = "pagina_15"
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")