# 🎨 Paleta de Cores - X-Men AgileTeam

## Cores Primárias

### 🔥 Laranja Principal
- **Cor**: `#FF7C2E` (255, 124, 46)
- **Uso**: Botões principais, destaque, CTA, ícones importantes
- **CSS Variable**: `--primary-color`

### 🟠 Laranja Secundário
- **Cor**: `#FF9500` (255, 149, 0)
- **Uso**: Hover states, gradientes, elementos secundários
- **CSS Variable**: `--secondary-color`

## Cores de Background

### 🌚 Background Principal
- **Cor**: `#0A0A0A` (10, 10, 10)
- **Uso**: Fundo principal da aplicação
- **CSS Variable**: `--background-color`

### 🃏 Background Cards
- **Cor**: `#1A1A1A` (26, 26, 26)
- **Uso**: Cards, modais, seções destacadas
- **CSS Variable**: `--card-background`

## Cores de Texto

### ✨ Texto Primário
- **Cor**: `#FFFFFF` (255, 255, 255)
- **Uso**: Títulos, texto principal
- **CSS Variable**: `--text-primary`

### 🌫️ Texto Secundário
- **Cor**: `#B3B3B3` (179, 179, 179)
- **Uso**: Subtítulos, descrições, labels
- **CSS Variable**: `--text-secondary`

### 💭 Texto Inativo
- **Cor**: `#666666` (102, 102, 102)
- **Uso**: Texto desabilitado, placeholders
- **CSS Variable**: `--text-inactive`

## Cores de Interface

### 🔲 Bordas
- **Cor**: `#333333` (51, 51, 51)
- **Uso**: Bordas de elementos, separadores
- **CSS Variable**: `--border-color`

### 🎯 Hover
- **Cor**: `#2A2A2A` (42, 42, 42)
- **Uso**: Estados de hover em elementos
- **CSS Variable**: `--hover-color`

## Cores de Status

### ✅ Sucesso
- **Cor**: `#22C55E` (34, 197, 94)
- **Uso**: Mensagens de sucesso, status positivo
- **CSS Variable**: `--success-color`

### ❌ Erro
- **Cor**: `#EF4444` (239, 68, 68)
- **Uso**: Mensagens de erro, status negativo
- **CSS Variable**: `--error-color`

### ⚠️ Atenção
- **Cor**: `#F59E0B` (245, 158, 11)
- **Uso**: Avisos, alertas
- **CSS Variable**: `--warning-color`

### ℹ️ Informação
- **Cor**: `#3B82F6` (59, 130, 246)
- **Uso**: Informações, dicas
- **CSS Variable**: `--info-color`

## Gradientes

### 🌟 Gradiente Principal
- **Cores**: `linear-gradient(135deg, #FF7C2E, #FF9500)`
- **Uso**: Botões premium, elementos de destaque

### 🌈 Gradiente de Cards
- **Cores**: `linear-gradient(135deg, #1A1A1A 0%, rgba(255,255,255,0.05) 100%)`
- **Uso**: Background de cards com sutileza

### 💫 Gradiente de Membros
- **Cores**: `linear-gradient(135deg, #FF7C2E, #FF9500)`
- **Uso**: Avatares de membros

## Aplicação das Cores

### CSS Root Variables
```css
:root {
    --primary-color: #FF7C2E;
    --secondary-color: #FF9500;
    --background-color: #0A0A0A;
    --card-background: #1A1A1A;
    --text-primary: #FFFFFF;
    --text-secondary: #B3B3B3;
    --text-inactive: #666666;
    --border-color: #333333;
    --hover-color: #2A2A2A;
    --success-color: #22C55E;
    --error-color: #EF4444;
    --warning-color: #F59E0B;
    --info-color: #3B82F6;
}
```

### Acessibilidade
- **Contraste mínimo**: 4.5:1 para texto normal
- **Contraste mínimo**: 3:1 para texto grande
- **Cores funcionais**: Nunca usar apenas cor para transmitir informação

### Uso Responsivo
- **Mobile**: Cores mais saturadas para melhor visibilidade
- **Desktop**: Gradientes sutis e efeitos de hover
- **Dark Mode**: Sistema nativo em tema escuro

## Inspiração

A paleta foi inspirada no **uniforme laranja dos X-Men**, transmitindo:
- 🔥 **Energia e dinamismo**
- 💪 **Força e determinação**
- 🚀 **Inovação e modernidade**
- 🤝 **Colaboração e trabalho em equipe**