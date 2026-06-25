"""
Propósito: Dividir as imagens de páginas inteiras em questões individuais
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS: 
- As imagens estão na pasta "inteiras"
- O padrão de divisão é o mesmo das colunas concatenadas
- Verifica no pixel x=390
- Corta 30px acima do padrão encontrado
- Salva na pasta "inteiras-questoes"
"""

from PIL import Image
import os
import shutil

def encontrar_padrao_faixa(imagem, tolerancia=15):
    """
    Encontra posições onde há uma faixa horizontal com o padrão:
    7px rgb(64,193,243), 4px rgb(179,230,250), 2px rgb(64,193,243)
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
    
    # Se a imagem for menor que 390, ajusta
    if x_verificacao >= largura:
        x_verificacao = largura - 10
        print(f"⚠️  Ajustando x para {x_verificacao} (largura da imagem: {largura})")
    
    print(f"Analisando padrão no pixel x={x_verificacao}")
    print(f"Dimensões da imagem: {largura}x{altura}")
    
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
                # Corta 30px ACIMA do início do padrão
                posicao_corte = max(0, y - 30)
                
                # Verifica se já não temos essa posição (evita duplicatas)
                if not posicoes_corte or abs(posicao_corte - posicoes_corte[-1]) > 20:
                    posicoes_corte.append(posicao_corte)
                    encontrados += 1
                    print(f"✅ Padrão encontrado em y={y}, cortando em y={posicao_corte} (30px acima)")
                    print(f"   -> 1ª azul escura: {qtd_escura1}px, azul clara: {qtd_clara}px, 2ª azul escura: {qtd_escura2}px")
                
                # Pula a faixa inteira
                y = posicao_atual + 10
                continue
        
        y += 1
    
    print(f"\nTotal de faixas encontradas: {encontrados}")
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando 30px ACIMA das faixas
    """
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"❌ ERRO: Arquivo não encontrado: {caminho_imagem}")
        return False
    
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    nome_arquivo = os.path.basename(caminho_imagem)
    
    print(f"\n{'='*60}")
    print(f"📄 IMAGEM: {nome_arquivo}")
    print(f"📐 Dimensões: {largura}x{altura} pixels")
    print(f"{'='*60}")
    
    # Encontra as posições das faixas
    posicoes_corte = encontrar_padrao_faixa(imagem)
    
    if not posicoes_corte:
        print("\n❌ NENHUMA FAIXA ENCONTRADA!")
        print("Verifique se:")
        print("  1. A imagem tem o padrão de cores RGB(64,193,243) e RGB(179,230,250)")
        print("  2. A posição x=390 é onde está o padrão")
        print("  3. A imagem tem pelo menos 400 pixels de largura")
        return False
    
    print(f"\n✅ Encontradas {len(posicoes_corte)} faixas para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    print(f"📁 Pasta de saída: {pasta_saida}")
    
    # Corta as seções da imagem
    posicao_anterior = 0
    questoes_cortadas = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção ANTES da faixa
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_questao = f"questao_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_questao)
        secao.save(caminho_completo)
        questoes_cortadas += 1
        print(f"💾 Salvo: {nome_questao} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa após o final desta faixa
        posicao_anterior = posicao_corte + 30  # Pula a faixa + 30px de margem
    
    # Corta a seção final (após a última faixa)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_questao = f"questao_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_questao)
        secao.save(caminho_completo)
        questoes_cortadas += 1
        print(f"💾 Salvo: {nome_questao} ({secao.width}x{secao.height}px)")
    
    print(f"\n✅ Total de questões extraídas: {questoes_cortadas}")
    return True

def processar_todas_imagens():
    """
    Processa todas as imagens PNG da pasta 'inteiras'
    """
    pasta_origem = "inteiras"
    pasta_destino = "inteiras-questoes"
    
    # Verifica se a pasta de origem existe
    if not os.path.exists(pasta_origem):
        print(f"❌ ERRO: Pasta '{pasta_origem}' não encontrada!")
        return
    
    # Cria a pasta de destino
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lista todas as imagens PNG na pasta
    imagens = [f for f in os.listdir(pasta_origem) if f.lower().endswith('.png')]
    
    if not imagens:
        print(f"❌ Nenhuma imagem PNG encontrada na pasta '{pasta_origem}'")
        return
    
    print("="*60)
    print("🎯 DIVISOR DE QUESTÕES - IMAGENS INTEIRAS")
    print(f"📁 Pasta origem: {pasta_origem}")
    print(f"📁 Pasta destino: {pasta_destino}")
    print(f"📌 Verificando padrão em x=390")
    print(f"✂️  Cortando 30px acima do padrão")
    print("="*60)
    
    imagens_processadas = 0
    questoes_totais = 0
    
    for i, nome_imagem in enumerate(imagens, 1):
        caminho_origem = os.path.join(pasta_origem, nome_imagem)
        nome_base = os.path.splitext(nome_imagem)[0]
        pasta_saida = os.path.join(pasta_destino, nome_base)
        
        print(f"\n{'#'*60}")
        print(f"Processando imagem {i}/{len(imagens)}: {nome_imagem}")
        print(f"{'#'*60}")
        
        if dividir_imagem_por_faixas(caminho_origem, pasta_saida):
            imagens_processadas += 1
            
            # Conta quantas questões foram geradas
            if os.path.exists(pasta_saida):
                questoes = [f for f in os.listdir(pasta_saida) if f.startswith('questao_')]
                questoes_totais += len(questoes)
    
    print(f"\n{'='*60}")
    print(f"✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"📊 Resumo:")
    print(f"   - Imagens processadas: {imagens_processadas}/{len(imagens)}")
    print(f"   - Total de questões extraídas: {questoes_totais}")
    print(f"   - Pasta de saída: {pasta_destino}/")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Processa todas as imagens da pasta "inteiras"
    processar_todas_imagens()
    
    print("\n" + "="*60)
    print("🏁 PROGRAMA FINALIZADO!")
    print("="*60)