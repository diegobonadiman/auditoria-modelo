# -*- coding: utf-8 -*-
__title__ = 'Painel de\nAuditoria' # Nome que vai aparecer no botão do Revit
__doc__ = 'Abre a lista de erros gerada pelo Dynamo e permite selecionar e dar zoom nos elementos.'

import json
import os
from pyrevit import forms
from pyrevit import revit, DB
from System.Collections.Generic import List

# Caminho do arquivo temporário que o seu Dynamo gerou
caminho_json = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Temp", "auditoria_bim.json")

if os.path.exists(caminho_json):
    with open(caminho_json, "r") as f:
        dados = json.load(f)
    
    # Classe que formata como cada linha vai aparecer na lista do pyRevit
    class ItemErro(forms.TemplateListItem):
        @property
        def name(self):
            return "[{}]  ID: {}  -  {}".format(self.item['erro'], self.item['id'], self.item['nome'])

    # Transforma os dados lidos do JSON em itens clicáveis
    itens_lista = [ItemErro(d) for d in dados]
    
    # Abre a janela interativa nativa do pyRevit com barra de pesquisa inclusa
    selecionado = forms.SelectFromList.show(
        itens_lista,
        title="Auditoria de Modelo (Dynamo + pyRevit)",
        button_name="Ir para o Elemento",
        width=650,
        height=450,
        multiselect=False
    )
    
    # Se o usuário clicou em um erro e apertou o botão
    if selecionado:
        try:
            # Converte o ID de string para ElementId
            id_inteiro = int(selecionado['id'])
            revit_id = DB.ElementId(id_inteiro)
            
            ids_selecao = List[DB.ElementId]()
            ids_selecao.Add(revit_id)
            
            # Executa a mágica: seleciona e dá o zoom/foco na tela
            revit.uidoc.Selection.SetElementIds(ids_selecao)
            revit.uidoc.ShowElements(ids_selecao)
            
        except Exception as e:
            forms.alert("Não foi possível dar foco no elemento. Verifique se ele não está oculto na vista atual.", title="Aviso")
else:
    forms.alert("Nenhum dado de auditoria encontrado.\n\nPor favor, execute o script do Dynamo primeiro!", title="Arquivo não encontrado")