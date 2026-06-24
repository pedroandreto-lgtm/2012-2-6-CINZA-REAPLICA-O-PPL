"""
Propósito: Dividir as questões por padrão em imagens de páginas inteiras.
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS: Verifica o padrão no pixel x=390 (lateral direita da área das questões)
Padrão: 7px rgb(64,193,243), 4px rgb(179,230,250), 2px rgb(64,193,243)
"""

from PIL import Image
import os

def encontrar_padrao_faixa(imagem, tolerancia=15):
    """
    Encontra posições onde há uma faixa horizontal com o padrão específico:
    7px rgb(64,193,243), 4px rgb(179,230,250), 2px rgb(64,193,243)
    Com margem de erro de 2px em cada faixa
    Verifica no pixel x=390
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Padrão esperado (mesmo das colunas concatenadas)
    cor_azul_escura = (64, 193, 243)
    cor_azul_clara = (179, 230, 250)
    
    # Posição fixa para verificar (x=390)
    x_verificacao = 390
    
    print(f"Analisando padrão no pixel x={x_verificacao}")
    print(f"Dimensões da imagem: {largura}x{altura}")
    
    if x_verificacao >= largura:
        print(f"⚠️  ATENÇÃO: x={x_verificacao} é maior que a largura da imagem ({largura})")
        print(f"Usando x={largura-10} como fallback")
        x_verificacao = largura - 10
    
    y = 0
    encontrados = 0
    
    while y < altura - 20:
        # Pega o pixel na posição x_verificacao
        pixel = pixels[x_verificacao, y]
        
        # Converte para RGB se necessário
        if len(pixel) == 4:  # RGBA
            r, g, b, a = pixel
        else:  # RGB
            r, g, b = pixel[:3]
        
        # Verifica se o pixel atual é da cor azul escura (início do padrão)
        if (abs(r - cor_azul_escura[0]) <= tolerancia and 
            abs(g - cor_azul_escura[1]) <= tolerancia and 
            abs(b - cor_azul_escura[2]) <= tolerancia):
            
            # Verifica se o padrão completo está presente
            padrao_valido = True
            posicao_atual = y
            
            # 1ª faixa azul escura: 7px ± 2px (5-9px)
            qtd_escura1 = 0
            while posicao_atual < altura and qtd_escura1 < 10:
                pixel_check = pixels[x_verificacao, posicao_atual]
                if len(pixel_check) == 4:
                    r, g, b, a = pixel_check
                else:
                    r, g, b = pixel_check[:3]
                
                if (abs(r - cor_azul_escura[0]) <= tolerancia and 
                    abs(g - cor_azul_escura[1]) <= tolerancia and 
                    abs(b - cor_azul_escura[2]) <= tolerancia):
                    qtd_escura1 += 1
                    posicao_atual += 1
                else:
                    break
            
            # Verifica se a quantidade está dentro da margem de erro (5-9px)
            if qtd_escura1 < 5 or qtd_escura1 > 9:
                padrao_valido = False
            
            # Faixa azul clara: 4px ± 2px (2-6px)
            if padrao_valido:
                qtd_clara = 0
                while posicao_atual < altura and qtd_clara < 7:
                    pixel_check = pixels[x_verificacao, posicao_atual]
                    if len(pixel_check) == 4:
                        r, g, b, a = pixel_check
                    else:
                        r, g, b = pixel_check[:3]
                    
                    if (abs(r - cor_azul_clara[0]) <= tolerancia and 
                        abs(g - cor_azul_clara[1]) <= tolerancia and 
                        abs(b - cor_azul_clara[2]) <= tolerancia):
                        qtd_clara += 1
                        posicao_atual += 1
                    else:
                        break
                
                # Verifica se a quantidade está dentro da margem de erro (2-6px)
                if qtd_clara < 2 or qtd_clara > 6:
                    padrao_valido = False
            
            # 2ª faixa azul escura: 2px ± 2px (0-4px)
            if padrao_valido:
                qtd_escura2 = 0
                while posicao_atual < altura and qtd_escura2 < 5:
                    pixel_check = pixels[x_verificacao, posicao_atual]
                    if len(pixel_check) == 4:
                        r, g, b, a = pixel_check
                    else:
                        r, g, b = pixel_check[:3]
                    
                    if (abs(r - cor_azul_escura[0]) <= tolerancia and 
                        abs(g - cor_azul_escura[1]) <= tolerancia and 
                        abs(b - cor_azul_escura[2]) <= tolerancia):
                        qtd_escura2 += 1
                        posicao_atual += 1
                    else:
                        break
                
                # Verifica se a quantidade está dentro da margem de erro (0-4px)
                if qtd_escura2 < 0 or qtd_escura2 > 4:
                    padrao_valido = False
            
            # Se o padrão foi validado, registra a posição de corte
            if padrao_valido:
                posicao_corte = max(0, y - 5)
                
                # Verifica se já não temos essa posição (evita duplicatas)
                if not posicoes_corte or abs(posicao_corte - posicoes_corte[-1]) > 20:
                    posicoes_corte.append(posicao_corte)
                    encontrados += 1
                    print(f"✅ Padrão encontrado em y={y}, cortando em y={posicao_corte}")
                    print(f"   -> 1ª azul escura: {qtd_escura1}px, azul clara: {qtd_clara}px, 2ª azul escura: {qtd_escura2}px")
                
                # Pula a faixa inteira
                y = posicao_atual + 10
                continue
        
        y += 1
    
    print(f"\nTotal de faixas encontradas: {encontrados}")
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem horizontalmente cortando ANTES das faixas
    """
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"❌ ERRO: Arquivo não encontrado: {caminho_imagem}")
        return
    
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"\n{'='*60}")
    print(f"📄 IMAGEM: {os.path.basename(caminho_imagem)}")
    print(f"📐 Dimensões: {largura}x{altura} pixels")
    print(f"{'='*60}")
    
    # Encontra as posições das faixas
    posicoes_corte = encontrar_padrao_faixa(imagem)
    
    if not posicoes_corte:
        print("\n❌ NENHUMA FAIXA ENCONTRADA!")
        print("Verifique se:")
        print("  1. A imagem está no formato correto")
        print("  2. O padrão de cores RGB(64,193,243) e RGB(179,230,250) está presente")
        print("  3. A posição x=390 é onde está o padrão")
        print("  4. A imagem tem pelo menos 400 pixels de largura")
        return
    
    print(f"\n✅ Encontradas {len(posicoes_corte)} faixas para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    print(f"📁 Pasta de saída: {pasta_saida}")
    
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
        print(f"💾 Salvo: {nome_arquivo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa após o final desta faixa
        posicao_anterior = posicao_corte + 20
    
    # Corta a seção final
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"💾 Salvo: {nome_arquivo} ({secao.width}x{secao.height}px)")

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
    print("🎯 DIVISOR DE QUESTÕES - IMAGENS INTEIRAS")
    print("📌 Verificando padrão em x=390")
    print("="*60)
    
    for i, nome_imagem in enumerate(imagens, 1):
        caminho_imagem = os.path.join("inteiras", nome_imagem)
        nome_base = os.path.splitext(nome_imagem)[0]
        pasta_saida = f"questoes_{nome_base}"
        
        print(f"\n{'#'*60}")
        print(f"Processando imagem {i}/{len(imagens)}: {nome_imagem}")
        print(f"{'#'*60}")
        
        dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print(f"\n{'='*60}")
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"{'='*60}")

