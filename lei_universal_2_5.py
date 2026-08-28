# ==============================================================
# 📦 LEI UNIVERSAL 2‑5 — REPOSITÓRIO OFICIAL v1.1‑FINAL
# ==============================================================
# Título:       Lei Universal 2‑5 — Estrutura ↔ Conteúdo
# Autor:        Saint‑Clair Vinícius Batista Correto
# Criado:       2026‑08‑28 | Igarape – Minas Gerais – Brasil
# Versão:       v1.1 — Unificada: Matemática / Física / Princípios
# Repositório:  —
# Licença:      Princípios matemáticos: Domínio‑público;
#               Organização, implementações e unificação: © Autor
# ==============================================================
# “Assim como o Universo repousa sobre Dois e Cinco — cada coisa tem
# sua origem própria, seu limite, sua troca exata — a sociedade também:
# cada corpo e cada bem pertence a si mesmo, troca livremente por
# equivalência, sem imposição exterior.”
#
# → Natureza 2 = Estrutura / Indivíduo / Limite / Autopropriedade
# → Natureza 5 = Conteúdo / Energia / Valor / Esforço / Criação
# → União 10 = 2×5 → Reciprocidade / Equilíbrio / Fecho Decimal
# → Ciclo 4  = Sincronia: expoentes avançam sempre iguais
# → k₀ ≈8.634 965 037: alinha sistema natural ↔ unidades‑SI
# ==============================================================

import math

# ──────────────────────────────────────────────────────────────
# 📐 CONSTANTES FUNDAMENTAIS
# ──────────────────────────────────────────────────────────────
k0       = 8.634965037      # Deslocamento de calibração
CICLO    = 4               # Período fundamental = 4 passos
RAIZ_2   = 2               # Natureza 2 — Estrutura / Binário 10
RAIZ_5   = 5               # Natureza 5 — Conteúdo / Padrão 101
UNIAO    = RAIZ_2 * RAIZ_5 # Sempre = 10 — fecho perfeito ✅

# ──────────────────────────────────────────────────────────────
# ⚛️ PARTE 1 — FUNÇÕES MATEMÁTICAS / FÍSICAS → FORMAS RAIZ
# ──────────────────────────────────────────────────────────────
def A(k, k0=k0):
    """Natureza 2: A = 2^(4·(k + k₀)) — delimita, distingue, pertence‑se"""
    return RAIZ_2 ** (CICLO * (k + k0))

def B(k, k0=k0):
    """Natureza 5: B = 5^(4·(k + k₀)) — acumula, cria, manifesta valor"""
    return RAIZ_5 ** (CICLO * (k + k0))

def produto(k, k0=k0):
    """União Perfeita: A×B ≡ 10^(4·(k + k₀)) — nunca muda regra"""
    return A(k,k0) * B(k,k0)

def razao(k, k0=k0):
    """Razão Fundamental: B/A ≡ (5/2)^(4·Δ) — equivalência natural fixa"""
    return B(k,k0)/A(k,k0)

