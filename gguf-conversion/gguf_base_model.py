# type: ignore

import modal
import os

app = modal.App("convert_gguf")

unsloth_image = modal.Image.from_dockerfile("gguf-conversion/Dockerfile")

"""
Modal script for creating a base model in GGUF format.
"""


@app.function(
    gpu="T4",
    image=unsloth_image,
    timeout=60 * 60 * 24,
    secrets=[modal.Secret.from_name("hugginface-secret")],
)
def convert_base_model_gguf(
    hf_model_repo: str,
    save_model_repo: str,
    quantization_method: str,
    load_in_4bit: bool,
) -> str:
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=hf_model_repo,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=load_in_4bit,
        token=os.environ["HF_ACCESS_TOKEN"],
    )

    # else ascii generation will get messed up
    tokenizer.clean_up_tokenization_spaces = False

    model.push_to_hub_gguf(
        save_model_repo,
        tokenizer,
        quantization_method=quantization_method,
        token=os.environ["HF_ACCESS_TOKEN"],
    )
    return ""


@app.local_entrypoint()
def main():
    hf_model_repo = "meta-llama/Llama-3.2-3B" # Base model
    save_model_repo = "prasanthntu/Llama-3.2-3B-guide-GGUF" # Save model
    quantization_method = "not_quantized"
    load_in_4bit = False
    convert_base_model_gguf.remote(
        hf_model_repo=hf_model_repo,
        save_model_repo=save_model_repo,
        quantization_method=quantization_method, # No quantization
        load_in_4bit=load_in_4bit, # Do not load in 4bit, rather load it fully
    )

# run using the below command in terminal (takes ~5 mins to complete)
# modal run gguf-conversion/gguf_base_model.py