def testar_padrao_cores():
    """
    Função de teste para verificar as cores na posição x=390
    """
    for nome_imagem in ["pagina_enem_3.png", "pagina_enem_8.png"]:
        caminho = os.path.join("inteiras", nome_imagem)
        
        if not os.path.exists(caminho):
            print(f"❌ Imagem não encontrada: {caminho}")
            continue
        
        print(f"\n{'='*60}")
        print(f"🔍 TESTE DE CORES: {nome_imagem}")
        print(f"{'='*60}")
        
        imagem = Image.open(caminho)
        pixels = imagem.load()
        largura, altura = imagem.size
        
        x_teste = 390
        if x_teste >= largura:
            print(f"⚠️  x={x_teste} é maior que a largura ({largura})")
            x_teste = largura - 10
            print(f"Usando x={x_teste}")
        
        print(f"\nAnalisando pixel em x={x_teste}:")
        print("  y  |  R    G    B  |  Cor")
        print("-----+----------------+----------------")
        
        # Mostra as cores dos primeiros 200 pixels
        for y in range(0, min(200, altura), 2):
            pixel = pixels[x_teste, y]
            if len(pixel) == 4:
                r, g, b, a = pixel
            else:
                r, g, b = pixel[:3]
            
            # Determina se é uma cor do padrão
            if (abs(r - 64) <= 15 and abs(g - 193) <= 15 and abs(b - 243) <= 15):
                cor_tipo = "🔵 AZUL ESCURO"
            elif (abs(r - 179) <= 15 and abs(g - 230) <= 15 and abs(b - 250) <= 15):
                cor_tipo = "🔷 AZUL CLARO"
            else:
                cor_tipo = "⬜ OUTRO"
            
            print(f"  {y:3d} | {r:3d}  {g:3d}  {b:3d} | {cor_tipo}")

if __name__ == "__main__":
    # Processa as imagens específicas
    processar_imagens_especificas()
    
    # Se quiser testar as cores, descomente a linha abaixo:
    # testar_padrao_cores()
    
    print("\n" + "="*60)
    print("🏁 PROGRAMA FINALIZADO!")
    print("="*60)