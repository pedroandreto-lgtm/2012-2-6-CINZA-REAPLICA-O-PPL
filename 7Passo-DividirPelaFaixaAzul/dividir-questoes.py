"""
Propósito: Dividir as questões por padrão. Observa-se que ao início de cada questão tem uma faixa de alguma cor, que é o padrão de início de cada questão
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026
"""

from PIL import Image
import os

def encontrar_padrao_questao(imagem):
    """
    Encontra padrões que indicam o início de uma questão:
    1. Linha com "---" (traços)
    2. Texto "# QUESTÃO" ou "# QUESTION"
    3. Padrão de cores específico
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    print("Procurando padrões de separação...")
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura:
        encontrou = False
        
        # --- MODO 1: Procurar linha com "---" (traços) ---
        # Verifica se tem muitos pixels escuros na linha (mais de 70% da linha)
        pixels_escuros = 0
        for x in range(largura):
            pixel = pixels[x, y]
            if len(pixel) == 4:
                r, g, b, a = pixel
            else:
                r, g, b = pixel[:3]
            
            # Se for escuro (menos de 100)
            if r < 100 and g < 100 and b < 100:
                pixels_escuros += 1
        
        # Se mais de 70% da linha for escura, é uma linha de separação
        if pixels_escuros > largura * 0.7:
            posicao_corte = y - 1
            if posicao_corte < 0:
                posicao_corte = 0
            
            if not posicoes_corte or posicao_corte != posicoes_corte[-1]:
                posicoes_corte.append(posicao_corte)
                print(f"Linha escura encontrada em y={y}, cortando em y={posicao_corte}")
                encontrou = True
                y += 5  # Pula a linha
                continue
        
        # --- MODO 2: Procurar por "# QUESTÃO" ou "# QUESTION" ---
        # Verifica se a linha tem texto escuro no meio
        if not encontrou:
            pixel_meio = largura // 2
            pixel = pixels[pixel_meio, y]
            
            if len(pixel) == 4:
                r, g, b, a = pixel
            else:
                r, g, b = pixel[:3]
            
            # Se for escuro (texto)
            if r < 80 and g < 80 and b < 80:
                # Verifica os pixels ao redor para ver se forma um texto
                # Vamos verificar se há um padrão de texto (pixels escuros e claros alternando)
                tem_texto = False
                contagem_escuros = 0
                for x in range(largura//2 - 50, largura//2 + 50):
                    pixel = pixels[x, y]
                    if len(pixel) == 4:
                        r2, g2, b2, a = pixel
                    else:
                        r2, g2, b2 = pixel[:3]
                    
                    if r2 < 80 and g2 < 80 and b2 < 80:
                        contagem_escuros += 1
                
                # Se tem muitos pixels escuros consecutivos, é texto
                if contagem_escuros > 20:
                    # Verifica se tem "QUESTION" ou "QUESTÃO" nas proximidades
                    # Como não temos OCR, vamos usar uma heurística
                    posicao_corte = y - 1
                    if posicao_corte < 0:
                        posicao_corte = 0
                    
                    if not posicoes_corte or posicao_corte != posicoes_corte[-1]:
                        posicoes_corte.append(posicao_corte)
                        print(f"Possível texto de questão encontrado em y={y}, cortando em y={posicao_corte}")
                        encontrou = True
                        y += 20  # Pula o texto
                        continue
        
        y += 1
        
        # Mostra progresso a cada 5000 linhas
        if y % 5000 == 0:
            print(f"Progresso: {y*100//altura}%")
    
    # Remove duplicatas e ordena
    posicoes_corte = sorted(list(set(posicoes_corte)))
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES das linhas de separação
    """
    # Abre a imagem
    print("Abrindo imagem...")
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições das linhas de separação
    posicoes_corte = encontrar_padrao_questao(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão de separação encontrado na imagem!")
        print("Tentando método alternativo: procurar por linhas com muitos pixels escuros...")
        
        # Método alternativo: procura qualquer linha com muitos pixels escuros
        pixels = imagem.load()
        for y in range(altura):
            pixels_escuros = 0
            for x in range(largura):
                pixel = pixels[x, y]
                if len(pixel) == 4:
                    r, g, b, a = pixel
                else:
                    r, g, b = pixel[:3]
                
                if r < 100 and g < 100 and b < 100:
                    pixels_escuros += 1
            
            if pixels_escuros > largura * 0.6:
                posicao_corte = y - 1
                if posicao_corte < 0:
                    posicao_corte = 0
                
                if not posicoes_corte or posicao_corte != posicoes_corte[-1]:
                    posicoes_corte.append(posicao_corte)
                    print(f"Linha escura encontrada em y={y}")
        
        if not posicoes_corte:
            print("❌ Nenhuma separação encontrada!")
            return
    
    print(f"\n✅ Encontradas {len(posicoes_corte)} separações")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Adiciona o topo e o final da imagem
    posicoes_corte_completas = [0] + posicoes_corte + [altura]
    
    # Corta as seções da imagem
    for i in range(len(posicoes_corte_completas) - 1):
        inicio = posicoes_corte_completas[i]
        fim = posicoes_corte_completas[i + 1]
        
        # Pula seções vazias ou muito pequenas
        if fim - inicio < 50:
            continue
        
        # Corta a seção
        area_corte = (0, inicio, largura, fim)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"questao_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    # ESCOLHA QUAL IMAGEM PROCESSAR
    
    # Opção 1: Colunas concatenadas
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"

    # Opção 2: Página inteira
    #caminho_imagem = "./inteiras/pagina_enem_15.png"
    #pasta_saida = "pagina_15"
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("\n✅ Divisão concluída!")