# 🎮 Axis – Gerenciador de Jogos PS1

O **Axis** é um gerenciador de jogos de **PlayStation 1** desenvolvido em **Python**, com foco em **simplicidade**, **rapidez** e **experiência moderna**.  
Com uma interface elegante e intuitiva, ele permite organizar, visualizar e jogar seus clássicos do PS1 com apenas alguns cliques.

---

## 🚀 Funcionalidades

- 🐍 **Desenvolvido em Python com CustomTkinter**
- 🎮 Interface dark moderna e responsiva
- 🔽 **Download de jogos** diretamente do Google Drive
- 📂 **Gerenciamento completo de ROMs**, com capas e visualização dinâmica
- 🔎 **Busca em tempo real** por nome de jogo
- 🛠️ **Configuração de controles** integrada
- ⚙️ Compatível com o emulador **DuckStation**
- 📦 **Empacotado em `.exe`** com PyInstaller (não requer instalação do Python)

---

## 🧰 Requisitos

- **Windows 10 ou superior**  
- **DuckStation** incluído automaticamente no pacote (baixado na primeira execução)  

---

## 🖥️ Como usar

1. Baixe o projeto e execute o **`build.bat`**
2. Abra a Pasta Release e Execute o launcher normalmente  
3. Na primeira inicialização, o **DuckStation** e os arquivos necessários serão configurados automaticamente  
4. O app detectará seus jogos em `/roms` ou oferecerá o download de uma lista inicial  
5. Clique em qualquer jogo da biblioteca para iniciar a jogatina 🎮  

---

## 📦 Estrutura de Pastas

```
📁 Axis/
 ┣ 📁 app/
 ┣ 📁 roms/           → Onde ficam os jogos (.chd, .bin, .iso)
 ┣ 📁 covers/         → Capas dos jogos (automáticas ou personalizadas)
 ┣ 📁 game/           → Emulador DuckStation + configurações
 ┗ 📄 Axis.exe
```

---

## 👨‍💻 Desenvolvido por

**Thiago Aciole**  
Engenheiro de Software Frontend e entusiasta de jogos retrô 🎮  
