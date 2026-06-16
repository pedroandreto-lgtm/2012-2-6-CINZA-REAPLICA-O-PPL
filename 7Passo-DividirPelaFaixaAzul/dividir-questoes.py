"""
Propósito: Dividir as questões por padrão de pixels específico.
Padrão: 7 pixels (13.7, 12.2, 12.5) + 4 pixels (100, 100, 100) + 2 pixels (13.7, 12.2, 12.5)

Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026
"""

from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """Converte valores do GIMP (0-100) para RGB (0-255)"""
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def verificar_padrao_pixels(imagem, x, y, padrao, tolerancia=15):
    """Verifica se a partir da posição (x,y) existe o padrão especificado"""
    pixels = imagem.load()
    largura, altura = imagem.size
    
    total_pixels = sum(quant for quant, _ in padrao)
    if y + total_pixels > altura:
        return False
    
    posicao_atual = y
    
    for quantidade, cor_alvo in padrao:
        for i in range(quantidade):
            if x >= largura or posicao_atual >= altura:
                return False
            
            pixel = pixels[x, posicao_atual]
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                return False
            
            posicao_atual += 1
    
    return True

def encontrar_posicoes_padrao(imagem, padrao, tolerancia=15):
    """Encontra posições onde o padrão aparece na imagem"""
    largura, altura = imagem.size
    
    # Analisa múltiplas colunas para ser mais robusto
    colunas_para_analisar = [
        largura // 4,
        largura // 2,
        3 * largura // 4,
        largura - 5,
        5
    ]
    
    posicoes_corte = []
    melhor_coluna = largura // 2
    
    # Testa qual coluna detecta melhor o padrão
    melhor_deteccao = 0
    for coluna in colunas_para_analisar:
        if coluna >= largura:
            continue
        
        deteccoes = []
        y = 0
        while y < altura:
            if verificar_padrao_pixels(imagem, coluna, y, padrao, tolerancia):
                deteccoes.append(y)
                total_pixels = sum(quant for quant, _ in padrao)
                y += total_pixels
            else:
                y += 1
        
        if len(deteccoes) > melhor_deteccao:
            melhor_deteccao = len(deteccoes)
            melhor_coluna = coluna
            print(f"Coluna x={coluna} encontrou {len(deteccoes)} ocorrências")
    
    # Usa a melhor coluna para encontrar as posições exatas
    print(f"\nUsando coluna x={melhor_coluna} para detectar padrões")
    y = 0
    while y < altura:
        if verificar_padrao_pixels(imagem, melhor_coluna, y, padrao, tolerancia):
            posicao_corte = y - 1
            if posicao_corte < 0:
                posicao_corte = 0
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado em y={y}, cortando em y={posicao_corte}")
            
            total_pixels = sum(quant for quant, _ in padrao)
            y += total_pixels
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_padrao(caminho_imagem, pasta_saida, padrao, tolerancia=15):
    """Divide a imagem baseado no padrão de pixels"""
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print("=" * 60)
    print(f"Imagem carregada: {largura}x{altura} pixels")
    print(f"Procurando padrão de {sum(quant for quant, _ in padrao)} pixels...")
    print("=" * 60)
    
    # Encontra as posições do padrão
    posicoes_corte = encontrar_posicoes_padrao(imagem, padrao, tolerancia)
    
    if not posicoes_corte:
        print("\n❌ Nenhum padrão encontrado na imagem!")
        print("   Verifique se:")
        print("   - As cores estão corretas")
        print("   - A tolerância não está muito baixa")
        print("   - A imagem realmente contém o padrão")
        return
    
    print(f"\n✅ Encontradas {len(posicoes_corte)} ocorrências do padrão")
    
    # Cria a pasta de saída
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção ANTES do padrão
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"questao_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"📄 Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa após o padrão
        total_pixels_padrao = sum(quant for quant, _ in padrao)
        posicao_anterior = posicao_corte + total_pixels_padrao
    
    # Corta a seção final (após a última ocorrência do padrão)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"📄 Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
    
    print("\n✅ Divisão concluída!")

if __name__ == "__main__":
    # Configuração do padrão de pixels
    # Valores do GIMP (0-100)
    cor1_gimp = (13.7, 12.2, 12.5)  # 7 pixels
    cor2_gimp = (100, 100, 100)      # 4 pixels
    cor3_gimp = (13.7, 12.2, 12.5)   # 2 pixels
    
    # Converte para RGB
    cor1_rgb = converter_cor_gimp_para_rgb(*cor1_gimp)
    cor2_rgb = converter_cor_gimp_para_rgb(*cor2_gimp)
    cor3_rgb = converter_cor_gimp_para_rgb(*cor3_gimp)
    
    # Define o padrão: [(quantidade, cor_rgb), ...]
    padrao = [
        (7, cor1_rgb),  # 7 pixels da cor1
        (4, cor2_rgb),  # 4 pixels da cor2
        (2, cor3_rgb),  # 2 pixels da cor3
    ]
    
    print("=" * 60)
    print("PADRÃO CONFIGURADO:")
    print(f"  7 pixels: RGB{cor1_rgb} (GIMP: {cor1_gimp})")
    print(f"  4 pixels: RGB{cor2_rgb} (GIMP: {cor2_gimp})")
    print(f"  2 pixels: RGB{cor3_rgb} (GIMP: {cor3_gimp})")
    print("=" * 60)
    
    # Escolha qual imagem processar
    
    # OPÇÃO 1: Colunas concatenadas
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"
    
    # OPÇÃO 2: Página inteira (descomente para usar)
    # caminho_imagem = "./inteiras/pagina_enem_15.png"
    # pasta_saida = "pagina_15"
    
    # OPÇÃO 3: Use a imagem atual (a que você está vendo)
    # caminho_imagem = "image.png"
    # pasta_saida = "questoes_extraidas"
    
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"\n❌ Arquivo não encontrado: {caminho_imagem}")
        print("   Verifique o caminho da imagem!")
        exit()
    
    # Executa a divisão
    dividir_imagem_por_padrao(caminho_imagem, pasta_saida, padrao, tolerancia=15)