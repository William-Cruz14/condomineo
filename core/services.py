from decouple import config
from huggingface_hub import InferenceClient
import re

print("Configurando cliente de inferência da Hugging Face...")
try:
    # Carrega o token a partir da variável de ambiente ou arquivo .env
    huggingface_token = config('HUGGINGFACE_TOKEN', default=None)
    if not huggingface_token:
        raise ValueError("A variável de ambiente HUGGINGFACE_TOKEN não foi configurada.")

    # Passa o token explicitamente para o cliente
    inference_client = InferenceClient(
        provider="novita",
        token=huggingface_token
    )

    # Define o modelo que será usado para a sumarização
    MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"
    print("Cliente de inferência configurado com sucesso.")

except Exception as e:
    print(f"Erro ao configurar o cliente de inferência: {e}")
    inference_client = None


def reformat_text(text: str) -> str | None:
    """
    Remove formatações indesejadas do texto retornado pela API.
    Args:
        text: O texto a ser reformulado.
    Returns:
        O texto reformulado.
    """
    reformatted_text = re.sub(r"(\*)+", "", text)
    return reformatted_text

def summarize_text(text_to_summarize: str) -> str | None:
    """
    Gera um resumo de um texto usando a API de Inferência da Hugging Face.

    Args:
        text_to_summarize: O texto a ser resumido.

    Returns:
        O texto resumido, ou None se o cliente não estiver disponível ou ocorrer um erro.
    """
    if not inference_client:
        print("Cliente de inferência não está disponível.")
        return None

    try:
        prompt = (
            "Resuma o seguinte texto em português de forma detalhada. "
            "Não inclua saudações ou frases introdutórias na sua resposta, "
            "apenas o resumo em si.\n\n"
            f"Texto:\n{text_to_summarize}"
        )
        # Chama a API de sumarização, passando os parâmetros diretamente
        summary_list = inference_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL_ID,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            n=1
        )
        # A API pode retornar uma lista, então pegamos o primeiro item.
        # O objeto retornado tem um atributo 'summary_text'.
        # Extrai o conteúdo da resposta do Llama
        md_summary = summary_list.choices[0].message.content
        return reformat_text(md_summary)

    except Exception as e:
        print(f"Erro ao gerar o resumo via API: {e}")
        return None


if __name__ == '__main__':
    # Este bloco só será executado se o arquivo services rodar o arquivo diretamente
    TEXTO_EXEMPLO = """
    A inteligência artificial (IA) é um campo da ciência da computação que se dedica
    ao desenvolvimento de sistemas capazes de realizar tarefas que normalmente exigiriam
    inteligência humana. Isso inclui aprendizado, raciocínio, resolução de problemas,
    percepção e uso da linguagem. As aplicações de IA são vastas, abrangendo desde
    assistentes virtuais e carros autônomos até diagnósticos médicos e análise de mercado financeiro.
    O desenvolvimento da IA tem sido impulsionado por avanços em poder computacional e pela
    disponibilidade de grandes volumes de dados (Big Data).
    """

    print("\n--- Resumindo texto de exemplo ---")
    resumo = summarize_text(TEXTO_EXEMPLO)

    if resumo:
        print("\nTexto Original:")
        print(TEXTO_EXEMPLO)
        print("\nResumo Gerado:")
        print(resumo)
