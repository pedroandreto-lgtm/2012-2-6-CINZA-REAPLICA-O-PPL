"""
Propósito: Dividir as imagens de páginas inteiras em questões individuais
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS: 
- As imagens estão na pasta "inteiras"
- Padrão: 7px rgb(35,31,32), 4px rgb(255,255,255), 2px rgb(35,31,32)
- Procura o padrão em várias posições x
- Corta 30px acima do padrão encontrado
- Salva na pasta "inteiras-questoes"
"""

from PIL import Image
import os

def encontrar_padrao_faixa(imagem, tolerancia=10):
    """
    Encontra posições onde há uma faixa horizontal com o padrão:
    7px rgb(35,31,32), 4px rgb(255,255,255), 2px rgb(35,31,32)
    Procura em várias posições x para encontrar onde está o padrão
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Padrão correto
    cor_escura = (35, 31, 32)
    cor_branca = (255, 255, 255)
    
    # Testar em várias posições x (da esquerda para a direita)
    posicoes_x = list(range(50, min(largura - 50, 800), 50))
    
    print(f"Procurando padrão em {len(posicoes_x)} posições diferentes...")
    print(f"Posições x testadas: {posicoes_x}")
    print(f"Dimensões da imagem: {largura}x{altura}")
    print("=" * 60)
    
    padroes_por_x = {}
    melhor_x = None
    mais_faixas = 0
    
    for x_verificacao in posicoes_x:
        encontrados_nesse_x = 0
        y = 0
        
        while y < altura - 20:
            # Pega o pixel na posição x_verificacao
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
                    
                    if qtd_escura2 < 0 or qtd_escura2 > 4:
                        padrao_valido = False
                
                if padrao_valido:
                    posicao_corte = max(0, y - 40)
                    
                    # Verifica se já não temos essa posição (evita duplicatas)
                    if not posicoes_corte or abs(posicao_corte - posicoes_corte[-1]) > 20:
                        posicoes_corte.append(posicao_corte)
                        encontrados_nesse_x += 1
                        print(f"  ✅ x={x_verificacao}: Padrão em y={y}, cortando em y={posicao_corte}")
                        print(f"     -> escura1: {qtd_escura1}px, branca: {qtd_branca}px, escura2: {qtd_escura2}px")
                    
                    y = posicao_atual + 10
                    continue
            
            y += 1
        
        if encontrados_nesse_x > 0:
            padroes_por_x[x_verificacao] = encontrados_nesse_x
            if encontrados_nesse_x > mais_faixas:
                mais_faixas = encontrados_nesse_x
                melhor_x = x_verificacao
    
    # Mostra o resumo
    print("=" * 60)
    if padroes_por_x:
        print(f"✅ Padrão encontrado nas posições x: {list(padroes_por_x.keys())}")
        print(f"🎯 Melhor posição: x={melhor_x} com {mais_faixas} faixas encontradas")
        print(f"📊 Total de faixas encontradas: {len(posicoes_corte)}")
    else:
        print("❌ Padrão NÃO encontrado em nenhuma posição x testada!")
        print("\n🔍 Sugestões:")
        print("  1. Verifique se as cores RGB(35,31,32) e RGB(255,255,255) estão corretas")
        print("  2. Aumente a tolerância (atualmente 10)")
        print("  3. Verifique se o padrão está realmente na imagem")
        print("  4. Tente posições x diferentes (modifique a lista posicoes_x)")
    
    return posicoes_corte, melhor_x

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
    posicoes_corte, x_encontrado = encontrar_padrao_faixa(imagem)
    
    if not posicoes_corte:
        print("\n❌ NENHUMA FAIXA ENCONTRADA!")
        print("O padrão RGB(35,31,32) e RGB(255,255,255) não foi encontrado.")
        return False
    
    print(f"\n✅ Encontradas {len(posicoes_corte)} faixas para corte em x={x_encontrado}")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    print(f"📁 Pasta de saída: {pasta_saida}")
    
    # Corta as seções da imagem
    posicao_anterior = 0
    questoes_cortadas = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_questao = f"questao_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_questao)
        secao.save(caminho_completo)
        questoes_cortadas += 1
        print(f"💾 Salvo: {nome_questao} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte + 30
    
    # Corta a seção final
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
    
    if not os.path.exists(pasta_origem):
        print(f"❌ ERRO: Pasta '{pasta_origem}' não encontrada!")
        return
    
    os.makedirs(pasta_destino, exist_ok=True)
    
    imagens = [f for f in os.listdir(pasta_origem) if f.lower().endswith('.png')]
    
    if not imagens:
        print(f"❌ Nenhuma imagem PNG encontrada na pasta '{pasta_origem}'")
        return
    
    print("="*60)
    print("🎯 DIVISOR DE QUESTÕES - IMAGENS INTEIRAS")
    print(f"📁 Pasta origem: {pasta_origem}")
    print(f"📁 Pasta destino: {pasta_destino}")
    print(f"🔍 Padrão: 7px RGB(35,31,32) + 4px RGB(255,255,255) + 2px RGB(35,31,32)")
    print(f"🔍 Procurando padrão em várias posições x")
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
    processar_todas_imagens()
    
    print("\n" + "="*60)
    print("🏁 PROGRAMA FINALIZADO!")
    print("="*60)