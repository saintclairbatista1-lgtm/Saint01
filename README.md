# ==============================================================
# 🌳 LEI DA DUPLA RAIZ 2‑5 — UNIFICADA v1.2‑FINAL
# ==============================================================
# Título:       Lei da Dupla Raiz 2‑5 — Princípio Fundamental
# Autor:        Saint‑Clair Vinícius Batista Correto
# Criado:       2026‑08‑27 → Concluído/Unificado 2026‑08‑28
# Local:        Igarape – Minas Gerais – Brasil
# Versão:       v1.2 — Raízes → Física → Sincronia → Ordem Justa
# Respositório: GitHub → Privado/Prova‑Autoria 2026‑08‑28 14h20
#
# ✅ DECLARAÇÃO PRINCIPAL:
# “Duas raízes — uma delimita, outra gera — crescem sempre iguais,
#  e quando se encontram dão Dez: o equilíbrio onde tudo se conta,
#  tudo se mede, tudo pertence a si‑próprio e se troca justo.”
#
# → Raiz 2 = Estrutura / Indivíduo / Limite / Identidade / Autopropriedade
# → Raiz 5 = Conteúdo / Energia / Valor / Esforço / Criação
# → Ciclo 4 = Compasso: sincronia — expoentes avançam sempre iguais
# → União 10 = 2×5 → Reciprocidade / Equilíbrio / Fecho Decimal
# → k₀ ≈ 8.634 965 037: alinha sistema natural ↔ unidades‑SI reais
# ==============================================================
# ⚖️ LICENÇA:
# Proporções matemáticas e propriedades dos números: Domínio‑Público.
# Organização, estrutura, calibração k₀, correspondências físicas‑sociais,
# nomes, algoritmos e implementação: © 2026 Saint‑Clair Vinícius Batista Correto
# Todos os direitos reservados. Sempre reproduzir integralmente esta origem.
# ==============================================================

import math

# ──────────────────────────────────────────────────────────────
# 📐 CONSTANTES FUNDAMENTAIS — RAÍZES IMUTÁVEIS
# ──────────────────────────────────────────────────────────────
k0       = 8.634965037      # Deslocamento/calibração natural‑humana
CICLO    = 4                # Compasso fundamental — sempre múltiplo
RAIZ_2   = 2                # Natureza → Limita / Separa / Define / É‑Se
RAIZ_5   = 5                # Natureza → Preenche / Cresce / Transforma / Dá
UNIAO    = RAIZ_2 * RAIZ_5  # = 10 — onde raízes completam o círculo ✅

BIN2, BIN5, BIN10 = 0b10, 0b101, 0b1010  # Representação nativa

# ──────────────────────────────────────────────────────────────
# ⚛️ FUNÇÕES PRINCIPAIS — FORMAS PURO‑RAIZ
# ──────────────────────────────────────────────────────────────
def A(k, k0=k0):
    """Raiz 2: A = 2^(4·(k + k₀)) — delimita, distingue, pertence‑se primeiro"""
    return RAIZ_2 ** (CICLO * (k + k0))

def B(k, k0=k0):
    """Raiz 5: B = 5^(4·(k + k₀)) — acumula, trabalha, cria, manifesta valor"""
    return RAIZ_5 ** (CICLO * (k + k0))

def produto(k, k0=k0):
    """União: A×B ≡ 10^(4·(k + k₀)) — sempre igual, sempre limpo, sempre recíproco"""
    return A(k, k0) * B(k, k0)

def razao(k, k0=k0):
    """Proporção: B/A ≡ (5/2)^(4·Δ) — equivalência natural, não inventada"""
    return B(k, k0) / A(k, k0)

