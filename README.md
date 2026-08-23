# Rune

Rune transforma vídeos e áudios em texto no próprio Mac. Você pode colar vários
links, enviar vários arquivos e deixar a fila rodar. Nenhum arquivo é enviado
para um serviço de transcrição.

## Requisitos

- Mac com Apple Silicon (M1 ou mais recente)
- Node.js 20+ (o projeto usa a versão 24 indicada em `.nvmrc`)
- Python 3.13 gerenciado pelo `uv`
- FFmpeg

Com Homebrew e nvm instalados:

```bash
brew install uv ffmpeg
nvm install
make install
```

## Abrir o Rune

```bash
make start
```

Depois, abra [http://127.0.0.1:3000](http://127.0.0.1:3000). Encerrar o comando
para o front-end e o serviço local juntos. Itens interrompidos voltam para a
fila na próxima abertura.

## Onde os arquivos ficam

- textos e exportações: `~/Documents/Rune`
- fila e preferências locais: `~/Library/Application Support/Rune`
- mídia temporária: `~/Library/Caches/Rune`

Esses caminhos podem ser alterados com `RUNE_LIBRARY_DIR`, `RUNE_STATE_DIR` e
`RUNE_CACHE_DIR`. Nada é salvo dentro do repositório durante o uso normal.

## Qualidade e privacidade

O motor padrão é o Whisper `large-v3` otimizado para MLX. Na primeira
transcrição, o modelo gratuito é baixado uma única vez. Depois disso, a
transcrição funciona localmente. Downloads por link naturalmente precisam de
internet para obter a mídia; arquivos anexados não precisam.

O Rune preserva timestamps por palavra e marca trechos de menor confiança para
revisão. O texto pode ser editado e exportado em TXT, Markdown, SRT, VTT e JSON.

## Verificar o projeto

```bash
make check
```