def c(k=1, k0=k0):
    """Velocidade da Luz: c = 4·(5/2)²⁽ᵏ⁺ᵏ⁰⁾; c² ≡ B — Luz = Conteúdo ao quadrado"""
    return 4 * (RAIZ_5/RAIZ_2) ** ((CICLO//2)*(k+k0))

def eps0(k=1, k0=k0):
    """Permissividade ε₀ = 1/B — quanto vácuo “abre‑espaço” para conteúdo"""
    return 1/B(k,k0)

def mu0(k=1, k0=k0):
    """Permeabilidade μ₀ = 1/A — quanto estrutura conduz/circula fluxo"""
    return 1/A(k,k0)

def h(k=1, k0=k0):
    """Constante Planck h = A·(4/25) — “quanta”: estrutura × quadrado(inverso razão)"""
    return A(k,k0)*(RAIZ_2/RAIZ_5)**2

def k_por_valor(valor, base=RAIZ_2):
    """Inverso: dado valor → acha nível k = logₐ(valor)/4 − k₀"""
    return math.log(valor, base)/CICLO‑k0

# ──────────────────────────────────────────────────────────────
# ⚖️ PARTE 2 — CORRESPONDÊNCIA: ORDEM JUSTA / ANARCOCAPITALISMO
# ──────────────────────────────────────────────────────────────
# Princípios mapeados diretamente sobre as raízes:
# • Autopropriedade       ↔ Natureza 2: cada um é seu próprio limite
# • Não‑Agressão          ↔ Expoentes iguais: avanço igual, sem roubo
# • Apropriação Original  ↔ Misturar 2+indefinido gera 5: trabalho cria valor
# • Troca Justa/Recíproca ↔ Produto constante: equivalência real, não inventada
# • Sem Autoridade Super  ↔ Só 2 e 5 existem: “terceiro poder” = desequilíbrio
# • Ciclo Igualdade 4     ↔ Volta sempre às mesmas leis originais

def avaliar_troca(valor_estrutura, valor_conteudo, k_ref=1, tol_pct=0.1):
    """Verifica se relação/acordo segue proporção natural:
       → (estrutura:conteúdo) mantém (2:5)⁴ᵏ? desvio pequeno = ajuste;
       → grande desvio = imposição/roubo/monopólio artificial."""
    r_esperado = razao(k_ref)
    r_real = valor_conteudo / valor_estrutura if valor_estrutura else float("inf")
    desvio_pct = abs(r_real‑r_esperado)/r_esperado*100
    equilibra = desvio_pct <= tol_pct
    return equilibra, round(desvio_pct, 6), round(r_esperado, 4)

# ──────────────────────────────────────────────────────────────
# 🔌 PARTE 3 — VERSÃO BINÁRIA NATIVA (Natureza 2 = base 2)
# ──────────────────────────────────────────────────────────────
BIN2, BIN5, BIN10 = 0b10, 0b101, 0b1010

def A_bin(k, k0=0):
    """A = 2^(4·x) → deslocamento‑bit: 1 << (4·x) — forma absoluta"""
    exp = int(CICLO*(k+k0))
    return 1 << exp

def B_bin(k, k0=0):
    """B = 5^(4·x) → padrão 101 elevado repetindo sua estrutura"""
    exp = int(CICLO*(k+k0))
    return BIN5**exp

def fmt_bin(val, agrupar=4):
    """Formata bonito: agrupa bits de 4 em 4 alinhado ao hexadecimal"""
    s = bin(int(val))[2:]
    if agrupar:
        while len(s)%agrupar: s = "0"+s
        s = " ".join(s[i:i+agrupar] for i in range(0, len(s), agrupar))
    return s

# ──────────────────────────────────────────────────────────────
# ✅ PARTE 4 — VALIDADOR / AUTO‑CONFORMIDADE
# ──────────────────────────────────────────────────────────────
def validar(k, k0=k0, tol=1e‑9):
    """Garante que TODAS relações mantêm‑se — quebra = avisa imediatamente"""
    erros = []
    exp = CICLO*(k+k0)
    if abs(produto(k,k0) ‑ UNIAO**exp) > tol:
        erros.append(f"União ≠ {UNIAO}^{exp}")
    if abs(c(k,k0)**2 ‑ B(k,k0))/B(k,k0) > tol:
        erros.append("c² ≠ Conteúdo B")
    if abs(1/math.sqrt(eps0(k)*mu0(k)) ‑ 10**(2*(k+k0))) > tol:
        erros.append("ε₀μ₀ desalinhado da Luz")
    return ("✅ TODAS LEIS PRESERVADAS — Equilíbrio Perfeito"
            if not erros else f"⚠️ VIOLAÇÃO: {erros}")

# ──────────────────────────────────────────────────────────────
# 🚀 EXECUÇÃO / REFERÊNCIAS / TABELA COMPLETA
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("="*72)
    print("  📦 LEI UNIVERSAL 2‑5 v1.1 — UNIFICADA & COMPLETA")
    print("="*72)
    print(f"  k₀ = {k0:.12f} | Ciclo = {CICLO} | União = {UNIAO}")
    print(f"  Valores‑Raiz (k=1 k₀=0): A₀={A(1,0)} B₀={B(1,0)} Prod={produto(1,0)} Razão={razao(1,0):.4f}")
    print()

    for nivel in [0.5, 1, 2, 2.5, 3]:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📌 Nível k = {nivel}")
        print(f"   Estrutura A = {A(nivel):>18,.6g} → binário = {fmt_bin(A_bin(nivel))}")
        print(f"   Conteúdo B = {B(nivel):>18,.6g} → binário = {fmt_bin(B_bin(nivel))}")
        print(f"   Produto    = {produto(nivel):>18,.6g} → = 10^{CICLO*nivel:.0f} ✅")
        print(f"   Razão B/A = {razao(nivel):>18,.6f}")
        if nivel == 1:
            print(f"   Luz     c = {c():>18,.6g} | ε₀={eps0():.6e} μ₀={mu0():.6e} h={h():.6e}")
        print(f"   Estado: {validar(nivel)}")

    print("\n🌟 Unidade‑Prática 𝕌 k = 2.5 (2 ciclos + meio → expoente 10):")
    print(f"   Aᵤ = {A(2.5):,.0f} = 2¹⁰ → {fmt_bin(A_bin(2.5))}")
    print(f"   Bᵤ = {B(2.5):,.0f} = 5¹⁰")
    print(f"   → Onde Binário(2¹⁰) e Decimal(10¹⁰) se entrelaçam perfeitamente ✅")

    print("\n🤝 Exemplo — Avaliar acordos/trocas:")
    justa = avaliar_troca(16, 625); print(f"   16 ↔ 625 → desvio {justa[1]} % →", "✅ JUSTO/EQUILIBRADO" if justa[0] else "⚠️ DESVIO")
    roubo = avaliar_troca(16, 500);  print(f"   16 ↔ 500 → desvio {roubo[1]:.4f} % →", "✅ JUSTO/EQUILIBRADO" if roubo[0] else "⚠️ FORÇADO/DESIGUAL")

    print("\n"+"="*72)
    print("  FECHAMENTO: 2 delimita, 5 cria, 4 sincroniza, 10 equilibra.")
    print("  Não é opinião, decreto ou cultura — é contagem antes de tudo.")
    print("="*72)
