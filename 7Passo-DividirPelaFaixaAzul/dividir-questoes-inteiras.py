"""
Propósito: Dividir as questões por padrão em imagens de páginas inteiras.
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026
"""

from PIL import Image
import os

def encontrar_padrao_faixa(imagem, tolerancia=10):
    """
    Encontra posições onde há uma faixa horizontal com o padrão específico na lateral esquerda:
    7px rgb(35,31,32), 4px rgb(255,255,255), 2px rgb(35,31,32)
    Com margem de erro de 2px em cada faixa
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Padrão esperado
    cor_escura = (35, 31, 32)
    cor_branca = (255, 255, 255)
    
    # Testar em várias posições na lateral esquerda
    posicoes_x = [5, 8, 10, 12, 15, 20, 25, 30]
    
    print(f"Analisando padrão em {len(posicoes_x)} posições diferentes na lateral esquerda")
    
    for x_verificacao in posicoes_x:
        print(f"\nVerificando em x={x_verificacao}")
        y = 0
        encontrados_nessa_posicao = 0
        
        while y < altura - 20:
            # Pega o pixel na lateral esquerda
            pixel = pixels[x_verificacao, y]
            
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
                while posicao_atual < altura and qtd_escura1 < 10:
                    pixel_check = pixels[x_verificacao, posicao_atual]
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
                    while posicao_atual < altura and qtd_branca < 7:
                        pixel_check = pixels[x_verificacao, posicao_atual]
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
                    while posicao_atual < altura and qtd_escura2 < 5:
                        pixel_check = pixels[x_verificacao, posicao_atual]
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
                    # Corta ANTES do padrão
                    posicao_corte = max(0, y - 5)
                    
                    # Verifica se já não temos essa posição
                    if posicao_corte not in posicoes_corte:
                        posicoes_corte.append(posicao_corte)
                        encontrados_nessa_posicao += 1
                        print(f"  Padrão encontrado em x={x_verificacao}, y={y}, cortando em y={posicao_corte}")
                        print(f"    -> 1ª escura: {qtd_escura1}px, branca: {qtd_branca}px, 2ª escura: {qtd_escura2}px")
                    
                    # Pula a faixa inteira
                    y = posicao_atual + 10
                    continue
            
            y += 1
        
        if encontrados_nessa_posicao > 0:
            print(f"  Total encontrado em x={x_verificacao}: {encontrados_nessa_posicao} faixas")
    
    # Ordena as posições
    posicoes_corte.sort()
    
    # Remove duplicatas próximas (menos de 20 pixels de diferença)
    if posicoes_corte:
        posicoes_filtradas = [posicoes_corte[0]]
        for pos in posicoes_corte[1:]:
            if pos - posicoes_filtradas[-1] > 20:
                posicoes_filtradas.append(pos)
        posicoes_corte = posicoes_filtradas
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem horizontalmente cortando ANTES das faixas
    """
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"ERRO: Arquivo não encontrado: {caminho_imagem}")
        return
    
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"\n{'='*60}")
    print(f"IMAGEM: {os.path.basename(caminho_imagem)}")
    print(f"Dimensões: {largura}x{altura} pixels")
    print(f"{'='*60}")
    
    # Encontra as posições das faixas
    posicoes_corte = encontrar_padrao_faixa(imagem)
    
    if not posicoes_corte:
        print("\n❌ NENHUMA FAIXA ENCONTRADA!")
        print("Verifique se:")
        print("  1. As imagens estão no formato correto")
        print("  2. O padrão de cores é o esperado")
        print("  3. A posição de verificação (x) está correta")
        print("  4. O padrão está visível na imagem")
        return
    
    print(f"\n✅ Encontradas {len(posicoes_corte)} faixas para corte:")
    for i, pos in enumerate(posicoes_corte):
        print(f"  Faixa {i+1}: y={pos}")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção ANTES da faixa
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"questao_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"✅ Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa após o final desta faixa
        posicao_anterior = posicao_corte + 20
    
    # Corta a seção final
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"✅ Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

def processar_imagens_especificas():
    """
    Processa especificamente as imagens pagina_enem_3.png e pagina_enem_8.png
    """
    # Lista das imagens a serem processadas
    imagens = [
        "pagina_enem_3.png",
        "pagina_enem_8.png"
    ]
    
    print("="*60)
    print("DIVISOR DE QUESTÕES - IMAGENS INTEIRAS")
    print("="*60)
    
    for i, nome_imagem in enumerate(imagens, 1):
        caminho_imagem = os.path.join("inteiras", nome_imagem)
        nome_base = os.path.splitext(nome_imagem)[0]
        pasta_saida = f"questoes_{nome_base}"
        
        print(f"\n{'='*60}")
        print(f"Processando imagem {i}/{len(imagens)}: {nome_imagem}")
        print(f"{'='*60}")
        
        dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print(f"\n{'='*60}")
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"{'='*60}")

def testar_padrao_cores():
    """
    Função de teste para verificar as cores na imagem
    """
    import sys
    
    for nome_imagem in ["pagina_enem_3.png", "pagina_enem_8.png"]:
        caminho = os.path.join("inteiras", nome_imagem)
        
        if not os.path.exists(caminho):
            print(f"❌ Imagem não encontrada: {caminho}")
            continue
        
        print(f"\n{'='*60}")
        print(f"TESTE DE CORES: {nome_imagem}")
        print(f"{'='*60}")
        
        imagem = Image.open(caminho)
        pixels = imagem.load()
        largura, altura = imagem.size
        
        # Testa várias posições x
        posicoes_x = [5, 8, 10, 12, 15, 20, 25, 30]
        
        for x in posicoes_x:
            print(f"\nPosição x={x}:")
            # Mostra as cores dos primeiros 50 pixels
            for y in range(0, min(50, altura), 5):
                pixel = pixels[x, y]
                if len(pixel) == 4:
                    r, g, b, a = pixel
                else:
                    r, g, b = pixel[:3]
                print(f"  y={y}: RGB({r:3d},{g:3d},{b:3d})")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DIVISOR DE QUESTÕES - IMAGENS INTEIRAS")
    print("="*60)
    
    # OPÇÃO 1: Processar as imagens específicas
    processar_imagens_especificas()
    
    # OPÇÃO 2: Testar as cores (descomente se precisar debugar)
    # testar_padrao_cores()
    
    print("\n" + "="*60)
    print("FINALIZADO!")
    print("="*60)