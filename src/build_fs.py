from littlefs import LittleFS
import os

SOURCE_DIR = "src"
OUTPUT_FILE = "fs.bin"

BLOCK_SIZE = 4096
BLOCK_COUNT = 512


def adicionar_arquivos(fs):
    for filename in os.listdir(SOURCE_DIR):
        filepath = os.path.join(SOURCE_DIR, filename)

        if os.path.isfile(filepath):
            with open(filepath, "rb") as source_file:
                content = source_file.read()

            with fs.open(filename, "wb") as destination_file:
                destination_file.write(content)

            print(f"  + {filename}")


def salvar_imagem(fs):
    with open(OUTPUT_FILE, "wb") as output_file:
        output_file.write(fs.context.buffer)


def main():
    fs = LittleFS(block_size=BLOCK_SIZE, block_count=BLOCK_COUNT)

    adicionar_arquivos(fs)
    salvar_imagem(fs)

    print(f"{OUTPUT_FILE} atualizado com sucesso!")


if __name__ == "__main__":
    main()
