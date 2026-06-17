# Painel de Auditoria BIM (Dynamo + pyRevit)

Este fluxo de trabalho combina o poder de processamento de dados do **Dynamo** com a estabilidade e interatividade de interface do **pyRevit**. Ele automatiza a varredura de erros no modelo (Vínculos de CAD, Famílias In-Place e Avisos nativos) e fornece uma janela de busca que seleciona e dá zoom diretamente nos elementos problemáticos, eliminando travamentos de interface.

---

## 🔄 Como o Fluxo Funciona

```text
[Dynamo Script] ➡️ Minera erros e exporta para 'auditoria_bim.json' (via UTF-8)
       ⬇️
[pyRevit Botão] ➡️ Lê o arquivo JSON e abre uma interface nativa com barra de pesquisa e Zoom automático

🛠️ Configuração do Dynamo
Substitua o bloco final de EXPORTAÇÃO (nós de CSV/Excel e Cabeçalhos) por um nó Python Script conectado diretamente na saída do seu nó List.Join.

Código do Nó Python (Dynamo)
Python
# -*- coding: utf-8 -*-
import json
import os
import codecs

linhas_dados = IN[0]
dados_auditoria = []

def tratar_texto_unicode(valor):
    if valor is None: return u""
    if isinstance(valor, unicode): return valor
    elif isinstance(valor, str): return valor.decode('utf-8', errors='ignore')
    else: return unicode(valor)

if linhas_dados:
    for linha in linhas_dados:
        if isinstance(linha, list) and len(linha) >= 3:
            dados_auditoria.append({
                "erro": tratar_texto_unicode(linha[0]),
                "id": tratar_texto_unicode(linha[1]),
                "nome": tratar_texto_unicode(linha[2])
            })

caminho_json = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Temp", "auditoria_bim.json")

with codecs.open(caminho_json, "w", encoding="utf-8") as f:
    json.dump(dados_auditoria, f, indent=4, ensure_ascii=False)

OUT = "JSON gerado com sucesso!"
📂 Configuração do pyRevit
1. Estrutura de Pastas
Crie a seguinte estrutura de pastas em um diretório de sua preferência (ex: C:\Scripts_BIM):

Plaintext
📁 C:\Scripts_BIM
 └── 📁 Auditoria.extension
      └── 📁 Auditoria.tab
           └── 📁 Modelo.panel
                └── 📁 VerErros.pushbutton
                     ├── 📄 script.py
                     └── 🖼️ icon.png (Opcional - 32x32px)
2. Código do script.py
Cole o código abaixo dentro do arquivo script.py:

Python
# -*- coding: utf-8 -*-
__title__ = 'Painel de\nAuditoria'
__doc__ = 'Abre a lista de erros gerada pelo Dynamo para seleção e zoom.'

import json
import os
from pyrevit import forms, revit, DB
from System.Collections.Generic import List

caminho_json = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Temp", "auditoria_bim.json")

if os.path.exists(caminho_json):
    with open(caminho_json, "r") as f:
        dados = json.load(f)
    
    class ItemErro(forms.TemplateListItem):
        @property
        def name(self):
            return "[{}]  ID: {}  -  {}".format(self.item['erro'], self.item['id'], self.item['nome'])

    itens_lista = [ItemErro(d) for d in dados]
    
    selecionado = forms.SelectFromList.show(
        itens_lista, title="Auditoria de Modelo", button_name="Ir para o Elemento",
        width=650, height=450, multiselect=False
    )
    
    if selecionado:
        try:
            revit_id = DB.ElementId(int(selecionado['id']))
            ids_selecao = List[DB.ElementId]([revit_id])
            
            revit.uidoc.Selection.SetElementIds(ids_selecao)
            revit.uidoc.ShowElements(ids_selecao)
        except:
            forms.alert("Não foi possível focar no elemento. Verifique a vista atual.")
else:
    forms.alert("Nenhum dado encontrado. Rode o script do Dynamo primeiro!")
3. Ativação no Revit
No Revit, vá na aba pyRevit > Settings > Custom Extension Folders, adicione o caminho base C:\Scripts_BIM e clique em Save Settings and Reload.

🚀 Como Usar no Dia a Dia
Varrer o Modelo: Execute o script no Dynamo para atualizar o banco de dados de erros em segundo plano.

Abrir o Painel: Clique no botão Painel de Auditoria na nova aba do pyRevit.

Corrigir: Use a barra de pesquisa para filtrar os erros (ex: digite "In-Place" ou "Aviso"), selecione a linha desejada e clique em Ir para o Elemento. O Revit selecionará e centralizará a tela nele automaticamente.