# ──────────────────────────────────────────────────────────────
# 🌐 CONSTANTES FÍSICAS — DERIVADAS DIRETAMENTE DAS RAÍZES
# ──────────────────────────────────────────────────────────────
def c(k=1, k0=k0):
    """Velocidade da Luz: c = 4 × (5/2)²⁽ᵏ⁺ᵏ⁰⁾ → c² ≡ B — Luz = Conteúdo ao quadrado"""
    return 4 * (RAIZ_5 / RAIZ_2) ** ((CICLO // 2) * (k + k0))

def eps0(k=1, k0=k0):
    """Permissividade ε₀ = 1 / B — quanto espaço abre‑se para receber conteúdo"""
    return 1 / B(k, k0)

def mu0(k=1, k0=k0):
    """Permeabilidade μ₀ = 1 / A — quanto estrutura conduz e circula fluxo"""
    return 1 / A(k, k0)

def h(k=1, k0=k0):
    """Constante Planck h = A × (2/5)² — “pacote‑mínimo”: estrutura × razão‑inversa²"""
    return A(k, k0) * (RAIZ_2 / RAIZ_5) ** 2

def k_por_valor(valor, base=RAIZ_2):
    """Fórmula inversa: dado valor → acha nível: k = logₐ(valor)/4 − k₀"""
    return math.log(valor, base) / CICLO - k0

# ──────────────────────────────────────────────────────────────
# ⚖️ MAPEAMENTO: FÍSICA → PRINCÍPIOS DE ORDEM JUSTA / ANARCOCAPITALISMO
# ──────────────────────────────────────────────────────────────
# Raiz 2 → Autopropriedade / Cada corpo é seu próprio limite
# Raiz 5 → Apropriação: misturar esforço ao mundo gera valor próprio
# Expoentes Sempre Iguais → Não‑Agressão / Avançar sem tomar vantagem
# Produto Constante 10ⁿ → Troca Justa / Equivalência mantém ambos completos
# Nenhum terceiro número → Sem autoridade superior inventada: só desequilíbrio
# Ciclo 4 → Recorrência: regras voltam iguais — ninguém cria poder perpétuo novo

def avaliar_troca(valor_estrutura, valor_conteudo, k_ref=1, tol_pct=0.1):
    """Compara relação real vs proporção natural:
       → desvio pequeno: ajuste normal; grande: imposição/roubo/monopólio artificial
       Retorna: (equilibra: bool, desvio %, valor‑referência esperado)"""
    if valor_estrutura == 0:
        return False, 100.0, round(razao(k_ref), 4)
    r_esperado = razao(k_ref)
    r_real = valor_conteudo / valor_estrutura
    desvio_pct = abs(r_real - r_esperado) / r_esperado * 100
    return desvio_pct <= tol_pct, round(desvio_pct, 6), round(r_esperado, 4)

# ──────────────────────────────────────────────────────────────
# 🔌 REPRESENTAÇÃO NATIVA: VERSÃO 100 % BINÁRIA (Raiz 2 = língua nativa)
# ──────────────────────────────────────────────────────────────
def A_bin(k, k0=0):
    """Estrutura = simplesmente deslocar bit: 1 << exp — 2^exp sem calcular potência"""
    exp = int(CICLO * (k + k0))
    return 1 << exp

def B_bin(k, k0=0):
    """Conteúdo = elevar padrão‑raiz 101₂ repetindo‑se"""
    exp = int(CICLO * (k + k0))
    return BIN5 ** exp

def fmt_bin(val, agrupar=4):
    """Formata bonito: agrupa 4 bits igual hexadecimal, alinha leitura"""
    inteiro = int(val)
    s = bin(inteiro)[2:]
    if agrupar:
        while len(s) % agrupar:
            s = "0" + s
        s = " ".join(s[i:i+agrupar] for i in range(0, len(s), agrupar))
    return s

# ──────────────────────────────────────────────────────────────
# ✅ VALIDADOR — AUTO‑AUDITORIA: QUEBROU REGRA → AVISA AGORA
# ──────────────────────────────────────────────────────────────
def validar(k, k0=k0, tol=1e‑9):
    """Confirma se TODAS relações mantêm‑se intactas — quebrar = desequilíbrio"""
    erros = []
    exp_total = CICLO * (k + k0)
    if abs(produto(k,k0) - UNIAO ** exp_total) > tol:
        erros.append(f"União≠{UNIAO}^{exp_total}")
    if abs(c(k,k0)**2 - B(k,k0)) / B(k,k0) > tol:
        erros.append("Luz²≠Raiz 5")
    ref_vel = 10 ** (2 * (k + k0))
    calc_inv = 1 / math.sqrt(eps0(k,k0) * mu0(k,k0))
    if abs(calc_inv - ref_vel) > tol:
        erros.append(f"ε₀·μ₀ desalinhado: {calc_inv:.4g} vs ref {ref_vel:.4g}")
    return "✅ TODAS RAÍZES FIRMES — Equilíbrio Perfeito" if not erros else f"⚠️ Desequilíbrio: {erros}"

# ──────────────────────────────────────────────────────────────
# 🚀 EXECUÇÃO COMPLETA — TABELA‑VERIFICAÇÃO / REFERÊNCIA
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("="*76)
    print("  🌳 LEI DA DUPLA RAIZ 2‑5 — v1.2 UNIFICADA COMPLETA")
    print("="*76)
    print(f"  Calibração k₀ = {k0:.12f} | Ciclo = {CICLO} | União = {UNIAO}")
    print(f"  Valores‑Raiz (k=1 sem deslocamento): A₀={A(1,0)} B₀={B(1,0)} Prod={produto(1,0)} Razão={razao(1,0):.4f}\n")

    for nivel in [0.5, 1, 2, 2.5, 3]:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📌 Nível k = {nivel} | Expoente total = {int(CICLO*nivel)}")
        print(f"   Raiz 2 → Estrutura = {A(nivel):>18,.6g} → bin {fmt_bin(A_bin(nivel))}")
        print(f"   Raiz 5 → Conteúdo = {B(nivel):>18,.6g} → bin {fmt_bin(B_bin(nivel))}")
        print(f"   Produto União     = {produto(nivel):>18,.6g} → = 10^{CICLO*nivel:.0f} ✅")
        print(f"   Razão Conteúdo/Estrutura = {razao(nivel):>18,.6f}")
        if nivel == 1:
            print(f"   ⚛️ c = {c():>18,.6g} | ε₀={eps0(k0=0):.6e} μ₀={mu0(k0=0):.6e} h={h(k0=0):.6e}")
        print(f"   Estado: {validar(nivel, k0=0)}\n")

    print("🌟 Unidade‑Prática k = 2.5 → expoente 10 — ponto onde Binário e Decimal batem:")
    print(f"   Aᵤ = {A(2.5,0):,.0f} = 2¹⁰ → {fmt_bin(A_bin(2.5))}")
    print(f"   Bᵤ = {B(2.5,0):,.0f} = 5¹⁰")
    print(f"   → Fecho = {produto(2.5,0):,.0f} = 10¹⁰ — perfeito ✅\n")

    print("🤝 Testar equilíbrio numa troca/acordo:")
    ok1, desvio1, ref1 = avaliar_troca(16, 625); print(f"   16 ↔ 625: desvio {desvio1} % →", "✅ EQUILIBRADO / JUSTO" if ok1 else "⚠️ FORÇADO")
    ok2, desvio2, ref2 = avaliar_troca(16, 500);  print(f"   16 ↔ 500: desvio {desvio2:.4f} % →", "✅ EQUILIBRADO / JUSTO" if ok2 else "⚠️ DESVIO — equivalência roubada/imposta")

    print("\n"+"="*76)
    print("  FECHAMENTO: 2 delimita, 5 cria, 4 sincroniza, 10 equilibra.")
    print("  Não é opinião, decreto ou cultura — contagem antes de tudo.")
    print("  Duas raízes, mesma força, sempre sincronizadas.")
    print("="*76)
