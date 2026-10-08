# Dicionario de Dados: datatran_sul_tratado.csv

| Variavel | Tipo | Origem | Descricao |
|---|---|---|---|
| `id` | int64 | Original | Identificador unico do acidente (chave primaria) |
| `data_inversa` | datetime64[us] | Original | Data do acidente (datetime) |
| `dia_semana` | str | Original | Dia da semana por extenso (texto com acentos) |
| `horario` | str | Original | Horario do acidente no formato hh:mm:ss |
| `uf` | str | Original | Unidade da Federacao (SC, PR ou RS) |
| `br` | int64 | Original | Numero da rodovia federal |
| `km` | float64 | Original | Quilometro da rodovia |
| `municipio` | str | Original | Nome do municipio |
| `causa_acidente` | str | Original | Causa registrada pelo agente (65 categorias originais) |
| `tipo_acidente` | str | Original | Tipo do acidente (16 categorias) |
| `classificacao_acidente` | str | Original | Variavel-alvo: Sem Vitimas / Com Vitimas Feridas / Com Vitimas Fatais |
| `fase_dia` | str | Original | Fase do dia: Pleno dia, Amanhecer, Anoitecer, Plena Noite |
| `sentido_via` | str | Original | Sentido do fluxo no trecho |
| `condicao_metereologica` | str | Original | Condicao climatica (Ignorado convertido para NaN) |
| `tipo_pista` | str | Original | Tipo de pista: Simples, Dupla ou Multipla |
| `tracado_via` | str | Original | Tracado original da via (multivalorado, separado por ponto-e-virgula) |
| `uso_solo` | str | Original | Area urbana (Sim) ou rural (Nao) conforme cadastro PRF |
| `pessoas` | int64 | Original | Total de pessoas envolvidas no acidente |
| `mortos` | int64 | Original | Numero de mortos confirmados |
| `feridos_leves` | int64 | Original | Numero de feridos leves |
| `feridos_graves` | int64 | Original | Numero de feridos graves |
| `feridos` | int64 | Original | Total de feridos (= feridos_leves + feridos_graves, coluna derivada) |
| `ilesos` | int64 | Original | Numero de ilesos |
| `ignorados` | int64 | Original | Pessoas com estado nao informado |
| `veiculos` | int64 | Original | Numero de veiculos envolvidos |
| `latitude` | float64 | Original | Latitude do acidente (decimal negativo) |
| `longitude` | float64 | Original | Longitude do acidente (decimal negativo) |
| `regional` | str | Original | Superintendencia regional da PRF |
| `delegacia` | str | Original | Delegacia de policia rodoviaria responsavel |
| `uop` | str | Original | Unidade operacional da PRF |
| `mes` | int32 | Derivada | Mes do acidente (1=jan, 5=mai) derivado de data_inversa |
| `dia_semana_num` | int32 | Derivada | Dia da semana numerico (0=segunda, 6=domingo) |
| `fim_de_semana` | int64 | Derivada | 1 se sabado ou domingo, 0 caso contrario |
| `hora` | int32 | Derivada | Hora do acidente (0-23) derivada de horario |
| `faixa_horaria` | str | Derivada | Faixa de 6h: Madrugada/Manha/Tarde/Noite (D4) |
| `tracado_via_norm` | str | Derivada | tracado_via com componentes ordenados alfabeticamente |
| `tracado_aclive` | int64 | Derivada | (sem descricao) |
| `tracado_curva` | int64 | Derivada | (sem descricao) |
| `tracado_declive` | int64 | Derivada | (sem descricao) |
| `tracado_desvio_temporário` | int64 | Derivada | (sem descricao) |
| `tracado_em_obras` | int64 | Derivada | (sem descricao) |
| `tracado_intersecao_de_vias` | int64 | Derivada | (sem descricao) |
| `tracado_ponte` | int64 | Derivada | (sem descricao) |
| `tracado_reta` | int64 | Derivada | (sem descricao) |
| `tracado_retorno_regulamentado` | int64 | Derivada | (sem descricao) |
| `tracado_rotatoria` | int64 | Derivada | (sem descricao) |
| `tracado_túnel` | int64 | Derivada | (sem descricao) |
| `tracado_viaduto` | int64 | Derivada | (sem descricao) |
| `macrocausa` | str | Derivada | Macrocategoria de causa_acidente (D4, aprovada pela equipe) |
| `teve_morte` | int64 | Derivada | 1 se houve pelo menos um morto, 0 caso contrario |
| `grave_ou_fatal` | int64 | Derivada | 1 se ferido_grave > 0 ou morto > 0 (variavel-alvo sugerida para ML) |